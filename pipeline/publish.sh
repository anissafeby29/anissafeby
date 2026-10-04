#!/bin/bash
# Rebuild data + site and push both repos.
# Usage: pipeline/publish.sh "commit message"   (PORTAL_REPO defaults to ../thefellowshipportal next to this repo)
set -e
HERE=$(cd "$(dirname "$0")" && pwd); REPO=$(dirname "$HERE"); PORTAL=${PORTAL_REPO:-$(dirname "$REPO")/thefellowshipportal}
python3 "$HERE/merge.py" | grep -E "patches|^programs" || true
cd "$REPO" && python3 fellowship-data/build_site.py
mkdir -p "$PORTAL/data"
for f in "$REPO"/fellowship-data/*; do cp -r "$f" "$PORTAL/data/"; done
sed -i "s|fellowship-data/build_site.py|data/build_site.py|" "$PORTAL/data/build_site.py"
cd "$PORTAL" && python3 data/build_site.py
MSG="$1"
for R in "$REPO" "$PORTAL"; do
  cd "$R"; git add -A; git diff --cached --quiet || git commit -qm "$MSG"; git push -q origin main; echo "pushed $R"
done
