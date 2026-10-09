# Rencana meningkatkan pengunjung anissafeby.com

Audit publik: 9 Oktober 2026. Target awal: pembaca Indonesia yang mencari profil dokter ortopedi dan informasi bahu/siku, serta kolega yang mencari publikasi. Sesuaikan prioritas apabila tujuan utama adalah kolaborasi akademik.

## Pembaruan repository

Setelah audit awal, atas permintaan pemilik, branch main diganti menjadi profil dari anissafeby.com. Metadata canonical, Open Graph, Person JSON-LD, robots.txt, dan sitemap.xml ditambahkan. Temuan di bawah adalah kondisi sebelum perubahan repository; deployment domain aktif belum diverifikasi. Isi Fellowship Portal tersimpan pada branch backup/fellowship-before-profile-20261009.

## Temuan yang terverifikasi saat audit awal

- anissafeby.com menampilkan profil profesional berbahasa Inggris, pendidikan, penghargaan, dan tautan publikasi PubMed.
- Judul halaman hanya berisi nama dan gelar. Deskripsi masih umum dan berbahasa Inggris.
- HTML beranda yang diperiksa belum memuat canonical, Open Graph, atau JSON-LD.
- Permintaan ke /robots.txt dan /sitemap.xml menampilkan halaman “Page not found”. Tidak adanya robots.txt sendiri tidak berarti situs diblokir.
- Beranda repository anissafeby29/anissafeby justru berisi The Fellowship Portal, dengan metadata domain thefellowshipportal.com. Pastikan sumber deployment anissafeby.com sebelum mengubah kode utama. Dokumen ini tidak mengubah deployment.
- Data Search Console dan analytics belum diperiksa; jumlah pengunjung, ranking, dan status indeks Google belum diketahui.

## Prioritas 30 hari

### Minggu 1: ukur dan rapikan fondasi

1. Verifikasi properti domain anissafeby.com di Google Search Console memakai DNS. Catat baseline klik, impresi, CTR, halaman terindeks, dan kueri.
2. Periksa beranda melalui URL Inspection dan ajukan pengindeksan setelah perbaikan.
3. Di sumber website profil yang benar, tambahkan canonical https://anissafeby.com/, metadata berbagi, dan sitemap berisi URL publik yang benar-benar tersedia. Cantumkan sitemap di robots.txt, lalu kirim melalui Search Console.
4. Usulan judul: “dr. Anissa Feby Canintika, Sp.OT | Dokter Spesialis Ortopedi”. Usulan deskripsi: “Profil dr. Anissa Feby Canintika, Sp.OT, dokter spesialis ortopedi dan traumatologi. Pendidikan, penghargaan, dan publikasi ilmiah.”
5. Tambahkan data terstruktur Person dengan nama, gelar, URL, dan afiliasi yang sudah diverifikasi. Jangan mengarang alamat praktik, jam layanan, rating, atau status subspesialis; halaman saat ini menyebut masih menjalani pelatihan bahu dan siku.
6. Uji tampilan ponsel dan PageSpeed Insights. Optimalkan gambar jika memang menjadi hambatan; ukur dahulu.

### Minggu 2–3: buat halaman yang menjawab kebutuhan pembaca

- Sediakan profil bahasa Indonesia, dengan tautan jelas ke versi Inggris. Gunakan URL terpisah dan hreflang bila kedua versi dibuat lengkap.
- Rencanakan artikel: “Apa yang ditangani dokter ortopedi?”, “Nyeri bahu: kapan perlu diperiksa?”, “Cedera siku: informasi untuk pasien”, dan “Persiapan sebelum konsultasi ortopedi”. Ini ide topik, bukan hasil riset volume kata kunci.
- Terbitkan 1 artikel bermutu per minggu setelah ditinjau dokter. Gunakan bahasa sederhana, nama penulis, tanggal tinjauan, dan referensi medis primer/pedoman yang relevan. Jangan mengubah hasil studi praklinis menjadi klaim manfaat terapi pada manusia.
- Tautkan artikel ke profil penulis dan artikel terkait. Beri setiap halaman judul dan deskripsi yang spesifik.
- Jika menerima pasien, tampilkan lokasi, jadwal, serta cara membuat janji hanya setelah data dikonfirmasi. Untuk tujuan akademik, tampilkan jalur kontak profesional untuk kolaborasi.

### Minggu 4: distribusi dan evaluasi

- Bagikan ringkasan artikel melalui akun profesional Instagram atau LinkedIn dengan tautan ke artikel lengkap. Gunakan satu konten utama untuk beberapa ringkasan pendek.
- Tambahkan tautan website pada profil profesional yang dikelola sendiri, misalnya ORCID dan profil institusi yang mengizinkan. Minta koreksi tautan melalui kanal resmi bila profil dikelola institusi.
- Bila memenuhi syarat dan memiliki lokasi layanan yang terverifikasi, pertimbangkan Google Business Profile. Jangan membuat lokasi praktik fiktif.
- Bandingkan data Search Console per 28 hari: klik organik, impresi, CTR, kueri non-nama, dan halaman yang mulai mendapat pengunjung. Jika memakai analytics, ukur klik kontak/janji sebagai konversi tanpa mengumpulkan detail kesehatan pasien.

## Target dan batas interpretasi

Target bulan pertama adalah pengukuran aktif, masalah teknis ditangani, profil Indonesia tersedia, dan 3–4 artikel yang ditinjau dokter. Tetapkan target pertumbuhan angka setelah baseline tersedia. SEO tidak menjamin peringkat atau jumlah pengunjung tertentu; evaluasi perkembangan dalam 8–12 minggu sebagai jadwal evaluasi, bukan janji hasil. Hindari membeli traffic bot, backlink massal, dan artikel duplikat.

## Referensi

- Website yang diaudit: https://anissafeby.com/
- Google SEO Starter Guide: https://developers.google.com/search/docs/fundamentals/seo-starter-guide
- Google Search Console: https://developers.google.com/search/docs/monitor-debug/search-console-start
- Sitemap: https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap

## Langkah implementasi berikutnya

Identifikasi repository/branch atau proyek hosting yang benar-benar menerbitkan anissafeby.com. Terapkan perubahan teknis di sumber itu; jangan mengganti beranda Fellowship Portal dengan profil dokter. Verifikasi domain, akses Search Console, dan data praktik memerlukan akses pemilik atau informasi yang belum tersedia dalam audit ini.
