# 📸 Photobox — Sony A6000 + Python

Project photobox otomatis yang menggunakan kamera **Sony A6000** sebagai
sumber foto, dikontrol via **Imaging Edge Desktop (Remote)**, dan diproses
otomatis pakai **Python** — foto baru otomatis diberi border, digabung
jadi satu strip, lalu dicoba dicetak.

Karena Sony A6000 tidak mendukung kontrol shutter langsung dari
Python/USB (tidak ada API resmi & tidak didukung `gphoto2`/`digiCamControl`
lewat USB), project ini memakai pendekatan **folder watching**: foto
diambil lewat software resmi Sony, lalu Python memantau folder output dan
otomatis memprosesnya begitu file baru muncul.

## Cara kerja

```
Kamera A6000 (USB, mode "PC Remote")
        │
        ▼
Imaging Edge Desktop → Remote   (klik tombol shutter di sini)
        │
        ▼
Foto otomatis tersimpan ke folder di laptop
        │
        ▼
photobox_watcher.py memantau folder tsb (watchdog)
        │
        ▼
Foto baru terdeteksi → border + teks → gabung 3 foto → print
```

## Requirements

**Hardware**
- Kamera Sony A6000
- Kabel USB data (bukan charge-only)
- Laptop/PC Windows

**Software**
- Python 3.9+
- [Imaging Edge Desktop](https://support.d-imaging.sony.co.jp/app/imagingedge/l/download/) (gratis, resmi dari Sony)

**Python packages**
```bash
pip install -r requirements.txt
```

## Setup

Panduan lengkap step-by-step (setting kamera, install software, cari
lokasi folder foto, dst) ada di [`docs/PANDUAN_SETUP.md`](docs/PANDUAN_SETUP.md).

Ringkas:
1. Kamera: `MENU → Setup → USB Connection → PC Remote`
2. Install & buka **Imaging Edge Desktop → Remote**, sambungkan kamera via USB
3. Cari lokasi folder tempat foto tersimpan (biasanya di folder Pictures / OneDrive)
4. Edit `WATCH_FOLDER` di `photobox_watcher.py` sesuai folder tersebut
5. Jalankan:
   ```bash
   python photobox_watcher.py
   ```
6. Klik tombol shutter di Imaging Edge Remote sebanyak 3x → hasil otomatis
   masuk ke folder `hasil_photobox/`

## Struktur project

```
photobox-sony-a6000/
├── photobox_watcher.py      # script utama
├── requirements.txt
├── docs/
│   └── PANDUAN_SETUP.md     # panduan lengkap dari nol
└── README.md
```

## Konfigurasi

Beberapa hal yang bisa diubah di bagian atas `photobox_watcher.py`:

```python
WATCH_FOLDER = r"C:\Users\NAMA_USER\Pictures"   # folder yang dipantau
NUM_PHOTOS = 3                                    # jumlah foto per sesi
```

## Catatan

- Live view tidak tersedia untuk A6000 lewat USB (hanya still capture)
- Kalau printer tidak terpasang, proses print akan gagal dengan warning
  saja — tidak menghentikan program
- Folder hasil (`hasil_photobox/`) tidak ikut ter-commit ke git (lihat `.gitignore`)
