"""
PHOTOBOX - VERSI SONY A6000 (via Imaging Edge Remote) + COUNTDOWN
===================================================================
Cara kerja:
1. Jalankan script ini, tekan ENTER kapan siap mulai sesi foto
2. Script menghitung mundur 3-2-1 di terminal
3. Begitu hitungan sampai "AMBIL FOTO SEKARANG!", KLIK tombol shutter
   (lingkaran merah) di Imaging Edge Remote
4. Kamera ambil foto, otomatis tersimpan ke folder yang dipantau
5. Script otomatis mendeteksi foto baru itu -> diberi border + teks
6. Diulang sampai NUM_PHOTOS foto terkumpul -> digabung jadi satu -> print

CATATAN: Python tidak bisa memicu shutter kamera secara langsung
(tidak ada API resmi untuk itu), jadi klik shutter tetap manual -
countdown ini cuma kasih aba-aba supaya waktunya pas.

CARA PAKAI:
1. pip install watchdog pillow
2. Sesuaikan WATCH_FOLDER di bawah
3. Jalankan: python photobox_watcher.py
4. Ikuti instruksi di terminal
"""

import os
import time
import shutil
import subprocess
import queue
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ================== KONFIGURASI ==================
WATCH_FOLDER = r"C:\Users\MyBook Hype AMD\OneDrive\画像"   # ganti sesuai folder kamu

SAVE_DIR = "hasil_photobox"
NUM_PHOTOS = 3
VALID_EXT = (".jpg", ".jpeg")
COUNTDOWN_SECONDS = 3
PHOTO_WAIT_TIMEOUT = 30   # detik, berapa lama nunggu foto muncul sebelum dianggap gagal
# ===================================================

os.makedirs(SAVE_DIR, exist_ok=True)

# Queue buat komunikasi antara "pengintip folder" (thread background)
# dengan alur utama (yang ngatur countdown)
new_photo_queue = queue.Queue()


def add_frame(photo_path):
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
    images = [Image.open(p) for p in photo_list]

    width = max(img.width for img in images)
    total_height = sum(img.height for img in images)

    combined = Image.new("RGB", (width, total_height), "white")

    y_offset = 0
    for img in images:
        combined.paste(img, (0, y_offset))
        y_offset += img.height

    output_path = os.path.join(
        save_dir, f"combined_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    )
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
    """Setiap ada file foto baru muncul di WATCH_FOLDER, taruh ke queue."""

    def on_created(self, event):
        if event.is_directory:
            return

        filepath = event.src_path
        filename = os.path.basename(filepath)

        if not filename.lower().endswith(VALID_EXT):
            return

        time.sleep(1.5)  # tunggu file selesai ditulis
        new_photo_queue.put(filepath)


def countdown(seconds):
    for i in range(seconds, 0, -1):
        print(f"{i}...")
        time.sleep(1)
    print(">>> AMBIL FOTO SEKARANG! (klik shutter di Imaging Edge Remote) <<<")


def photo_session():
    session_photos = []

    for i in range(1, NUM_PHOTOS + 1):
        input(f"\nFoto ke-{i}/{NUM_PHOTOS} — tekan ENTER kalau sudah siap...")
        countdown(COUNTDOWN_SECONDS)

        print("[INFO] Menunggu foto masuk dari kamera...")
        try:
            filepath = new_photo_queue.get(timeout=PHOTO_WAIT_TIMEOUT)
        except queue.Empty:
            print(f"[WARN] Tidak ada foto baru terdeteksi dalam {PHOTO_WAIT_TIMEOUT} detik. "
                  f"Pastikan sudah klik shutter di Imaging Edge Remote. Foto ini dilewati.")
            continue

        filename = os.path.basename(filepath)
        dest_path = os.path.join(SAVE_DIR, filename)

        try:
            shutil.copy2(filepath, dest_path)
        except Exception as e:
            print(f"[ERROR] Gagal menyalin file: {e}")
            continue

        add_frame(dest_path)
        session_photos.append(dest_path)
        print(f"[INFO] Foto ke-{i} berhasil diproses: {filename}")

    if session_photos:
        print(f"\n[INFO] {len(session_photos)} foto terkumpul! Menggabungkan...")
        combined = combine_photos(session_photos)
        print_photo(combined)
    else:
        print("[WARN] Tidak ada foto yang berhasil diambil di sesi ini.")

    print("[INFO] Sesi selesai.\n")


def main():
    if not os.path.isdir(WATCH_FOLDER):
        raise RuntimeError(
            f"Folder tidak ditemukan: {WATCH_FOLDER}\n"
            f"Cek lagi WATCH_FOLDER di bagian atas script ini."
        )

    print(f"[INFO] Memantau folder: {WATCH_FOLDER}")

    handler = PhotoHandler()
    observer = Observer()
    observer.schedule(handler, WATCH_FOLDER, recursive=False)
    observer.start()

    try:
        while True:
            print("\n=== SESI FOTO BARU ===")
            print("Buka Imaging Edge Remote dan pastikan kamera sudah terhubung.")
            mulai = input("Tekan ENTER untuk mulai sesi (atau ketik 'q' lalu ENTER untuk keluar): ")
            if mulai.strip().lower() == "q":
                break
            photo_session()
    except KeyboardInterrupt:
        pass
    finally:
        observer.stop()
        observer.join()
        print("\n[INFO] Program berhenti.")


if __name__ == "__main__":
    main()
