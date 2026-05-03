# Panduan Deployment Sistem Sinkronisasi Terdistribusi

Dokumen ini menyediakan panduan langkah demi langkah untuk melakukan deployment dan menjalankan Sistem Sinkronisasi Terdistribusi menggunakan Docker dan Docker Compose.

## Prasyarat

Sebelum memulai, pastikan Anda telah menginstal perangkat lunak berikut di sistem Anda:

*   **Docker:** [Instalasi Docker Engine](https://docs.docker.com/engine/install/)
*   **Docker Compose:** [Instalasi Docker Compose](https://docs.docker.com/compose/install/)
*   **Git:** [Instalasi Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)

## Langkah-langkah Deployment

### 1. Clone Repositori

Pertama, clone repositori proyek dari GitHub:

```bash
git clone <URL_REPOSITORI_ANDA>
cd distributed-sync-system
```

### 2. Konfigurasi Lingkungan

Sistem menggunakan file `.env` untuk konfigurasi lingkungan. Salin file `.env.example` dan sesuaikan sesuai kebutuhan Anda.

```bash
cp .env.example .env
```

Edit file `.env` untuk mengatur variabel lingkungan seperti `REDIS_HOST`, `REDIS_PORT`, `NODE_ID`, dan `CLUSTER_NODES`. Pastikan `CLUSTER_NODES` mencantumkan semua node yang akan Anda jalankan dengan format `node_id:port`.

Contoh `.env`:

```
REDIS_HOST=redis
REDIS_PORT=6379
NODE_ID=node1
CLUSTER_NODES=node1:8001,node2:8002,node3:8003
LOG_LEVEL=INFO
```

**Catatan:** Untuk setiap node yang Anda jalankan, Anda perlu memastikan `NODE_ID` unik dan `CLUSTER_NODES` mencerminkan semua node yang berpartisipasi dalam cluster.

### 3. Bangun dan Jalankan Kontainer

Navigasikan ke direktori `docker` di dalam proyek Anda dan gunakan Docker Compose untuk membangun image dan menjalankan kontainer:

```bash
cd docker
docker-compose build
docker-compose up -d
```

Perintah ini akan melakukan hal berikut:

*   Membangun image Docker untuk setiap node menggunakan `Dockerfile.node`.
*   Membuat dan memulai kontainer untuk Redis, node1, node2, dan node3 seperti yang didefinisikan dalam `docker-compose.yml`.
*   Kontainer akan berjalan di latar belakang (`-d`).

### 4. Verifikasi Deployment

Anda dapat memverifikasi bahwa semua kontainer berjalan dengan benar menggunakan perintah berikut:

```bash
docker-compose ps
```

Anda akan melihat daftar kontainer yang sedang berjalan. Anda juga dapat memeriksa log dari setiap layanan:

```bash
docker-compose logs node1
```

Untuk menguji fungsionalitas API, Anda dapat mengakses endpoint kesehatan dari salah satu node, misalnya:

```bash
curl http://localhost:8001/health
```

Ini akan mengembalikan status kesehatan node.

### 5. Scaling Node (Opsional)

Untuk menskalakan node secara dinamis, Anda dapat memodifikasi file `docker-compose.yml` untuk menambahkan lebih banyak layanan node, atau menggunakan perintah `docker-compose up --scale` jika Anda memiliki konfigurasi yang memungkinkan.

Misalnya, untuk menskalakan node `app` (jika didefinisikan sebagai layanan yang dapat diskalakan):

```bash
docker-compose up -d --scale app=5
```

### 6. Menghentikan dan Menghapus Kontainer

Untuk menghentikan dan menghapus semua kontainer, jaringan, dan volume yang dibuat oleh `docker-compose`:

```bash
docker-compose down
```

Untuk menghentikan kontainer tanpa menghapusnya:

```bash
docker-compose stop
```

## Troubleshooting

*   **Kontainer tidak dapat dimulai:** Periksa log kontainer untuk pesan kesalahan (`docker-compose logs <service_name>`). Pastikan tidak ada konflik port atau masalah konfigurasi dalam file `.env` atau `docker-compose.yml`.
*   **Komunikasi antar node gagal:** Pastikan nama host dan port dalam `CLUSTER_NODES` di file `.env` sudah benar dan sesuai dengan konfigurasi jaringan Docker Compose.
*   **Masalah Redis:** Pastikan kontainer Redis berjalan dan dapat diakses oleh node-node aplikasi.

Jika Anda mengalami masalah, pastikan untuk memeriksa dokumentasi Docker dan Docker Compose untuk informasi lebih lanjut.
