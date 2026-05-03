# Distributed Sync System

Dokumentasi ringkas untuk proyek tugas "Implementasi Distributed Synchronization System".

## Tujuan

Proyek ini mensimulasikan sistem sinkronisasi terdistribusi yang mencakup:
- Distributed Lock Manager (Raft-based)
- Distributed Queue (consistent hashing + persistence)
- Distributed Cache Coherence (MESI)

Implementasi ditujukan untuk memenuhi spesifikasi tugas mata kuliah Sistem Paralel dan Terdistribusi.

## Struktur Proyek (penting)

- `src/` — kode sumber utama
	- `nodes/` — node components (`base_node.py`, `lock_manager.py`, `queue_node.py`, `cache_node.py`)
	- `consensus/` — algoritma konsensus (`raft.py`)
	- `communication/` — messenger dan failure detector (`message_passing.py`, `failure_detector.py`)
	- `utils/` — konfigurasi dan metrik
- `docker/` — `Dockerfile.node` dan `docker-compose.yml`
- `docs/` — `architecture.md`, `api_spec.yaml`, `deployment_guide.md`
- `benchmarks/`, `tests/`, `requirements.txt`, `.env.example`

## Status Implementasi (ringkas)

- Raft (`src/consensus/raft.py`): kerangka dasar ada (state, handlers), tetapi RPC `request_vote` dan `send_heartbeats` masih placeholder; log replication dan persistent storage belum lengkap.
- Distributed Lock Manager (`src/nodes/lock_manager.py`): API dasar ada, namun belum terintegrasi penuh dengan Raft (propose/commit) dan deteksi deadlock belum diimplementasikan.
- Distributed Queue (`src/nodes/queue_node.py`): `ConsistentHash` dan persistence per-node sudah ada; replikasi, ack/retry, dan recovery antar-node belum lengkap.
- Cache Coherence (`src/nodes/cache_node.py`): protokol MESI dasar diimplementasikan; belum ada kebijakan LRU/LFU dan endpoint HTTP belum terhubung di `BaseNode`.
- Komunikasi (`src/communication/message_passing.py`): `Messenger` dan `FailureDetector` siap untuk RPC berbasis `aiohttp`.
- Containerization (`docker/`): `Dockerfile.node` dan `docker-compose.yml` tersedia dan siap untuk pengujian multi-node.

## Cara Menjalankan (Docker, lokal)

1. Salin contoh env dan sesuaikan:

```bash
cp .env.example .env
```

2. Build dan jalankan dengan Docker Compose (direktori repo root):

```bash
docker-compose -f docker/docker-compose.yml build
docker-compose -f docker/docker-compose.yml up -d
```

3. Verifikasi health endpoint pada node (mis. untuk `node1` di port 8001):

```bash
curl http://localhost:8001/health
```

Catatan: `docker-compose.yml` memetakan service internal port `8000` ke host ports `8001`,`8002`,`8003`.

## API Ringkas (sesuai `docs/api_spec.yaml`)

- `GET /health` — health check
- `GET /metrics` — metrik node
- `POST /raft/append_entries` — Raft AppendEntries RPC
- `POST /raft/request_vote` — Raft RequestVote RPC
- `POST /lock/acquire` — akuisisi kunci (belum sepenuhnya terhubung)
- `POST /lock/release` — release kunci (belum sepenuhnya terhubung)
- `POST /queue/enqueue` — enqueue pesan (lokal)
- `POST /queue/dequeue` — dequeue pesan (lokal)
- `POST /cache/read` — baca cache (perlu routing)
- `POST /cache/write` — tulis cache (perlu routing)

Beberapa endpoint di atas tercantum di spesifikasi API namun belum diimplementasikan sepenuhnya di `BaseNode`.

## Testing & Benchmarking

- Dependensi untuk testing: lihat `requirements.txt` (pytest, pytest-asyncio, locust).
- Skrip benchmark ada di `benchmarks/load_test_scenarios.py` (perlu penyesuaian setelah implementasi komponen yang lengkap).

## Langkah Selanjutnya (prioritas)

1. Lengkapi RPC Raft (`request_vote`, `send_heartbeats`, `append_entries`) dan log replication.
2. Hubungkan `DistributedLockManager` ke Raft (propose/commit operasi lock) dan implementasikan redirection ke leader.
3. Implementasikan replikasi pesan dan ack/retry di `DistributedQueue` untuk guarantee at-least-once.
4. Tambahkan API `/lock/*`, `/queue/*`, `/cache/*` di `src/nodes/base_node.py` dan sesuaikan `docs/api_spec.yaml` bila perlu.
5. Tambahkan LRU/LFU di `cache_node.py` dan wiring invalidation/broadcast menggunakan `Messenger`.
6. Tambah unit/integration tests dan jalankan benchmark serta dokumentasikan hasil.

## Referensi

- `docs/architecture.md` — arsitektur lengkap
- `docs/deployment_guide.md` — panduan deployment
- `docs/api_spec.yaml` — spesifikasi API OpenAPI

---

Jika Anda ingin, saya bisa mulai mengimplementasikan satu komponen sekarang (mis. lengkapi RPC Raft) atau membuat checklist terperinci dengan estimasi waktu per tugas.

# TUGAS_3_SISTER
# TUGAS_3_SISTER
