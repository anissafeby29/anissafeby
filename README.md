# Belajar Operasi Ortopedi

Aplikasi web edukasi untuk mempelajari prinsip dasar berbagai operasi ortopedi: indikasi, kontraindikasi, persiapan, langkah operasi, instrumen kunci, komplikasi, dan tips klinis — dilengkapi kuis interaktif, flashcard istilah, dan glosarium.

Dibangun sebagai aplikasi statis (HTML/CSS/JS murni, tanpa framework atau proses build), sehingga bisa langsung dibuka di browser atau di-hosting di mana saja (GitHub Pages, Netlify, dsb).

## Menjalankan secara lokal

Buka `index.html` langsung di browser, atau jalankan server statis sederhana:

```bash
python3 -m http.server 8000
```

lalu buka `http://localhost:8000`.

## Struktur

- `index.html` — kerangka halaman (sidebar navigasi + area konten)
- `assets/data.js` — seluruh konten: daftar kategori, prosedur operasi, soal kuis, dan glosarium
- `assets/app.js` — logika SPA: routing antar halaman, mesin kuis, flashcard, dan pelacakan progres (localStorage)
- `assets/style.css` — tampilan visual

## Fitur

- **Materi Operasi** — dikelompokkan per kategori (Fraktur & Fiksasi, Artroplasti, Artroskopi, Tulang Belakang, Amputasi, Ortopedi Anak), setiap prosedur berisi definisi, indikasi, kontraindikasi, persiapan, langkah operasi, instrumen kunci, komplikasi, dan tips klinis.
- **Kuis** — pilih kategori soal, jawab, dapat penjelasan langsung, lihat skor dan tinjauan jawaban di akhir.
- **Flashcard** — kartu istilah ortopedi yang bisa dibalik dan ditandai sudah dihafal.
- **Glosarium** — daftar istilah bedah ortopedi yang bisa dicari.
- **Progres Saya** — ringkasan prosedur yang sudah dipelajari, istilah yang sudah dihafal, dan riwayat skor kuis, tersimpan otomatis di perangkat (localStorage).

> Catatan: seluruh konten bersifat edukasi umum (overview) dan bukan pengganti panduan klinis resmi atau supervisi dokter spesialis ortopedi.
