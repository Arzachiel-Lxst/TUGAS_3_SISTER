# Arsitektur Sistem Sinkronisasi Terdistribusi

## 1. Pendahuluan

Dokumen ini menjelaskan arsitektur sistem sinkronisasi terdistribusi yang dikembangkan sebagai bagian dari Tugas 2 mata kuliah Sistem Parallel dan Terdistribusi. Sistem ini dirancang untuk mensimulasikan skenario real-world dalam distributed systems, dengan fokus pada penanganan multiple nodes yang berkomunikasi dan mensinkronisasi data secara konsisten.

## 2. Komponen Utama

Sistem ini terdiri dari beberapa komponen utama yang bekerja sama untuk mencapai sinkronisasi terdistribusi:

### 2.1. Node Dasar (BaseNode)

Setiap instance dari sistem adalah `BaseNode` yang mengintegrasikan fungsionalitas dari Distributed Lock Manager, Distributed Queue, dan Distributed Cache Coherence. `BaseNode` menggunakan FastAPI untuk menyediakan endpoint API RESTful untuk komunikasi antar node dan interaksi klien.

### 2.2. Distributed Lock Manager (DLM)

DLM bertanggung jawab untuk mengelola kunci terdistribusi (shared dan exclusive locks) di seluruh cluster. Implementasi DLM didasarkan pada algoritma konsensus Raft untuk memastikan konsistensi dan toleransi kesalahan. DLM juga mencakup mekanisme deteksi deadlock.

**Algoritma Konsensus Raft:**

Raft adalah algoritma konsensus yang dirancang agar mudah dipahami dan diimplementasikan. Raft memastikan bahwa semua node dalam cluster menyetujui urutan log yang sama, yang menjadi dasar untuk operasi DLM. Node Raft dapat berada dalam salah satu dari tiga state: Follower, Candidate, atau Leader.

*   **Follower:** Node pasif yang mendengarkan pesan dari Leader atau Candidate.
*   **Candidate:** Node yang mencoba menjadi Leader dengan memulai pemilihan.
*   **Leader:** Node yang bertanggung jawab untuk mereplikasi log ke Follower dan memproses permintaan klien.

### 2.3. Distributed Queue System

Sistem antrian terdistribusi ini memungkinkan multiple producers dan consumers untuk bertukar pesan secara andal. Implementasi menggunakan Consistent Hashing untuk mendistribusikan pesan ke node-node antrian, memastikan distribusi beban yang merata dan penanganan kegagalan node tanpa kehilangan data. Fitur message persistence dan recovery juga diimplementasikan untuk menjamin `at-least-once delivery`.

**Consistent Hashing:**

Consistent Hashing adalah teknik hashing yang meminimalkan reorganisasi data saat node ditambahkan atau dihapus dari sistem. Ini membantu dalam menjaga ketersediaan dan kinerja sistem antrian saat terjadi perubahan topologi cluster.

### 2.4. Distributed Cache Coherence

Komponen ini mengelola konsistensi data di antara beberapa node cache. Protokol MESI (Modified, Exclusive, Shared, Invalid) diimplementasikan untuk memastikan bahwa semua node memiliki pandangan yang konsisten terhadap data yang di-cache. Mekanisme invalidasi cache dan propagasi update ditangani untuk menjaga integritas data. Kebijakan penggantian cache (LRU/LFU) juga dipertimbangkan.

**Protokol MESI:**

MESI adalah protokol cache coherence berbasis snooping yang menggunakan empat state untuk setiap baris cache: Modified, Exclusive, Shared, dan Invalid. Protokol ini memastikan bahwa setiap data yang di-cache memiliki state yang benar di semua cache, mencegah inkonsistensi data.

### 2.5. Komunikasi Antar Node

Komunikasi antar node diimplementasikan menggunakan `aiohttp` untuk permintaan HTTP asinkron. Ini memungkinkan node untuk mengirim pesan (misalnya, permintaan vote Raft, heartbeat, permintaan kunci, pesan antrian, invalidasi cache) satu sama lain secara efisien. `FailureDetector` memantau ketersediaan node dalam cluster.

### 2.6. Metrik dan Pemantauan

Sistem mengumpulkan metrik kinerja seperti latensi, throughput, dan uptime menggunakan `MetricsCollector`. Metrik ini penting untuk analisis kinerja dan identifikasi bottleneck.

## 3. Struktur Proyek

Struktur proyek mengikuti konvensi yang umum untuk aplikasi Python, dengan pemisahan yang jelas antara kode sumber, tes, dokumentasi, dan konfigurasi Docker.

```
distributed-sync-system/
├── src/
│   ├── nodes/
│   │   ├── __init__.py
│   │   ├── base_node.py
│   │   ├── lock_manager.py
│   │   ├── queue_node.py
│   │   └── cache_node.py
│   ├── consensus/
│   │   ├── __init__.py
│   │   ├── raft.py
│   │   └── pbft.py (opsional)
│   ├── communication/
│   │   ├── __init__.py
│   │   ├── message_passing.py
│   │   └── failure_detector.py
│   └── utils/
│       ├── __init__.py
│       ├── config.py
│       └── metrics.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── performance/
├── docker/
│   ├── Dockerfile.node
│   └── docker-compose.yml
├── docs/
│   ├── architecture.md
│   ├── api_spec.yaml
│   └── deployment_guide.md
├── benchmarks/
│   └── load_test_scenarios.py
├── requirements.txt
├── .env.example
├── README.md
└── report.pdf
```

## 4. Containerization

Setiap komponen sistem di-containerisasi menggunakan Docker. `Dockerfile.node` mendefinisikan lingkungan untuk setiap node, dan `docker-compose.yml` digunakan untuk orkestrasi dan deployment multi-node, termasuk layanan Redis sebagai backend untuk distributed state. Konfigurasi lingkungan dikelola melalui file `.env`.

## 5. Alur Kerja (Contoh)

1.  **Inisialisasi:** Node-node dimulai, Raft election terjadi, dan seorang Leader dipilih.
2.  **Permintaan Kunci:** Klien meminta kunci dari Leader DLM. Leader memproses permintaan, mereplikasi ke Follower, dan mengkonfirmasi ke klien.
3.  **Pengiriman Pesan:** Produser mengirim pesan ke Distributed Queue. Consistent Hashing menentukan node mana yang akan menyimpan pesan, dan pesan di-persist.
4.  **Akses Cache:** Klien membaca/menulis data ke Distributed Cache. Protokol MESI memastikan konsistensi di seluruh node cache.
5.  **Penanganan Kegagalan:** Jika Leader Raft gagal, election baru dimulai. Jika node antrian gagal, Consistent Hashing mengarahkan pesan ke node yang tersedia, dan pesan yang di-persist dapat dipulihkan.

## 6. Kesimpulan

Arsitektur ini menyediakan fondasi yang kuat untuk sistem sinkronisasi terdistribusi yang toleran terhadap kesalahan, konsisten, dan dapat diskalakan, memenuhi persyaratan tugas yang diberikan.
