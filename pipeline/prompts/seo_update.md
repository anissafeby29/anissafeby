SEO update for thefellowshipportal.com

You are improving the search visibility of thefellowshipportal.com, a free directory of medical and surgical
fellowships (about 6,300 programmes, 25 specialties, 54 countries). Reply to me in Indonesian; write all site
content in English.

## How the site works (read before changing anything)
- Repos: anissafeby29/anissafeby (data + build scripts) and anissafeby29/thefellowshipportal (built site,
  auto-deployed by Hostinger from main to public_html). Clone both side by side.
- Everything is generated. Never hand-edit HTML in the site repo; change the generators in
  anissafeby/fellowship-data/ and rebuild:
  - build_site.py: home page (site_template.html) and assets/programmes.json
  - profiles.py: one profile per programme at /programs/<slug>/, About, Contact, sitemap.xml, robots.txt, .htaccess
  - pages.py: /specialties/, /countries/, /training/, /institutions/ (one page per institution), /deadlines/,
    /compare/, 404 page and old-URL redirects
- Publish: `PORTAL_REPO=../thefellowshipportal pipeline/publish.sh "<commit message>"` from the anissafeby repo.
  If the site does not update within a few minutes, tell me to click Deploy in hPanel > Advanced > GIT.

## Already done (do not redo)
Unique title, meta description and canonical on every page; Open Graph and Twitter card with assets/og.png;
JSON-LD (EducationalOccupationalProgram on profiles, CollectionPage + ItemList on landing pages); sitemap.xml
with all pages; robots.txt; 301 redirects for old URLs; 404 page; compression and caching in .htaccess.

## Tasks, in this order
1. Audit first. Build locally, then write a short audit covering:
   - duplicate or truncated titles and descriptions
   - pages with thin content: institutions with a single programme, landing pages with fewer than 3 programmes
   - broken internal links
   - orphan pages: pages nothing links to
   - JSON-LD validity: parse every block, and check required fields against schema.org
   - pages missing from sitemap.xml
   - largest pages by size
   Show me the audit before making big changes.
2. Titles and descriptions. Lead with what people search, for example
   "Paediatric Cardiology Fellowship in Toronto | SickKids | The Fellowship Portal". Put the specialty, country
   and "open to international applicants" in the description when the data supports it. Keep titles under about
   60 characters and descriptions under 155, and keep them unique.
3. Landing pages. Add a short intro paragraph per specialty and country page, generated from the data:
   - how many programmes there are and the top cities
   - the share open to IMGs and the share with a stated visa route
   - typical duration
   - the next deadlines
   Also add a small FAQ section generated from the data, with FAQPage JSON-LD only if the answers are factual
   and on the page. Add cross-links: specialty × country links where at least 5 programmes exist.
4. Specialty × country pages. Create /specialties/<spec>/<country>/ only for combinations with 8 or more
   programmes, and add them to the sitemap. Avoid thin or near-duplicate pages; if a page would just repeat
   another, skip it.
5. Internal linking:
   - breadcrumbs with BreadcrumbList JSON-LD on profiles and landing pages
   - "Related programmes" already exists on profiles; make sure every profile links to its specialty, country
     and institution pages
6. Sitemap. Add `<lastmod>` from the build date, and split it into a sitemap index if it exceeds 50,000 URLs
   or 50 MB.
7. Performance. Check Core Web Vitals risks:
   - font loading (use font-display: swap and preload the main font)
   - layout shift on the home page while programmes.json loads
   - keep the home page's first view usable without JavaScript where practical
8. Indonesian audience (optional, ask me first). Propose a small set of Indonesian-language guide pages, for
   example "Fellowship di luar negeri untuk dokter Indonesia", "Cara daftar fellowship di Amerika (ECFMG, J-1)"
   and "Fellowship di Singapura untuk dokter Indonesia". Use hreflang only if real translated pages exist.

## Rules
- Facts only from the existing data or official sources. Never invent programme details, rankings, salaries
  or success rates. No fake reviews or ratings markup.
- No keyword stuffing, hidden text, doorway pages or auto-generated pages without unique, useful content.
- Do not change URLs of existing pages. If a URL must change, add a 301 redirect.
- Keep the visual design (navy hero, gold accent, boarding-pass cards) and the light/dark theme working.
- Test before publishing:
  - rebuild and serve locally (`python3 -m http.server`)
  - check the home page, a profile, a specialty, a country and an institution page in Playwright, at desktop
    and at 390 px wide
  - no console errors and no horizontal scroll
  - validate the JSON-LD
- Commit messages end with the attribution lines your environment provides. Publish once everything passes.

## When done, report to me in Indonesian
What changed, how many pages were affected, before/after examples of 2–3 titles and descriptions, and what
I should do in Google Search Console: resubmit the sitemap, request indexing for key pages, and which reports
to watch over the next 2–4 weeks.
