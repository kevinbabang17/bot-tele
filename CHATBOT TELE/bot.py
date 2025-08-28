# -*- coding: utf-8 -*-
import os
import json
import time
import logging
import random
import threading
import requests
from datetime import datetime


from telebot import TeleBot, types, apihelper
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googlesearch import search


# ✅ Aktifkan middleware SEBELUM inisialisasi bot
apihelper.ENABLE_MIDDLEWARE = True
# Tampilkan detail user pada setiap pesan yang masuk
SHOW_USER_EACH_MESSAGE = False  # ⬅️ matikan spam


# Penanda agar detail user hanya tampil sekali per sesi per chat
session_intro_shown = set()


# =========================
# Load Environment
# =========================
load_dotenv()
API_KEY_TELEGRAM = os.getenv("API_KEY_TELEGRAM")
API_KEY_YOUTUBE  = os.getenv("API_KEY_YOUTUBE")
API_KEY_WEATHER  = os.getenv("API_KEY_WEATHER")
CX_GOOGLE        = os.getenv("CX_GOOGLE")


if not API_KEY_TELEGRAM:
    raise RuntimeError("ENV API_KEY_TELEGRAM tidak ditemukan.")


# =========================
# Inisialisasi Bot
# =========================
bot = TeleBot(API_KEY_TELEGRAM, parse_mode=None)


# =========================
# Import Modul Lokal
# =========================
logging.basicConfig(level=logging.INFO)


try:
    import kodeapi as config
    from kodeapi import languages, quotes, daily_tips, foto_paths
except ImportError as e:
    logging.error(f"Error importing kodeapi: {e}")
    raise ImportError("Pastikan modul 'kodeapi' tersedia (languages, quotes, daily_tips, foto_paths).")


try:
    import latihansoal
    from latihansoal import latihan_soal
except ImportError as e:
    logging.error(f"Error importing latihansoal: {e}")
    raise ImportError("Pastikan modul 'latihansoal' tersedia dan mengekspor 'latihan_soal'.")


try:
    import materiajar
    from materiajar import materi_ajar
except ImportError as e:
    logging.error(f"Error importing materiajar: {e}")
    raise ImportError("Pastikan modul 'materiajar' tersedia dan mengekspor 'materi_ajar'.")


try:
    from admin_tools import setup_admin_handlers, simpan_user_nama, muat_user_nama, ADMIN_IDS
except ImportError as e:
    logging.error(f"Error importing admin_tools: {e}")
    raise ImportError("Pastikan modul 'admin_tools' tersedia.")


logging.info("✅ Semua modul lokal berhasil diimpor.")


# =========================
# File JSON
# =========================
PROGRESS_FILE = "progress.json"
LOG_FILE      = "logkeluar.json"
USER_FILE     = "users.json"


# =========================
# Variabel RAM
# =========================
user_nama      = {}
user_language  = {}   # {chat_id: 'id'|'en'}
user_progress  = {}   # {chat_id: {...}}
data_user      = {}
stop_flag      = threading.Event()


# Fallback ikon materi (opsional)
try:
    materi_ikon
except NameError:
    materi_ikon = {
        # "5G": "📶",
        # "Jaringan Komputer": "🖧",
        # "Keamanan": "🛡️",
    }


def get_icon(topik: str) -> str:
    return materi_ikon.get(topik, "📚")


# =========================
# ====== Simpan/Load detail pengguna ke users.json ======
# =========================
# Util Load/Save PROGRESS
# =========================
def load_progress():
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    # kunci chat_id harus int; bila tersimpan string, konversi aman
                    fixed = {}
                    for k, v in data.items():
                        try:
                            fixed[int(k)] = v
                        except:
                            fixed[k] = v
                    return fixed
                return {}
        except json.JSONDecodeError:
            return {}
    return {}


def save_progress(data: dict):
    # simpan dengan kunci string agar konsisten cross-platform
    out = {str(k): v for k, v in data.items()}
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=4, ensure_ascii=False)


def load_users():
    if os.path.exists(USER_FILE):
        try:
            with open(USER_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Kalau file kosong atau bukan dict, pulangkan dict baru
                if not isinstance(data, dict):
                    return {}
                return data
        except json.JSONDecodeError:
            return {}
    return {}


def save_users(data):
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def upgrade_users_schema(data: dict) -> dict:
    """
    Migrasi entry user dari format lama (string nama) ke format dict lengkap.
    Dipanggil sekali saat boot.
    """
    changed = False
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for uid, val in list(data.items()):
        if not isinstance(val, dict):
            # val adalah string nama lama
            nama = str(val)
            try:
                int_uid = int(uid)
            except:
                int_uid = uid  # fallback
            data[uid] = {
                "id": int_uid,
                "is_bot": False,
                "first_name": nama,
                "last_name": None,
                "username": None,
                "language_code": None,
                "first_seen": now,
                "last_seen": now
            }
            changed = True
        else:
            # pastikan kunci wajib ada
            required_keys = ["id", "first_seen", "last_seen"]
            for k in required_keys:
                if k not in val:
                    if k == "id":
                        try:
                            val["id"] = int(uid)
                        except:
                            val["id"] = uid
                    else:
                        val[k] = now
                    changed = True
    if changed:
        save_users(data)
    return data


_users_cache = upgrade_users_schema(load_users())


def remember_user(user):
    """
    Simpan/Update detail pengguna ke users.json:
    - id, username, first_name, last_name, language_code
    - first_seen (set sekali)
    - last_seen (update setiap pesan)
    """
    uid = str(user.id)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


    # Jika record lama berupa string / bukan dict, migrasi di sini juga (safeguard)
    rec = _users_cache.get(uid)
    if not isinstance(rec, dict):
        rec = {
            "id": user.id,
            "is_bot": user.is_bot,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
            "language_code": getattr(user, "language_code", None),
            "first_seen": now,
            "last_seen": now
        }
    else:
        rec["first_name"] = user.first_name
        rec["last_name"] = user.last_name
        rec["username"] = user.username
        rec["language_code"] = getattr(user, "language_code", rec.get("language_code"))
        rec.setdefault("first_seen", now)
        rec["last_seen"] = now


    _users_cache[uid] = rec
    save_users(_users_cache)


def get_user_record(uid: int):
    """Ambil rekaman user dari cache (fallback dict kosong)."""
    return _users_cache.get(str(uid), {}) or {}


def format_user_details(u: dict) -> str:
    """Kembalikan string markdown berisi detail user yang rapi."""
    def v(key, default="-"):
        val = u.get(key)
        return default if (val is None or val == "") else str(val)


    username = v("username", "-")
    if username != "-" and not username.startswith("@"):
        username = "@" + username


    lines = [
        "👤 *Detail Pengguna*",
        f"🆔 ID: `{v('id')}`",
        f"🧾 Username: {username}",
        f"📛 Nama Depan: {v('first_name')}",
        f"📛 Nama Belakang: {v('last_name')}",
        f"🌐 Bahasa Telegram: {v('language_code')}",
        f"⏱️ Pertama Kali: `{v('first_seen')}`",
        f"⏳ Terakhir Aktif: `{v('last_seen')}`",
    ]
    return "\n".join(lines)



# =========================
def tambah_user_nama(user_id, nama):
    """
    Kompatibel schema baru: selalu simpan sebagai dict,
    dan update first_name + timestamps.
    """
    uid = str(user_id)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


    rec = _users_cache.get(uid)
    if not isinstance(rec, dict):
        rec = {
            "id": user_id,
            "is_bot": False,
            "first_name": nama,
            "last_name": None,
            "username": None,
            "language_code": None,
            "first_seen": now,
            "last_seen": now
        }
    else:
        rec["first_name"] = nama
        rec.setdefault("first_seen", now)
        rec["last_seen"] = now


    _users_cache[uid] = rec
    save_users(_users_cache)
    return _users_cache


# =========================
def simpan_log_keluar(chatid, materi, soal_ke, skor):
    waktu = datetime.now().strftime("%A, %d %B %Y pukul %H:%M")
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = {}
    uid = str(chatid)
    if uid not in data:
        data[uid] = []
    data[uid].append({
        "materi": materi,
        "soal_ke": soal_ke,
        "skor": skor,
        "waktu": waktu
    })
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# Load progress awal
user_progress = load_progress()


# =========================
# Admin Handlers
# =========================
setup_admin_handlers(bot, user_nama, user_language, user_progress)


# =========================
# Helper State
# =========================
def is_stopped(message):
    # Izinkan bangun dengan /start atau ▶️ Start
    return stop_flag.is_set() and (message.text not in ('/start', '▶️ Start'))


# =========================
# START / Language
# =========================
@bot.message_handler(commands=['start'])
def command_start(message):
    selamat_datang(message)


@bot.message_handler(func=lambda message: message.text == '▶️ Start')
def manual_restart(message):
    selamat_datang(message)


def selamat_datang(message):
    stop_flag.clear()
    chatid = message.chat.id


    # catat user & update last_seen
    remember_user(message.from_user)


    # 🧹 hapus 'history' user saat masuk kembali
    uid = str(message.from_user.id)
    rec = _users_cache.get(uid, {})
    if isinstance(rec, dict) and 'history' in rec:
        rec.pop('history', None)
        _users_cache[uid] = rec
        save_users(_users_cache)


    # pilih bahasa
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(types.KeyboardButton('🇮🇩 Bahasa Indonesia'), types.KeyboardButton('🇬🇧 English'))
    bot.send_message(chatid, languages['id']['choose_language'], reply_markup=markup)


    # (opsional) tampilkan detail user langsung saat /start
    # (kalau SHOW_USER_EACH_MESSAGE True, sebenarnya ini juga akan tampil dari middleware)
   # tampilkan detail user hanya sekali per sesi
    if message.chat.id not in session_intro_shown:
         rec = get_user_record(message.from_user.id)
    bot.send_message(chatid, format_user_details(rec), parse_mode="Markdown")
    session_intro_shown.add(message.chat.id)




@bot.message_handler(func=lambda message: message.text in ['🇮🇩 Bahasa Indonesia', '🇬🇧 English'])
def set_language(message):
    chatid = message.chat.id
    lang_mapping = {
        '🇮🇩 Bahasa Indonesia': 'id',
        '🇬🇧 English': 'en'
    }
    user_language[chatid] = lang_mapping[message.text]
    lang = user_language[chatid]
    bot.send_message(chatid, languages[lang]['welcome'])
    update_language_buttons(chatid, lang)


def update_language_buttons(chatid, lang):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(
        types.KeyboardButton('🌦 Weather'),
        types.KeyboardButton('📚 Material'),
        types.KeyboardButton('📝 Exercises')
    )
    markup.row(types.KeyboardButton('♻️Join Grup'))
    markup.row(
        types.KeyboardButton('📺 Youtube'),
        types.KeyboardButton('🔎 Google')
    )
    markup.row(
        types.KeyboardButton('📖 Quote'),
        types.KeyboardButton('📊 Final Lesson Report')
    )
    # 🔽 Tambahan tombol ID
    markup.row(types.KeyboardButton('🆔 Show my ID'),
                types.KeyboardButton('🙎‍♂️About Me'),
    )
    markup.row(
        types.KeyboardButton('▶️ Start'),
        types.KeyboardButton('❌ Stop')
    )
    if chatid in ADMIN_IDS:
        markup.row(types.KeyboardButton("⚙️ Admin Menu"))
    bot.send_message(chatid, languages[lang]['choose_option'], reply_markup=markup)


# ==== Handler: Admin Menu ====
@bot.message_handler(func=lambda m: m.text == "⚙️ Admin Menu" and m.from_user.id in ADMIN_IDS)
def admin_menu(message):
    teks = (
        "⚙️ *Menu Admin:*\n\n"
        "✅ Gunakan perintah berikut:\n"
        "/lihatprogres - Lihat progres siswa\n"
        "/logkeluar - Lihat log siswa keluar latihan\n"
        "/resetdata - Reset semua data\n"
    )
    bot.send_message(message.chat.id, teks, parse_mode="Markdown")


# ==== Helper: kirim teks panjang (pecah sesuai limit Telegram) ====
def _send_long_message(chatid, text, parse_mode="Markdown"):
    MAX = 4096
    if len(text) <= MAX:
        bot.send_message(chatid, text, parse_mode=parse_mode)
        return


    # pecah per paragraf/line agar rapi
    chunk, total = [], 0
    for line in text.split("\n"):
        add_len = len(line) + 1  # + newline
        if total + add_len > MAX:
            bot.send_message(chatid, "\n".join(chunk), parse_mode=parse_mode)
            chunk = [line]
            total = add_len
        else:
            chunk.append(line)
            total += add_len
    if chunk:
        bot.send_message(chatid, "\n".join(chunk), parse_mode=parse_mode)


# ==== Admin: /lihatprogres (hanya user yang SUDAH PILIH BAHASA) ====
@bot.message_handler(commands=['lihatprogres'])
def lihat_progres(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "⛔ Perintah ini hanya untuk admin.")
        return


    # Ambil user yang sudah pilih bahasa (kunci user_language)
    aktif_ids = list(user_language.keys())


    # Urutkan by last_seen (jika tersedia di _users_cache), fallback ke uid
    def sort_key(uid):
        rec = _users_cache.get(str(uid), {})
        return (rec.get("last_seen") or ""), uid
    aktif_ids.sort(key=sort_key, reverse=True)


    jumlah_aktif = len(aktif_ids)


    # "Sedang mengerjakan latihan" = punya kunci 'soal'
    sedang_latihan_ids = [uid for uid, rec in user_progress.items()
                          if isinstance(rec, dict) and 'soal' in rec]
    jumlah_latihan = len(sedang_latihan_ids)


    # Susun daftar tampil
    lines = ["👥 *Daftar Pengguna Aktif* (sudah memilih bahasa)", ""]
    if not aktif_ids:
        lines.append("_Belum ada pengguna aktif._")
    else:
        for i, uid in enumerate(aktif_ids, start=1):
            rec = _users_cache.get(str(uid), {})  # dari users.json
            first_name = (rec.get("first_name") or "").strip() or "-"
            last_name  = (rec.get("last_name") or "").strip()
            full_name  = (first_name + (" " + last_name if last_name else "")).strip()
            username   = rec.get("username")
            username_s = f" (@{username})" if username else ""
            last_seen  = rec.get("last_seen") or "-"
            badge_lat  = " • _(sedang latihan)_" if uid in sedang_latihan_ids else ""
            lines.append(f"{i}. *{full_name}*{username_s} — `ID:{uid}`\n   ⏳ Terakhir aktif: `{last_seen}`{badge_lat}")


    lines.append("")
    lines.append(f"📊 Total pengguna aktif: *{jumlah_aktif}*")
    lines.append(f"📝 Sedang mengerjakan latihan: *{jumlah_latihan}*")


    _send_long_message(message.chat.id, "\n".join(lines), parse_mode="Markdown")



# =========================
# ==== Middleware: catat semua user setiap ada pesan ====
@bot.middleware_handler(update_types=['message'])
def _capture_users(bot_instance, message):
    try:
        if message and message.from_user:
            # tetap update users.json (last_seen, dst.)
            remember_user(message.from_user)


            # ⛔ tidak mengirim detail di setiap pesan lagi
            if SHOW_USER_EACH_MESSAGE:
                rec = get_user_record(message.from_user.id)
                bot.send_message(message.chat.id, format_user_details(rec), parse_mode="Markdown")
    except Exception as e:
        logging.debug(f"remember_user skip: {e}")


# =========================
# Misc Handlers
# =========================
@bot.message_handler(func=lambda m: m.text == "🆔 Show my ID")
def show_my_id_button(message):
    remember_user(message.from_user)  # update last_seen
    rec = get_user_record(message.from_user.id)
    bot.send_message(message.chat.id, format_user_details(rec), parse_mode="Markdown")


@bot.message_handler(commands=['myid'])
def send_my_id(message):
    remember_user(message.from_user)  # update last_seen
    rec = get_user_record(message.from_user.id)
    bot.send_message(message.chat.id, format_user_details(rec), parse_mode="Markdown")


# Fungsi untuk menangani menu "About Me"
@bot.message_handler(func=lambda message: message.text == "🙎‍♂️About Me")
def about_me(message):
    if is_stopped(message): return
    chatid = message.chat.id
    lang = user_language.get(chatid, 'id')  # Mendapatkan bahasa yang dipilih
    # Mengirimkan pesan "About Me"
    bot.reply_to(message, languages[lang]['help'])
    
    # Mengirimkan foto jika ada dalam daftar foto_paths
    bot.send_message(chatid, languages[lang]['picture'])
    
    for path in foto_paths:
        try:
            with open(path, 'rb') as photo:
                bot.send_photo(chatid, photo)
        except FileNotFoundError:
            bot.send_message(chatid, f"Foto tidak ditemukan: {path}")
# =========================
# Youtube
# =========================
@bot.message_handler(func=lambda message: message.text == "📺 Youtube")
def handle_youtube_command(message):
    if is_stopped(message): return
    chatid = message.chat.id
    lang = user_language.get(chatid, 'id')
    bot.send_message(chatid, languages[lang]['search_prompt'])
    bot.register_next_step_handler(message, process_youtube_query)


def process_youtube_query(message):
    chatid = message.chat.id
    query = message.text
    search_youtube(query, chatid)


def search_youtube(query, chatid):
    lang = user_language.get(chatid, 'id')
    api_key = API_KEY_YOUTUBE
    try:
        youtube = build("youtube", "v3", developerKey=api_key)
        search_response = youtube.search().list(
            q=query, part="snippet", type="video", maxResults=5
        ).execute()
        video_ids = [item['id']['videoId'] for item in search_response['items']]
        if not video_ids:
            bot.send_message(chatid, languages[lang]['no_results'])
            return
        video_response = youtube.videos().list(
            part="contentDetails,statistics", id=",".join(video_ids)
        ).execute()
        import isodate
        for idx, item in enumerate(search_response['items']):
            video_id = item['id']['videoId']
            snippet = item['snippet']
            stats = video_response['items'][idx]['statistics']
            content = video_response['items'][idx]['contentDetails']
            title = snippet['title']
            channel = snippet['channelTitle']
            published = snippet['publishedAt'].split("T")[0]
            thumbnail = snippet['thumbnails']['high']['url']
            link = f"https://www.youtube.com/watch?v={video_id}"
            duration = isodate.parse_duration(content['duration'])
            minutes, seconds = divmod(int(duration.total_seconds()), 60)
            duration_str = f"{minutes}:{seconds:02d}"
            views = stats.get('viewCount', '0')
            views_str = f"{int(views):,}".replace(",", ".")
            caption = (
                f"🎬 *{title}*\n"
                f"📺 _{channel}_\n"
                f"🕒 Durasi: `{duration_str}`\n"
                f"👁️ Ditonton: `{views_str}` views\n"
                f"📅 Tanggal: `{published}`"
            )
            markup = InlineKeyboardMarkup(row_width=2)
            markup.add(
                InlineKeyboardButton("▶️ Nonton", url=link),
                InlineKeyboardButton("❤️ Suka", callback_data=f"like_{idx}"),
                InlineKeyboardButton("💾 Simpan", callback_data=f"save_{idx}")
            )
            bot.send_photo(chatid, photo=thumbnail, caption=caption, parse_mode='Markdown', reply_markup=markup)
    except Exception as e:
        logging.exception("Error Youtube")
        bot.send_message(chatid, f"❌ Error saat mencari video: {str(e)}")


@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    try:
        if call.data.startswith("like_"):
            bot.answer_callback_query(call.id, "❤️ Terima kasih sudah menyukai video ini!")
        elif call.data.startswith("save_"):
            bot.answer_callback_query(call.id, "💾 Video telah disimpan!")
    except Exception as e:
        bot.answer_callback_query(call.id, f"❌ Error: {str(e)}")


# =========================
# Google Search (sederhana)
# =========================
@bot.message_handler(func=lambda message: message.text == "🔎 Google")
def google_search_handler(message):
    if is_stopped(message): return
    chatid = message.chat.id
    lang = user_language.get(chatid,'id')
    prompt = languages.get(lang, {}).get('search_engine', "Ketik kata kunci untuk mencari di Google:")
    bot.send_message(chatid, prompt)
    bot.register_next_step_handler(message, handle_google_search)


def handle_google_search(message):
    query = message.text
    chatid = message.chat.id
    results = search_google(query, num_results=5)
    lang = user_language.get(chatid, 'id')
    if results:
        response = "\n\n".join([f"{i+1}. [{r['title']}]({r['link']})" for i, r in enumerate(results)])
        bot.send_message(chatid, response, parse_mode='Markdown')
    else:
        bot.send_message(chatid, languages[lang].get('no_results', 'No results found.'))


def search_google(query, num_results=5):
    try:
        out = []
        for result in search(query, num_results=num_results):
            out.append({'title': result, 'link': result})
        return out
    except Exception as e:
        logging.error(f"Google search error: {e}")
        return None


# =========================
# Weather
# =========================
@bot.message_handler(func=lambda message: message.text == "🌦 Weather")
def weather(message):
    if is_stopped(message): return
    chatid = message.chat.id
    lang = user_language.get(chatid, 'id')
    bot.send_message(chatid, "🏙️ " + languages[lang]['enter_city'])
    bot.register_next_step_handler(message, fetch_weather)


def fetch_weather(message):
    chatid = message.chat.id
    lang = user_language.get(chatid, 'id')
    city = message.text
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY_WEATHER}&units=metric"
    try:
        response = requests.get(url, timeout=15)
        data = response.json()
    except Exception as e:
        bot.send_message(chatid, f"❌ Error koneksi cuaca: {e}")
        return
    if data.get('cod') != 200:
        bot.send_message(chatid, "❌ " + languages[lang]['weather_not_found'])
        return
    temperature = data['main']['temp']
    condition = data['weather'][0]['description'].capitalize()
    icon = get_weather_icon(condition.lower())
    message_weather = (
        f"🌤️ *Cuaca di {city.title()}*\n\n"
        f"{icon} Kondisi: *{condition}*\n"
        f"🌡️ Suhu: *{temperature}°C*"
    )
    bot.send_message(chatid, message_weather, parse_mode='Markdown')


def get_weather_icon(condition):
    condition = condition.lower()
    if "clear" in condition or "cerah" in condition:
        return "☀️"
    elif "cloud" in condition or "awan" in condition:
        return "☁️"
    elif "rain" in condition or "hujan" in condition:
        return "🌧️"
    elif "storm" in condition or "badai" in condition:
        return "⛈️"
    elif "snow" in condition or "salju" in condition:
        return "❄️"
    elif "mist" in condition or "kabut" in condition:
        return "🌫️"
    else:
        return "🌈"


# =========================
# LATIHAN SOAL
# =========================
def normalize_label(text: str) -> str:
    if not isinstance(text, str):
        return ""
    t = text.strip()
    # Jika ada ikon/emoji + spasi di depan (contoh: "📚 Topik A")
    if " " in t and len(t) > 2 and not t[0].isalnum():
        return t.split(" ", 1)[1].strip()
    return t


def is_valid_materi_msg(m):
    lang = user_language.get(m.chat.id, 'id')
    materi_map = latihan_soal.get(lang, {})
    txt = m.text or ""
    return (txt in materi_map) or (normalize_label(txt) in materi_map)


@bot.message_handler(func=lambda m: m.text == "📝 Exercises")
def latihan_soal_menu(message):
    if is_stopped(message): return
    chatid = message.chat.id
    lang = user_language.get(chatid, 'id')
    if lang not in latihan_soal or not latihan_soal[lang]:
        bot.send_message(chatid, "⚠️ Latihan soal belum tersedia dalam bahasa yang dipilih.")
        return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for topik in latihan_soal[lang]:
        ikon = get_icon(topik)
        markup.add(types.KeyboardButton(f"{ikon} {topik}"))
    markup.add(types.KeyboardButton("🔙 Kembali Menu Awal"))
    bot.send_message(
        chatid,
        "📝 Pilih *materi soal* yang ingin kamu kerjakan:",
        parse_mode="Markdown",
        reply_markup=markup
    )


@bot.message_handler(func=is_valid_materi_msg)
def pilih_materi(message):
    chatid = message.chat.id
    lang = user_language.get(chatid, 'id')
    raw = message.text or ""
    nama_materi = raw if raw in latihan_soal.get(lang, {}) else normalize_label(raw)
    soal_list = latihan_soal.get(lang, {}).get(nama_materi, [])
    if not soal_list:
        bot.send_message(chatid, "❌ Soal tidak ditemukan untuk materi ini.")
        return
    user_progress[chatid] = {
        "materi": nama_materi,
        "nomor": 0,
        "skor": 0,
        "soal": soal_list,
        "history": user_progress.get(chatid, {}).get("history", [])
    }
    save_progress(user_progress)
    kirim_soal(chatid, lang)


@bot.message_handler(func=lambda m: m.text == "🔁 Kembali ke Materi Soal")
def kembali_ke_materi_dari_soal(message):
    chatid = message.chat.id
    progress = user_progress.get(chatid)
    if not progress or 'materi' not in progress:
        bot.send_message(chatid, "⚠️ Kamu belum memulai latihan.")
        return
    materi = progress.get('materi', '-')
    nomor = progress.get('nomor', 0)
    skor = progress.get('skor', 0)
    try:
        simpan_log_keluar(chatid, materi, nomor + 1, skor)
    except Exception:
        pass
    history = progress.get("history", [])
    last_materi = progress.get("materi", None)
    last_lang = user_language.get(chatid, 'id')
    user_progress[chatid] = {
        "history": history,
        "last_materi": last_materi,
        "last_lang": last_lang
    }
    save_progress(user_progress)
    bot.send_message(chatid, "🔁 Kamu kembali ke menu materi.")
    latihan_soal_menu(message)


def kirim_soal(chatid, lang):
    progress = user_progress.get(chatid)
    if not progress or 'soal' not in progress:
        bot.send_message(chatid, "❌ Tidak ada progres ditemukan.")
        return
    nomor = progress.get('nomor', 0)
    soal_list = progress.get('soal', [])
    if nomor >= len(soal_list):
        skor = progress.get('skor', 0)
        materi = progress.get('materi', '-')
        history = progress.get("history", [])
        history.append({
            "materi": materi,
            "skor": f"{skor}/{len(soal_list)}",
            "waktu": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        user_progress[chatid] = {
            "history": history,
            "last_materi": materi,
            "last_lang": lang
        }
        save_progress(user_progress)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(types.KeyboardButton("🔁 Ulangi Materi"), types.KeyboardButton("🔙 Kembali Menu Awal"))
        bot.send_message(
            chatid,
            f"✅ Latihan selesai!\n📚 Materi: *{materi}*\n🎯 Skor akhir: *{skor}/{len(soal_list)}*",
            parse_mode="Markdown",
            reply_markup=markup
        )
        return


    soal_data = soal_list[nomor]
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for opsi in soal_data.get('pilihan', []):
        markup.add(types.KeyboardButton(opsi))
    markup.add(types.KeyboardButton("🔁 Kembali ke Materi Soal"))
    markup.add(types.KeyboardButton("🔙 Kembali Menu Awal"))
    bot.send_message(
        chatid,
        f"❓ Soal {nomor + 1}: {soal_data.get('soal', '-')}",
        reply_markup=markup
    )
    bot.register_next_step_handler_by_chat_id(chatid, cek_jawaban)


def cek_jawaban(message):
    chatid = message.chat.id
    jawaban = (message.text or "").strip()
    progress = user_progress.get(chatid)
    if jawaban == "🔁 Kembali ke Materi Soal":
        kembali_ke_materi_dari_soal(message)
        return
    elif jawaban == "🔙 Kembali Menu Awal":
        user_progress.pop(chatid, None)
        save_progress(user_progress)
        kembali_ke_menu(message)
        return
    if not progress or 'soal' not in progress:
        bot.send_message(chatid, "⚠️ Progres tidak valid. Silakan ulang latihan.")
        user_progress.pop(chatid, None)
        save_progress(user_progress)
        return
    soal_list = progress['soal']
    nomor = progress.get('nomor', 0)
    skor = progress.get('skor', 0)
    if nomor >= len(soal_list):
        kirim_soal(chatid, user_language.get(chatid, 'id'))
        return
    jawaban_benar = soal_list[nomor].get('jawaban')
    if jawaban == jawaban_benar:
        bot.send_message(chatid, "✅ Jawaban benar!")
        skor += 1
    else:
        bot.send_message(chatid, f"❌ Jawaban salah!\n✅ Jawaban yang benar: {jawaban_benar}")
    user_progress[chatid]['nomor'] = nomor + 1
    user_progress[chatid]['skor'] = skor
    save_progress(user_progress)
    kirim_soal(chatid, user_language.get(chatid, 'id'))


@bot.message_handler(func=lambda m: m.text == "🔁 Ulangi Materi")
def ulangi_materi(message):
    chatid = message.chat.id
    if chatid in user_progress and 'last_materi' in user_progress[chatid]:
        materi_nm = user_progress[chatid]['last_materi']
        lang = user_progress[chatid].get('last_lang', 'id')
        soal_list = latihan_soal.get(lang, {}).get(materi_nm, [])
        if not soal_list:
            bot.send_message(chatid, "❌ Soal tidak ditemukan untuk materi ini.")
            return
        history = user_progress[chatid].get('history', [])
        user_progress[chatid] = {
            'materi': materi_nm,
            'nomor': 0,
            'skor': 0,
            'soal': soal_list,
            'last_materi': materi_nm,
            'last_lang': lang,
            'history': history
        }
        save_progress(user_progress)
        kirim_soal(chatid, lang)
    else:
        bot.send_message(chatid, "⚠️ Tidak ditemukan materi sebelumnya untuk diulang.")


# =========================
# Fungsi untuk menampilkan menu materi
@bot.message_handler(func=lambda m: m.text == "📚 Material")
def materi_ajar_menu(message):
    if is_stopped(message): return
    chatid = message.chat.id
    lang = user_language.get(chatid, 'id')


    # Pastikan materi tersedia dalam bahasa yang dipilih
    if lang not in materi_ajar or not materi_ajar[lang]:
        bot.send_message(chatid, "⚠️ Materi belum tersedia dalam bahasa yang dipilih.")
        return


    # Menampilkan tombol topik materi
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for topik in materi_ajar[lang]:
        markup.add(types.KeyboardButton(topik))  # Menambahkan tombol materi
    markup.add(types.KeyboardButton("🔙 Kembali Menu Awal"))


    bot.send_message(
        chatid,
        "📚 Pilih *materi* yang ingin kamu pelajari:",
        parse_mode="Markdown",
        reply_markup=markup
    )


# Fungsi untuk menampilkan deskripsi dan PDF materi
@bot.message_handler(func=lambda m: m.text in materi_ajar.get(user_language.get(m.chat.id, 'id'), {}))
def tampilkan_materi(message):
    chatid = message.chat.id
    lang = user_language.get(chatid, 'id')
    topik = message.text
    
    if topik in materi_ajar[lang]:
        materi = materi_ajar[lang][topik]
        deskripsi = materi["deskripsi"]
        pdf_url = materi.get("pdf", None)  # Ambil URL PDF jika ada
        
        # Kirim deskripsi materi
        bot.send_message(chatid, f"📖 *{topik}*\n\n{deskripsi}", parse_mode="Markdown")
        
        # Jika ada PDF, kirimkan link download
        if pdf_url:
            bot.send_message(chatid, f"📄 *Download PDF Materi*: {pdf_url}")
        else:
            bot.send_message(chatid, "⚠️ Tidak ada file PDF untuk materi ini.")
        
        # Kirim tombol navigasi untuk kembali
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("🔁 Kembali ke Materi Ajar"))
        markup.add(types.KeyboardButton("🔙 Kembali Menu Awal"))
        bot.send_message(chatid, "Pilih aksi berikut:", reply_markup=markup)
    else:
        bot.send_message(chatid, "⚠️ Materi tidak ditemukan.")
        return


# Fungsi untuk kembali ke menu materi
@bot.message_handler(func=lambda m: m.text == "🔁 Kembali ke Materi Ajar")
def kembali_ke_materi(message):
    if is_stopped(message): return
    chatid = message.chat.id
    lang = user_language.get(chatid, 'id')
    
    if lang not in materi_ajar or not materi_ajar[lang]:
        bot.send_message(chatid, "⚠️ Materi tidak ditemukan dalam bahasa yang kamu pilih.")
        return
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for topik in materi_ajar[lang]:
        markup.add(types.KeyboardButton(topik))  # Menambahkan tombol topik
    markup.add(types.KeyboardButton("🔙 Kembali Menu Awal"))
    
    bot.send_message(
        chatid,
        "📚 Pilih *materi* yang ingin kamu pelajari:",
        parse_mode="Markdown",
        reply_markup=markup
    )


# =========================
# Laporan Akhir
# =========================
@bot.message_handler(func=lambda m: m.text == "📊 Final Lesson Report")
def laporan_akhir(message):
    if is_stopped(message): return
    chatid = message.chat.id
    lang = user_language.get(chatid, 'id')


    laporan = "📊 *Laporan Akhir Pembelajaran*\n\n"
    history = user_progress.get(chatid, {}).get("history", [])


    if not history:
        laporan += "Belum ada data latihan yang diselesaikan."
    else:
        for h in history:
            laporan += f"📚 Materi: {h['materi']}\n"
            laporan += f"📝 Skor: {h['skor']}\n"
            laporan += f"🕒 Waktu: {h['waktu']}\n\n"


    # Tambah tombol hapus history
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("🧹 Hapus History"))
    markup.add(types.KeyboardButton("🔙 Kembali Menu Awal"))


    bot.send_message(chatid, laporan, parse_mode="Markdown", reply_markup=markup)


@bot.message_handler(func=lambda m: m.text == "🧹 Hapus History")
def hapus_history(message):
    chatid = message.chat.id
    if chatid in user_progress:
        user_progress[chatid]["history"] = []
        save_progress(user_progress)
        bot.send_message(chatid, "🧹 History latihan berhasil dihapus.")
    else:
        bot.send_message(chatid, "⚠️ Tidak ada history untuk dihapus.")



# =========================
# Grup
# =========================
@bot.message_handler(func=lambda message: message.text == "♻️Join Grup")
def menu_grup_telegram(message):
    if is_stopped(message): return
    chatid = message.chat.id
    grup_link = "https://t.me/+U4OapIx8TLU1ZjY1"  # Ganti dengan link grup kamu
    teks = (
        "📣 *Grup Diskusi Belajar Sudah Dibuka!* 🎉\n\n"
        "Gabung yuk kalau ingin:\n"
        "🔹 Tanya-jawab soal & materi\n"
        "🔹 Dapetin tips belajar \n"
        "🔹 Diskusi bareng teman & guru\n"
        "🔹 Update fitur & info penting\n\n"
        "🛡️ *Catatan:* Grup ini bersifat _privat_.\n"
        "Hanya siswa yang menerima link ini yang bisa bergabung.\n"
        "Jangan sebarkan link ini ke luar ya!\n\n"
        f"👉 Klik di sini untuk gabung: {grup_link}"
    )
    bot.send_message(chatid, teks, parse_mode="Markdown")


# =========================
# Quote & Tip
# =========================
@bot.message_handler(commands=['quote'])
def daily_quote(message):
    if is_stopped(message): return
    chatid = message.chat.id
    lang = user_language.get(chatid, 'id')
    quote = random.choice(quotes[lang])
    bot.send_message(chatid, languages[lang]['quote'].format(quote))


@bot.message_handler(func=lambda message: message.text == "📖 Quote")
def daily_tip_handler(message):
    if is_stopped(message): return
    chatid = message.chat.id
    lang = user_language.get(chatid, 'id')
    tip = random.choice(daily_tips[lang])
    bot.send_message(chatid, languages[lang]['daily_tip'].format(tip))


# =========================
# Stop
# =========================
@bot.message_handler(func=lambda message: message.text == "❌ Stop")
def stop_bot(message):
    if is_stopped(message): return
    chatid = message.chat.id
    stop_flag.set()
    # reset penanda agar saat start lagi, detail ditampilkan lagi
    session_intro_shown.discard(chatid)
    bot.send_message(chatid, languages[user_language.get(chatid, 'id')]['bot_stopped'])


# =========================
# Kembali ke Menu Awal
# =========================
@bot.message_handler(func=lambda m: m.text == "🔙 Kembali Menu Awal")
def kembali_ke_menu(message):
    chatid = message.chat.id
    lang = user_language.get(chatid, 'id')
    update_language_buttons(chatid, lang)


# =========================
# Fallback
# =========================
@bot.message_handler(func=lambda message: True)
def fallback_handler(message):
    chatid = message.chat.id
    lang = user_language.get(chatid, 'id')
    if stop_flag.is_set():
        if (message.text or "").strip() in ("/start", "▶️ Start"):
            selamat_datang(message)
        else:
            bot.send_message(chatid, "⛔ Bot sedang dihentikan.\nSilakan ketuk tombol ▶️ Start atau /start untuk memulai kembali.")
        return
    if chatid not in user_language:
        bot.send_message(chatid, "⚠️ Silakan pilih bahasa terlebih dahulu dengan mengetuk salah satu opsi bahasa setelah ▶️ Start.")
        return
    bot.send_message(chatid, f"⚠️ {languages[lang]['choose_option']}")


# =========================
# Runner dengan Backoff
# =========================
def run_bot():
    backoff = 1.0
    while not stop_flag.is_set():
        try:
            bot.polling(
                none_stop=True,
                skip_pending=True,
                timeout=20,
                long_polling_timeout=20
            )
            backoff = 1.0  # reset jika sukses
        except Exception as e:
            logging.error(f"Polling error: {e}")
            time.sleep(backoff)
            backoff = min(backoff * 2, 60)


# =========================
# Main
# =========================
if __name__ == '__main__':
    print("🤖 Bot sedang berjalan...")
    run_bot()
