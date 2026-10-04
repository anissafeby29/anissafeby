#!/usr/bin/env python3
"""Fetch official pages as text for research agents, cheapest method first.

Order: plain HTTP -> Crawl4AI (headless Chromium, renders JavaScript) -> Wayback Machine snapshot.
Paid tools (Firecrawl, Tavily, Parallel) are left for the agent to try only when this reports BLOCKED.

Usage:
  python3 pipeline/fetch.py URL [URL ...]            print a short report and save text to pipeline/work/fetch/
  python3 pipeline/fetch.py --out DIR URL [URL ...]  save to DIR instead
  python3 pipeline/fetch.py --print URL               print the page text

Each saved file starts with a header line: "# <url> | method=<http|crawl4ai|wayback> | status=<code>".
Wayback text is an archived copy: say so when citing it, and prefer the live page when possible.
Setup (once per machine): pip install crawl4ai
"""
import asyncio
import hashlib
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0 Safari/537.36"
BLOCK = re.compile(r"you have been blocked|access denied|attention required|just a moment|enable (javascript|cookies)|"
                   r"verify you are human|cf-chl|captcha|request unsuccessful|incapsula", re.I)
MIN_TEXT = 400  # shorter pages are usually JavaScript shells or error stubs
CDP_PORT = 9222


def html_to_text(html):
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        for t in soup(["script", "style", "noscript", "svg", "nav", "footer", "header"]):
            t.decompose()
        text = soup.get_text("\n")
    except ImportError:
        text = re.sub(r"<script.*?</script>|<style.*?</style>", " ", html, flags=re.S | re.I)
        text = re.sub(r"<[^>]+>", "\n", text)
    return re.sub(r"\n\s*\n+", "\n\n", text).strip()


def usable(text):
    return len(text) >= MIN_TEXT and not BLOCK.search(text[:3000])


def via_http(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,*/*",
                                               "Accept-Language": "en-GB,en;q=0.9"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read(5_000_000)
            ctype = r.headers.get("Content-Type", "")
            if "pdf" in ctype or url.lower().endswith(".pdf"):
                return r.status, pdf_to_text(body)
            return r.status, html_to_text(body.decode(r.headers.get_content_charset() or "utf-8", "replace"))
    except urllib.error.HTTPError as ex:
        return ex.code, ""
    except Exception as ex:  # timeouts, TLS, DNS
        return 0, f"ERROR {ex}"


def pdf_to_text(data):
    tool = shutil.which("pdftotext")
    if not tool:
        return ""
    p = subprocess.run([tool, "-layout", "-", "-"], input=data, capture_output=True, timeout=60)
    return p.stdout.decode("utf-8", "replace")


def chromium_path():
    for c in (os.environ.get("CHROMIUM"), "/opt/pw-browsers/chromium", shutil.which("chromium"), shutil.which("google-chrome")):
        if c and os.path.exists(c):
            return c
    return None


def ensure_chromium():
    """Start a local headless Chromium for Crawl4AI to attach to (avoids Playwright version mismatches)."""
    with socket.socket() as s:
        if s.connect_ex(("127.0.0.1", CDP_PORT)) == 0:
            return True
    exe = chromium_path()
    if not exe:
        return False
    args = [exe, "--headless=new", "--no-sandbox", f"--remote-debugging-port={CDP_PORT}", "--user-data-dir=/tmp/fetch-chromium"]
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    if proxy:
        args += [f"--proxy-server={proxy}", "--ignore-certificate-errors"]
    subprocess.Popen(args + ["about:blank"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    for _ in range(30):
        time.sleep(0.5)
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", CDP_PORT)) == 0:
                return True
    return False


async def _crawl(urls):
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CacheMode, CrawlerRunConfig
    bc = BrowserConfig(browser_mode="cdp", cdp_url=f"http://127.0.0.1:{CDP_PORT}", use_managed_browser=False,
                       verbose=False, enable_stealth=True)
    rc = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, page_timeout=45000, verbose=False)
    out = {}
    async with AsyncWebCrawler(config=bc) as c:
        for u in urls:
            try:
                r = await c.arun(u, config=rc)
                md = str(r.markdown or "") if r.success else ""
                out[u] = (r.status_code or 0, md)
            except Exception as ex:
                out[u] = (0, f"ERROR {ex}")
    return out


def via_crawl4ai(urls):
    try:
        import crawl4ai  # noqa: F401
    except ImportError:
        return {u: (0, "ERROR crawl4ai not installed (pip install crawl4ai)") for u in urls}
    if not ensure_chromium():
        return {u: (0, "ERROR no Chromium found") for u in urls}
    return asyncio.run(_crawl(urls))


def via_wayback(url):
    api = "https://archive.org/wayback/available?url=" + urllib.parse.quote(url, safe="")
    try:
        with urllib.request.urlopen(urllib.request.Request(api, headers={"User-Agent": UA}), timeout=30) as r:
            snap = json.load(r).get("archived_snapshots", {}).get("closest")
    except Exception:
        return 0, "", ""
    if not snap or snap.get("status") != "200":
        return 0, "", ""
    status, text = via_http(snap["url"].replace("http://", "https://", 1))
    return status, text, snap.get("timestamp", "")


def fetch_all(urls):
    results, pending = {}, []
    for u in urls:
        status, text = via_http(u)
        if status == 200 and usable(text):
            results[u] = ("http", status, text, "")
        else:
            pending.append(u)
    if pending:
        for u, (status, text) in via_crawl4ai(pending).items():
            if usable(text):
                results[u] = ("crawl4ai", status, text, "")
    for u in urls:
        if u in results:
            continue
        status, text, ts = via_wayback(u)
        if usable(text):
            results[u] = ("wayback", status, text, ts)
        else:
            results[u] = ("BLOCKED", status, "", "")
    return results


def main(argv):
    out_dir, do_print, urls = os.path.join(HERE, "work", "fetch"), False, []
    it = iter(argv)
    for a in it:
        if a == "--out":
            out_dir = next(it)
        elif a == "--print":
            do_print = True
        else:
            urls.append(a)
    if not urls:
        print(__doc__)
        return 1
    os.makedirs(out_dir, exist_ok=True)
    for u, (method, status, text, ts) in fetch_all(urls).items():
        if do_print:
            print(f"# {u} | method={method} | status={status}" + (f" | archived={ts}" if ts else "") + "\n" + text + "\n")
            continue
        if method == "BLOCKED":
            print(f"BLOCKED   {u}  (try Tavily extract / Firecrawl, or the run-locally script)")
            continue
        name = re.sub(r"[^a-z0-9]+", "-", urllib.parse.urlparse(u).netloc.lower()).strip("-") + "-" + hashlib.sha1(u.encode()).hexdigest()[:8] + ".md"
        path = os.path.join(out_dir, name)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(f"# {u} | method={method} | status={status}" + (f" | archived={ts}" if ts else "") + "\n\n" + text)
        print(f"{method:<9} {len(text):>7} chars  {u}  -> {os.path.relpath(path)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
