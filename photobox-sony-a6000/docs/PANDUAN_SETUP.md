# Panduan Lengkap: Photobox dengan Kamera Sony A6000 (Python)

Dokumen ini merangkum semua langkah dari nol sampai berhasil, khusus jalur
**kamera fisik (Sony A6000)** — bukan webcam.

---

## 1. Kenapa arsitekturnya seperti ini?

Sony A6000 **tidak didukung** untuk kontrol langsung lewat USB oleh
library pihak ketiga seperti `gphoto2` atau `digiCamControl` (kamera ini
hanya didukung tools tersebut lewat WiFi). Solusi yang berhasil jalan
adalah kombinasi:

```
Kamera A6000 (USB, mode "PC Remote")
        ↓
Imaging Edge Desktop / Remote  ← kamu klik tombol shutter di sini
        ↓
Foto otomatis tersimpan ke folder di laptop
        ↓
Python (watchdog) memantau folder itu
        ↓
Begitu ada foto baru → otomatis diberi border, digabung, di-print
```

Python tidak memicu rana kamera secara langsung (karena tidak ada API
resmi untuk itu), tapi **otomatis memproses** setiap foto begitu muncul.

---

## 2. Hardware yang dibutuhkan

- Kamera **Sony A6000**
- Kabel **USB data** (bukan kabel charge-only) yang cocok dengan port kamera
- Laptop/PC Windows
- Baterai kamera terisi cukup (jangan sampai 0%, seperti kasus sebelumnya)

---

## 3. Setting yang harus diubah di kamera

1. Tekan **MENU**
2. Buka tab **Setup** (ikon toolbox 🧰)
3. Cari item **"USB Connection"**
4. Ubah dari default (**Mass Storage**) menjadi **"PC Remote"**

> Kalau mode ini tidak diganti, kamera hanya akan terbaca sebagai flashdisk
> biasa (Mass Storage) dan tidak bisa dikontrol dari software di PC.

---

## 4. Software desktop yang dibutuhkan

### Imaging Edge Desktop (dari Sony, gratis)
- Download resmi: `https://support.d-imaging.sony.co.jp/app/imagingedge/l/download/`
- Install seperti aplikasi Windows biasa
- Setelah kamera disambungkan via USB (mode PC Remote), buka aplikasi ini
  lalu pilih fitur **"Remote"**
- Kalau berhasil, nama/model kamera akan muncul di aplikasi, lengkap
  dengan kontrol shutter, ISO, shutter speed, dll.
- Foto yang diambil dari sini otomatis tersimpan ke sebuah folder di
  laptop (defaultnya biasanya folder Pictures, tapi bisa berbeda-beda
  tergantung setting Windows/OneDrive — lihat cara mencarinya di
  bagian 6 di bawah).

---

## 5. Python: instalasi & library

**1. Install Python** (jika belum ada):
`https://www.python.org/downloads/` → centang **"Add python.exe to PATH"**
saat instalasi.

**2. Install library yang dibutuhkan:**
```bash
pip install watchdog pillow
```
- `watchdog` → mendeteksi otomatis kalau ada file foto baru muncul di folder
- `pillow` (PIL) → untuk menambahkan border/teks ke foto dan menggabungkan foto

---

## 6. Cari lokasi folder tempat foto tersimpan

Ini langkah yang sering meleset karena Windows/OneDrive kadang
memindahkan folder Pictures ke lokasi tidak terduga (termasuk nama folder
yang di-translate ke bahasa lain, seperti `画像` alih-alih `Pictures`
kalau ada campuran region/bahasa).

Cara paling pasti mencari lokasi foto (ganti `NAMAFILE` dengan nama file
foto hasil test kamu, misal `DSC00256.JPG`):
```bash
where /r C:\ NAMAFILE.JPG
```
Perintah ini akan menyisir seluruh drive C dan menunjukkan path lengkap
di mana file itu berada.

---

## 7. Script Python: `photobox_watcher.py`

Script ini melakukan:
- Memantau folder hasil Imaging Edge Remote terus-menerus
- Setiap foto baru terdeteksi → disalin ke folder kerja (`hasil_photobox`),
  lalu diberi border putih + teks "Photobox Event"
- Setelah 3 foto terkumpul → otomatis digabung jadi satu file vertikal
  (`combined_TIMESTAMP.jpg`)
- Mencoba mencetak foto gabungan (kalau printer tidak terpasang, ini akan
  gagal dengan warning saja — tidak menghentikan program)

**Konfigurasi yang WAJIB disesuaikan** di bagian atas script:
```python
WATCH_FOLDER = r"C:\Users\NAMA_USER_KAMU\OneDrive\画像"   # hasil dari langkah 6
NUM_PHOTOS = 3                                              # jumlah foto per sesi
```

---

## 8. Menjalankan seluruh alur (urutan final)

1. Sambungkan kamera A6000 via USB (mode **PC Remote** sudah aktif)
2. Buka **Imaging Edge Desktop → Remote**, pastikan kamera terdeteksi
3. Buka Command Prompt, masuk ke folder tempat `photobox_watcher.py`
   disimpan, lalu jalankan:
   ```bash
   python photobox_watcher.py
   ```
   Tunggu sampai muncul: `[INFO] Memantau folder: ...`
4. Di aplikasi Imaging Edge Remote, klik tombol shutter (lingkaran merah)
   untuk mengambil foto
5. Perhatikan terminal — setiap foto baru akan muncul log:
   ```
   [FOTO BARU] DSC00003.JPG
   [INFO] Foto ke-1/3 diproses...
   ```
6. Ulangi klik shutter sampai 3 foto (jeda sesuka hati, tidak perlu
   buru-buru)
7. Setelah foto ke-3, otomatis muncul:
   ```
   [INFO] 3 foto lengkap! Menggabungkan...
   [INFO] Gabungan foto tersimpan: hasil_photobox\combined_....jpg
   [INFO] Mencetak foto...
   ```
8. Cek folder **`hasil_photobox`** (dibuat otomatis di folder yang sama
   dengan script) — di situ ada 3 foto individual (sudah ada border) dan
   1 file gabungan

---

## 9. Ringkasan checklist

| # | Item | Keterangan |
|---|------|------------|
| 1 | Kamera Sony A6000 | USB Connection = **PC Remote** |
| 2 | Kabel USB data | Bukan kabel charge-only |
| 3 | Imaging Edge Desktop | Software resmi Sony, fitur **Remote** |
| 4 | Python 3.x | Sudah ditambahkan ke PATH |
| 5 | Library `watchdog` | `pip install watchdog` |
| 6 | Library `pillow` | `pip install pillow` |
| 7 | `photobox_watcher.py` | `WATCH_FOLDER` sudah disesuaikan |
| 8 | Baterai kamera | Terisi cukup, jangan 0% |

Kalau semua poin di atas sudah dilakukan urut, hasil akhirnya adalah foto
otomatis diberi border, digabung, dan dicoba di-print — **tanpa Python
langsung mengontrol rana kamera**, melainkan lewat mekanisme
"folder watching" terhadap output dari Imaging Edge Remote.
