import json
import os
from datetime import datetime
from telebot import types

# === Konstanta Admin & File ===
ADMIN_IDS = [7242962539]  # Ganti ID admin sesuai kebutuhan
USER_FILE = "users.json"

# === Fungsi: Muat dan Simpan Data User ===
def muat_user_nama():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def simpan_user_nama(user_nama):
    with open(USER_FILE, "w") as f:
        json.dump(user_nama, f, indent=4)

def tambah_user_nama(user_id, nama):
    user_id = str(user_id)
    data = muat_user_nama()
    data[user_id] = nama
    simpan_user_nama(data)

# === Fungsi: Setup Handler Admin ===
def setup_admin_handlers(bot, user_nama, user_language, user_progress):

    # === /lihatprogres: Menampilkan progres siswa ===
    @bot.message_handler(commands=["lihatprogres"])
    def lihat_progres(message):
        if message.from_user.id not in ADMIN_IDS:
            return

        file_path = "progress.json"
        if not os.path.exists(file_path):
            bot.send_message(message.chat.id, "⚠️ File `progress.json` tidak ditemukan.")
            return

        try:
            with open(file_path, "r") as f:
                data = json.load(f)
        except Exception as e:
            bot.send_message(message.chat.id, f"⚠️ Gagal membaca progress.json:\n{str(e)}")
            return

        teks = "📊 *Progres Siswa Saat Ini:*\n\n"
        kosong = True

        for uid, progress in data.items():
            if isinstance(progress, dict) and 'materi' in progress:
                kosong = False
                nama = user_nama.get(str(uid), "Tidak diketahui")
                teks += (
                    f"👤 *{nama}* (`{uid}`)\n"
                    f"📚 Materi: *{progress['materi']}*\n"
                    f"❓ Soal Ke: *{progress['nomor'] + 1}*\n"
                    f"✅ Skor: *{progress['skor']}*\n\n"
                )

        if kosong:
            teks += "_Tidak ada siswa yang sedang mengerjakan._"

        bot.send_message(message.chat.id, teks, parse_mode="Markdown")

    # === /logkeluar: Menampilkan siswa yang keluar sebelum selesai ===
    @bot.message_handler(commands=["logkeluar"])
    def lihat_log_keluar(message):
        if message.from_user.id not in ADMIN_IDS:
            return

        file_path = "logkeluar.json"
        if not os.path.exists(file_path):
            bot.send_message(message.chat.id, "⚠️ File `logkeluar.json` tidak ditemukan.")
            return

        try:
            with open(file_path, "r") as f:
                data = json.load(f)
        except Exception as e:
            bot.send_message(message.chat.id, f"⚠️ Gagal membaca logkeluar.json:\n{str(e)}")
            return

        teks = "📄 *Log Siswa Keluar Sebelum Selesai:*\n\n"
        kosong = True

        for uid, logs in data.items():
            if isinstance(logs, list) and logs:
                kosong = False
                nama = user_nama.get(str(uid), "Tidak diketahui")
                for log in logs:
                    teks += (
                        f"👤 *{nama}* (`{uid}`)\n"
                        f"📚 Materi: {log['materi']}\n"
                        f"❓ Soal Ke: {log['soal_ke']}\n"
                        f"✅ Skor: {log['skor']}\n"
                        f"⏰ Waktu: {log['waktu']}\n\n"
                    )

        if kosong:
            teks += "_Tidak ada data siswa yang keluar latihan._"

        bot.send_message(message.chat.id, teks, parse_mode="Markdown")

    # === /resetdata: Hapus semua data dari RAM & file JSON ===
    @bot.message_handler(commands=["resetdata"])
    def reset_data_command(message):
        if message.from_user.id not in ADMIN_IDS:
            bot.send_message(message.chat.id, "⛔ Kamu tidak punya izin untuk perintah ini.")
            return

        for file in ["progress.json", "logkeluar.json", "users.json"]:
            if os.path.exists(file):
                os.remove(file)

        user_nama.clear()
        user_language.clear()
        user_progress.clear()

        bot.send_message(message.chat.id, "✅ Semua data berhasil dihapus (RAM + file).")
