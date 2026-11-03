# Python CRUD REST API — CI/CD Pipeline dengan Jenkins, GitHub, Docker, dan ngrok

Proyek praktikum Hands-On CI/CD untuk membangun layanan REST API menggunakan Python 3.11 (`ThreadingHTTPServer`), mengintegrasikan source control GitHub dengan Jenkins Pipeline, melakukan pengujian otomatis, membangun Docker image dengan persistensi Docker Named Volume, serta menguji trigger otomatis via GitHub Webhook dan ngrok.

## Daftar Endpoint REST API

| Method | Endpoint | Deskripsi |
| :--- | :--- | :--- |
| `GET` | `/` atau `/health` | Memeriksa status kesehatan layanan (`HTTP 200`, `{"status": "active", "service": "Backend API"}`). |
| `GET` | `/messages` | Mengambil seluruh daftar pesan beserta total pesan. |
| `GET` | `/messages?search=<kata>` | Memfilter daftar pesan berdasarkan kata kunci (case-insensitive). |
| `GET` | `/messages/<id>` | Mengambil satu pesan spesifik berdasarkan indeks integer (`0..N-1`). |
| `POST` | `/messages` | Menambahkan pesan baru (JSON `{"message": "..."}`, maks 500 karakter). |
| `DELETE` | `/messages?index=<id>` | Menghapus pesan pada indeks tertentu. |
