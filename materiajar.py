import os
import telebot
from telebot import types

# Token bot Telegram Anda
API_KEY_TELEGRAM = os.getenv("API_KEY_TELEGRAM")
bot = telebot.TeleBot(API_KEY_TELEGRAM, parse_mode=None)

# Dictionary materi yang sudah diubah
materi_ajar = {
    "id": {
        "1. 5G": {
            "deskripsi": "5G adalah generasi kelima dari teknologi jaringan seluler yang menawarkan kecepatan lebih tinggi, latency lebih rendah, dan kapasitas lebih besar dibandingkan dengan 4G. Teknologi ini memungkinkan koneksi yang lebih stabil untuk perangkat IoT, mendukung aplikasi augmented reality (AR), dan memungkinkan kendaraan otonom.",
            "pdf": "https://drive.google.com/file/d/1zZusPt91YMC7BkY4KxfX5zsOyteudn1B/view?usp=drive_link"  # URL file PDF terkait
        },
        "2. Microwave Link": {
            "deskripsi": "Microwave Link adalah teknologi komunikasi yang menggunakan gelombang mikro untuk mentransmisikan data antara dua titik yang terpisah. Teknologi ini sering digunakan untuk koneksi jarak jauh seperti antara gedung atau antar wilayah.",
            "pdf": "https://drive.google.com/file/d/1-cejM1AaZlparkYqfI0M8alXGCbpiQve/view?usp=drive_link"
        },
        "3. IPv6": {
            "deskripsi": "IPv6 adalah versi terbaru dari Internet Protocol (IP) yang menggantikan IPv4. Dengan panjang alamat 128 bit, IPv6 menyediakan jumlah alamat yang hampir tidak terbatas, memungkinkan koneksi lebih banyak perangkat ke internet.",
            "pdf": "https://drive.google.com/file/d/1WgBJd-oLuwazACpONEvwChBhHyVWoQwD/view?usp=drive_link"
        },
        "4. Serat Optik": {
            "deskripsi": "Serat optik menggunakan cahaya untuk mentransmisikan data, menawarkan kecepatan tinggi dan daya tahan terhadap gangguan elektromagnetik. Teknologi ini banyak digunakan untuk jaringan internet kecepatan tinggi dan komunikasi jarak jauh.",
            "pdf": "https://drive.google.com/file/d/1P0iTIw-73aQSweyYQgxGUnOv0guYtIWR/view?usp=drive_link"
        },
        "5. IoT": {
            "deskripsi": "Internet of Things (IoT) mengacu pada konsep menghubungkan perangkat fisik ke internet untuk saling bertukar data. IoT digunakan dalam berbagai aplikasi seperti smart home, kendaraan pintar, dan sistem industri otomatis.",
            "pdf": "https://drive.google.com/file/d/12n_Vah8X8lGCIZNXZARa1v_rj9MOGcvY/view?usp=drive_link"
        },
        "6. Data Center": {
            "deskripsi": "Data Center adalah fasilitas yang digunakan untuk menyimpan, mengelola, dan mengamankan data dalam jumlah besar. Data Center sering digunakan untuk menyokong layanan cloud computing dan untuk menyediakan ruang server bagi perusahaan.",
            "pdf": "https://drive.google.com/file/d/1dI0ed_M0YEhNBarW4i4GxEAkMrDYhcyc/view?usp=drive_link"
        },
        "7. Cloud Computing": {
            "deskripsi": "Cloud Computing memungkinkan pengguna untuk mengakses aplikasi dan data melalui internet tanpa memerlukan perangkat keras lokal yang besar. Layanan cloud dibagi menjadi IaaS, PaaS, dan SaaS.",
            "pdf": "https://drive.google.com/file/d/1HokrhHdHjijYPT5urI3MMlc1w_N_mC6p/view?usp=drive_link"
        },
        "8. Keamanan Informasi": {
            "deskripsi": "Keamanan informasi melibatkan perlindungan data dari akses yang tidak sah, perubahan, dan kerusakan. Ini mencakup aspek seperti enkripsi, keamanan jaringan, dan perlindungan data sensitif dari serangan siber.",
            "pdf": "https://drive.google.com/file/d/1pnwYWMEeVx3LnEf1x3K0lFLf9oACE0dK/view?usp=sharing"
        }
    },
    "en": {
        "5G": {
            "deskripsi": "5G is the fifth generation of cellular network technology, offering higher speeds, lower latency, and greater capacity compared to 4G. This technology enables more stable connections for IoT devices, supports augmented reality (AR) applications, and facilitates autonomous vehicles.",
            "pdf": "https://drive.google.com/file/d/1zZusPt91YMC7BkY4KxfX5zsOyteudn1B/view?usp=drive_link"
        },
        "Microwave Link": {
            "deskripsi": "A Microwave Link is a communication technology that uses microwave waves to transmit data between two distant points. It is commonly used for long-distance connections such as between buildings or across regions.",
            "pdf": "https://drive.google.com/file/d/1-cejM1AaZlparkYqfI0M8alXGCbpiQve/view?usp=drive_link"
        },
        "IPv6": {
            "deskripsi": "IPv6 is the latest version of the Internet Protocol (IP) that replaces IPv4. With a 128-bit address length, IPv6 provides an almost unlimited number of addresses, enabling more devices to connect to the internet.",
            "pdf": "https://drive.google.com/file/d/1WgBJd-oLuwazACpONEvwChBhHyVWoQwD/view?usp=drive_link"
        },
        "Fiber Optics": {
            "deskripsi": "Fiber optics uses light to transmit data, offering high speed and resistance to electromagnetic interference. This technology is widely used for high-speed internet connections and long-distance communication.",
            "pdf": "https://drive.google.com/file/d/1P0iTIw-73aQSweyYQgxGUnOv0guYtIWR/view?usp=drive_link"
        },
        "IoT": {
            "deskripsi": "The Internet of Things (IoT) refers to the concept of connecting physical devices to the internet for exchanging data. IoT is used in various applications such as smart homes, smart vehicles, and automated industrial systems.",
            "pdf": "https://drive.google.com/file/d/12n_Vah8X8lGCIZNXZARa1v_rj9MOGcvY/view?usp=drive_link"
        },
        "Data Center": {
            "deskripsi": "A Data Center is a facility used to store, manage, and secure large amounts of data. Data Centers are commonly used to support cloud computing services and provide server space for businesses.",
            "pdf": "https://drive.google.com/file/d/1dI0ed_M0YEhNBarW4i4GxEAkMrDYhcyc/view?usp=drive_link"
        },
        "Cloud Computing": {
            "deskripsi": "Cloud Computing allows users to access applications and data over the internet without needing large local hardware. Cloud services are divided into IaaS, PaaS, and SaaS.",
            "pdf": "https://drive.google.com/file/d/1HokrhHdHjijYPT5urI3MMlc1w_N_mC6p/view?usp=drive_link"
        },
        "Information Security": {
            "deskripsi": "Information security involves protecting data from unauthorized access, modification, and damage. It includes aspects such as encryption, network security, and protecting sensitive data from cyberattacks.",
            "pdf": "https://drive.google.com/file/d/1pnwYWMEeVx3LnEf1x3K0lFLf9oACE0dK/view?usp=sharing"
        }
    }
}

