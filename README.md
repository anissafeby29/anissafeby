# Profil dr. Anissa Feby Canintika, Sp.OT

Website profil profesional untuk https://anissafeby.com/.

Halaman mencakup profil, foto, pendidikan, penghargaan ilmiah, dan publikasi dengan tautan PubMed. Isi profil disalin dari website aktif pada 9 Oktober 2026. Foto tertanam di HTML; tidak membutuhkan proses build atau paket JavaScript.

## File

- `index.html`: halaman profil dan metadata SEO.
- `robots.txt`: aturan perayapan dan lokasi sitemap.
- `sitemap.xml`: URL utama website.
- `docs/rencana-pengunjung-anissafeby.md`: audit awal dan rencana pengembangan pengunjung.

## Preview dan deployment

Jalankan `python3 -m http.server 8000` dari root repository, lalu buka http://localhost:8000/.

Untuk hosting statis, publikasikan root repository tanpa build command. Domain dan koneksi hosting perlu menunjuk ke repository serta branch `main` ini. Push ke GitHub saja tidak membuktikan bahwa hosting anissafeby.com menggunakan repository ini.

## Cadangan

Isi The Fellowship Portal sebelumnya tersimpan pada branch `backup/fellowship-before-profile-20261009` dan riwayat Git.

## Optional Analytics

The existing GA4 stream `G-R5G70KHYDN` is integrated in `analytics.js` using basic opt-in consent. The local adapter loads on the profile; the Google tag remains absent until Allow analytics is selected. Advertising purposes stay denied. Consent is remembered for up to 180 days; withdrawal disables collection, clears accessible GA cookies and reloads the loaded tag. `privacy.html` explains the choice.

Only the public site origin and an external referring origin are passed with a generic title. Query strings, referring paths, fragments, credentials and internal referrers are excluded. The approved GA4 stream has Enhanced Measurement disabled; do not re-enable it without reviewing the extra automatically collected data.

Run `node --test tests/analytics.test.cjs`, `node --check analytics.js` and `git diff --check`. The tests execute the real adapter with browser boundary fakes and do not send data to Google. Production consent and collector delivery need separate browser/GA4 verification. Deploy `index.html`, `analytics.js`, `analytics.css`, `privacy.html`, `robots.txt` and `sitemap.xml`; do not publish tests or Git metadata.
