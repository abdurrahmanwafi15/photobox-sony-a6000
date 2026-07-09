"""
PHOTOBOX - VERSI SONY A6000 (via Imaging Edge Remote)
======================================================
Cara kerja:
1. Kamu klik tombol shutter (lingkaran merah) di aplikasi Imaging Edge Remote
2. Kamera A6000 ambil foto, otomatis tersimpan ke folder Pictures
3. Script ini terus "mengintip" folder Pictures
4. Begitu ada file foto BARU muncul -> otomatis diproses:
   - dikasih border + teks "Photobox Event"
   - dihitung sampai 3 foto -> digabung jadi satu
   - foto terakhir/gabungan di-print

CARA PAKAI:
1. pip install watchdog pillow
2. Sesuaikan WATCH_FOLDER di bawah (folder Pictures kamu)
3. Jalankan: python photobox_watcher.py
4. Buka Imaging Edge Remote, klik shutter 3x (boleh jeda santai)
5. Tekan Ctrl+C di terminal buat berhenti
"""

import os
import time
import shutil
import subprocess
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ================== KONFIGURASI ==================
# Ganti sesuai lokasi folder tempat Imaging Edge menyimpan foto
WATCH_FOLDER = r"C:\Users\NamaKamu\Pictures"

SAVE_DIR = "hasil_photobox"          # folder hasil olahan (dibuat di folder script ini)
NUM_PHOTOS = 3                        # jumlah foto per sesi sebelum digabung & print
VALID_EXT = (".jpg", ".jpeg")         # ekstensi yang dianggap "foto baru"
# ===================================================

os.makedirs(SAVE_DIR, exist_ok=True)


def add_frame(photo_path):
    """Tambah border putih + teks di foto."""
    img = Image.open(photo_path)

    border_size = 50
    framed = Image.new(
        "RGB",
        (img.width + border_size * 2, img.height + border_size * 2),
        "white",
    )
    framed.paste(img, (border_size, border_size))

    draw = ImageDraw.Draw(framed)
    text = "Photobox Event"

    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except Exception:
        font = ImageFont.load_default()

    draw.text((50, framed.height - 60), text, fill="black", font=font)
    framed.save(photo_path)
    return photo_path


def combine_photos(photo_list, save_dir=SAVE_DIR):
    """Gabung beberapa foto jadi satu file vertikal."""
    images = [Image.open(p) for p in photo_list]

    width = max(img.width for img in images)
    total_height = sum(img.height for img in images)

    combined = Image.new("RGB", (width, total_height), "white")

    y_offset = 0
    for img in images:
        combined.paste(img, (0, y_offset))
        y_offset += img.height

    output_path = os.path.join(save_dir, f"combined_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
    combined.save(output_path)
    print(f"[INFO] Gabungan foto tersimpan: {output_path}")
    return output_path


def print_photo(photo_path):
    print("[INFO] Mencetak foto...")
    try:
        if os.name == "nt":
            os.startfile(photo_path, "print")
        else:
            subprocess.run(["lp", photo_path], check=True)
    except Exception as e:
        print(f"[WARN] Print gagal (mungkin tidak ada printer terpasang): {e}")


class PhotoHandler(FileSystemEventHandler):
    """Dipanggil otomatis setiap ada file baru muncul di WATCH_FOLDER."""

    def __init__(self):
        self.session_photos = []

    def on_created(self, event):
        if event.is_directory:
            return

        filepath = event.src_path
        filename = os.path.basename(filepath)

        if not filename.lower().endswith(VALID_EXT):
            return

        # Tunggu sebentar, pastikan file selesai ditulis (belum "locked")
        time.sleep(1.5)

        print(f"\n[FOTO BARU] {filename}")

        # Copy foto ke folder kerja kita, biar file asli di Pictures tidak diubah
        dest_path = os.path.join(SAVE_DIR, filename)
        try:
            shutil.copy2(filepath, dest_path)
        except Exception as e:
            print(f"[ERROR] Gagal menyalin file: {e}")
            return

        add_frame(dest_path)
        self.session_photos.append(dest_path)

        sisa = NUM_PHOTOS - len(self.session_photos)
        if sisa > 0:
            print(f"[INFO] Foto ke-{len(self.session_photos)}/{NUM_PHOTOS} diproses. "
                  f"Ambil {sisa} foto lagi di Imaging Edge Remote...")
        else:
            print(f"[INFO] {NUM_PHOTOS} foto lengkap! Menggabungkan...")
            combined = combine_photos(self.session_photos)
            print_photo(combined)
            print("[INFO] Sesi selesai. Menunggu foto baru untuk sesi berikutnya...\n")
            self.session_photos = []  # reset buat sesi berikutnya


def main():
    if not os.path.isdir(WATCH_FOLDER):
        raise RuntimeError(
            f"Folder tidak ditemukan: {WATCH_FOLDER}\n"
            f"Cek lagi WATCH_FOLDER di bagian atas script ini."
        )

    print(f"[INFO] Memantau folder: {WATCH_FOLDER}")
    print(f"[INFO] Ambil foto lewat Imaging Edge Remote, script ini otomatis memproses.")
    print(f"[INFO] Tekan Ctrl+C untuk berhenti.\n")

    handler = PhotoHandler()
    observer = Observer()
    observer.schedule(handler, WATCH_FOLDER, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n[INFO] Berhenti memantau folder.")
    observer.join()


if __name__ == "__main__":
    main()
