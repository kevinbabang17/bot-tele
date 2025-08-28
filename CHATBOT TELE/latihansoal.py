import random
import re
from copy import deepcopy

# ===================== DATA =====================

latihan_soal = {
    'id': {
        '5G': [
            {
                'soal': 'Apa keuntungan utama teknologi 5G dibandingkan dengan 4G?',
                'pilihan': ['a. Kecepatan lebih tinggi dan latency lebih rendah', 'b. Keamanan lebih tinggi', 'c. Penggunaan bandwidth lebih efisien', 'd. Tidak memerlukan perangkat keras tambahan'],
                'jawaban': 'a. Kecepatan lebih tinggi dan latency lebih rendah',
                'keterangan': '5G dirancang untuk throughput sangat tinggi dan latensi sangat rendah sehingga cocok untuk aplikasi real-time.'
            },
            {
                'soal': '5G dapat digunakan untuk...',
                'pilihan': ['a. Menyediakan koneksi nirkabel dengan kecepatan tinggi dan latency rendah', 'b. Menghubungkan perangkat IoT secara lokal', 'c. Menyimpan data dalam Data Center', 'd. Meningkatkan keamanan di jaringan Wi-Fi'],
                'jawaban': 'a. Menyediakan koneksi nirkabel dengan kecepatan tinggi dan latency rendah'
            },
            {
                'soal': 'Apa yang dimaksud dengan low latency dalam konteks 5G?',
                'pilihan': ['a. Waktu tunggu yang sangat singkat antara pengiriman dan penerimaan data', 'b. Kemampuan untuk menghubungkan lebih banyak perangkat', 'c. Pengurangan jumlah server di Data Center', 'd. Kecepatan transmisi yang lebih cepat'],
                'jawaban': 'a. Waktu tunggu yang sangat singkat antara pengiriman dan penerimaan data'
            }
        ],
        'Microwave Link': [
            {
                'soal': 'Teknologi Microwave Link digunakan untuk...',
                'pilihan': ['a. Mengirimkan data dalam bentuk gelombang mikro antar perangkat', 'b. Menyambungkan perangkat IoT ke jaringan', 'c. Menyimpan data secara online di Cloud', 'd. Menyediakan akses internet untuk rumah tangga'],
                'jawaban': 'a. Mengirimkan data dalam bentuk gelombang mikro antar perangkat'
            },
            {
                'soal': 'Keuntungan utama dari Microwave Link adalah...',
                'pilihan': ['a. Kecepatan transmisi yang tinggi untuk jarak jauh', 'b. Pengiriman data dengan teknologi nirkabel', 'c. Tidak terpengaruh cuaca buruk', 'd. Memiliki bandwidth terbatas'],
                'jawaban': 'a. Kecepatan transmisi yang tinggi untuk jarak jauh'
            },
            {
                'soal': 'Microwave Link biasanya digunakan dalam...',
                'pilihan': ['a. Koneksi jaringan lokal', 'b. Jaringan jarak jauh, seperti koneksi antar gedung atau wilayah', 'c. Penyimpanan data di server', 'd. Pengaturan perangkat IoT di rumah pintar'],
                'jawaban': 'b. Jaringan jarak jauh, seperti koneksi antar gedung atau wilayah'
            }
        ],
        'IPv6': [
            {
                'soal': 'IPv6 dikembangkan untuk menggantikan IPv4 karena...',
                'pilihan': ['a. IPv4 kekurangan alamat IP', 'b. IPv6 lebih aman daripada IPv4', 'c. IPv4 mendukung kecepatan lebih tinggi', 'd. IPv4 lebih mudah dikelola'],
                'jawaban': 'a. IPv4 kekurangan alamat IP'
            },
            {
                'soal': 'Berapa panjang alamat IP pada IPv6?',
                'pilihan': ['a. 32 bit', 'b. 128 bit', 'c. 64 bit', 'd. 256 bit'],
                'jawaban': 'b. 128 bit'
            },
            {
                'soal': 'Salah satu keuntungan IPv6 adalah...',
                'pilihan': ['a. Alamat IP yang hampir tidak terbatas', 'b. Kecepatan transmisi yang lebih tinggi', 'c. Kemampuan untuk menghubungkan lebih banyak perangkat ke jaringan', 'd. Tidak memerlukan DNS'],
                'jawaban': 'a. Alamat IP yang hampir tidak terbatas'
            }
        ],
        'Serat Optik': [
            {
                'soal': 'Serat optik mentransmisikan data menggunakan...',
                'pilihan': ['a. Gelombang mikro', 'b. Cahaya', 'c. Arus listrik', 'd. Gelombang radio'],
                'jawaban': 'b. Cahaya'
            },
            {
                'soal': 'Keuntungan utama penggunaan serat optik dalam jaringan adalah...',
                'pilihan': ['a. Kecepatan tinggi dan daya tahan terhadap gangguan elektromagnetik', 'b. Harga yang sangat murah', 'c. Mudah dipasang dan ringan', 'd. Dapat mentransmisikan data dalam jarak sangat jauh tanpa pemeliharaan'],
                'jawaban': 'a. Kecepatan tinggi dan daya tahan terhadap gangguan elektromagnetik'
            },
            {
                'soal': 'Serat optik umumnya digunakan untuk...',
                'pilihan': ['a. Koneksi jaringan internet yang cepat dan stabil', 'b. Menyimpan data di Data Center', 'c. Menghubungkan perangkat IoT', 'd. Menggunakan koneksi nirkabel'],
                'jawaban': 'a. Koneksi jaringan internet yang cepat dan stabil'
            }
        ],
        'IoT': [
            {
                'soal': 'Apa yang dimaksud dengan Internet of Things (IoT)?',
                'pilihan': ['a. Menghubungkan perangkat fisik ke internet untuk saling bertukar data', 'b. Menyimpan data di cloud secara aman', 'c. Menggunakan jaringan kabel untuk transmisi data', 'd. Mengontrol perangkat komputer secara jarak jauh'],
                'jawaban': 'a. Menghubungkan perangkat fisik ke internet untuk saling bertukar data'
            },
            {
                'soal': 'Salah satu tantangan utama dalam implementasi IoT adalah...',
                'pilihan': ['a. Keamanan dan privasi data', 'b. Penggunaan bandwidth yang rendah', 'c. Koneksi kabel yang berlebihan', 'd.Jumlah perangkat yang terbatas'],
                'jawaban': 'a. Keamanan dan privasi data'
            },
            {
                'soal': 'IoT banyak digunakan dalam...',
                'pilihan': ['a. Smart home (rumah pintar) untuk mengontrol perangkat elektronik', 'b. Penyimpanan data di Data Center', 'c. Keamanan jaringan 5G', 'd. Pengiriman data antar perangkat menggunakan microwave link'],
                'jawaban': 'a. Smart home (rumah pintar) untuk mengontrol perangkat elektronik'
            }
        ],
        'Data Center': [
            {
                'soal': 'Fungsi utama dari Data Center adalah...',
                'pilihan': ['a. Menyimpan, mengelola, dan mengamankan data dalam jumlah besar', 'b. Menyediakan koneksi internet ke rumah tangga', 'c. Menghubungkan perangkat IoT ke jaringan', 'd. Menyebarkan jaringan 5G ke berbagai wilayah'],
                'jawaban': 'a. Menyimpan, mengelola, dan mengamankan data dalam jumlah besar'
            },
            {
                'soal': 'Data Center berbasis cloud memungkinkan pengguna untuk...',
                'pilihan': ['a. Mengakses data dan aplikasi dari mana saja menggunakan internet', 'b. Menyimpan data hanya secara lokal di perangkat', 'c. Mengelola server fisik secara langsung', 'd. Mengurangi kebutuhan akan server'],
                'jawaban': 'a. Mengakses data dan aplikasi dari mana saja menggunakan internet'
            },
            {
                'soal': 'Salah satu isu penting dalam pengelolaan Data Center adalah...',
                'pilihan': ['a. Memastikan efisiensi penggunaan energi dan biaya', 'b. Kecepatan transmisi data yang lebih rendah', 'c. enggunaan kabel yang lebih banyak', 'd. Keterbatasan bandwidth dalam jaringan'],
                'jawaban': 'a. Memastikan efisiensi penggunaan energi dan biaya'
            }
        ],
        'Cloud Computing': [
            {
                'soal': 'Cloud Computing memungkinkan pengguna untuk...',
                'pilihan': ['a. Mengakses aplikasi dan data melalui internet tanpa perangkat keras lokal yang besar', 'b. Menyimpan data hanya di komputer lokal', 'c. Menghubungkan perangkat secara langsung menggunakan jaringan kabel', 'd. Menggunakan perangkat fisik sebagai server'],
                'jawaban': 'a. Mengakses aplikasi dan data melalui internet tanpa perangkat keras lokal yang besar'
            },
            {
                'soal': 'Layanan utama dalam Cloud Computing adalah...',
                'pilihan': ['a. IaaS, PaaS, dan SaaS', 'b. IP, DNS, dan HTTP', 'c. HTTP, FTP, dan SSH', 'd. OSI, TCP/IP, dan UDP'],
                'jawaban': 'a. IaaS, PaaS, dan SaaS'
            },
            {
                'soal': 'Salah satu keuntungan utama menggunakan Cloud Computing adalah...',
                'pilihan': ['a. Skalabilitas dan efisiensi biaya', 'b. Penggunaan perangkat keras lokal yang mahal', 'c. Penggunaan bandwidth yang terbatas', 'd. Harus selalu terhubung ke jaringan fisik'],
                'jawaban': 'a. Skalabilitas dan efisiensi biaya'
            }
        ],
        'Information Security': [
            {
                'soal': 'Keamanan informasi mencakup...',
                'pilihan': ['a. Kerahasiaan, integritas, dan ketersediaan data', 'b. Kecepatan transfer data', 'c.Penggunaan alamat IP yang aman', 'd. Penyimpanan data di cloud'],
                'jawaban': 'a. Kerahasiaan, integritas, dan ketersediaan data'
            },
            {
                'soal': 'Serangan DDoS bertujuan untuk...',
                'pilihan': ['a. Membanjiri server dengan lalu lintas untuk menghentikan layanan', 'b. Mencuri data sensitif pengguna', 'c. Menyebarkan perangkat IoT ke seluruh dunia', 'd. Meningkatkan keamanan jaringan 5G'],
                'jawaban': 'a. Membanjiri server dengan lalu lintas untuk menghentikan layanan'
            },
            {
                'soal': 'Salah satu cara untuk melindungi data dalam jaringan adalah...',
                'pilihan': ['a. Menggunakan enkripsi untuk menjaga kerahasiaan data', 'b. Meningkatkan kecepatan internet', 'c. Menggunakan lebih banyak perangkat IoT', 'd. Mengurangi penggunaan server'],
                'jawaban': 'a. Menggunakan enkripsi untuk menjaga kerahasiaan data'
            }
        ]
    },

    'en': {
        '5G': [
            {
                'soal': 'What is the main advantage of 5G technology compared to 4G?',
                'pilihan': ['a. Higher speed and lower latency', 'b. Higher security', 'c. More efficient bandwidth usage', 'd. No additional hardware required'],
                'jawaban': 'a. Higher speed and lower latency'
            },
            {
                'soal': '5G can be used for...',
                'pilihan': ['a. Providing wireless connections with high speed and low latency', 'b. Connecting IoT devices locally', 'c. Storing data in a Data Center', 'd. Improving security on Wi-Fi networks'],
                'jawaban': 'a. Providing wireless connections with high speed and low latency'
            },
            {
                'soal': 'What does low latency mean in the context of 5G?',
                'pilihan': ['a. Very short delay between sending and receiving data', 'b. The ability to connect more devices', 'c. Reducing the number of servers in the Data Center', 'd. Faster transmission speed'],
                'jawaban': 'a. Very short delay between sending and receiving data'
            }
        ],
        'Microwave Link': [
            {
                'soal': 'Microwave Link technology is used for...',
                'pilihan': ['a. Sending data in the form of microwave waves between devices', 'b. Connecting IoT devices to the network', 'c. Storing data online in the Cloud', 'd. Providing internet access to households'],
                'jawaban': 'a. Sending data in the form of microwave waves between devices'
            },
            {
                'soal': 'The main advantage of Microwave Link is...',
                'pilihan': ['a. High transmission speed for long distances', 'b. Wireless data transmission', 'c. Not affected by bad weather', 'd. Has limited bandwidth'],
                'jawaban': 'a. High transmission speed for long distances'
            },
            {
                'soal': 'Microwave Link is commonly used in...',
                'pilihan': ['a. Local network connections', 'b. Long-distance networks, such as connections between buildings or regions', 'c. Data storage in servers', 'd. Setting up IoT devices in smart homes'],
                'jawaban': 'b. Long-distance networks, such as connections between buildings or regions'
            }
        ],
        'IPv6': [
            {
                'soal': 'IPv6 was developed to replace IPv4 because...',
                'pilihan': ['a. IPv4 lacks IP addresses', 'b. IPv6 is more secure than IPv4', 'c. IPv4 supports higher speeds', 'd. IPv4 is easier to manage'],
                'jawaban': 'a. IPv4 lacks IP addresses'
            },
            {
                'soal': 'What is the length of an IPv6 address?',
                'pilihan': ['a. 32 bit', 'b. 128 bit', 'c. 64 bit', 'd. 256 bit'],
                'jawaban': 'b. 128 bit'
            },
            {
                'soal': 'One of the advantages of IPv6 is...',
                'pilihan': ['a. Almost unlimited IP addresses', 'b. Higher transmission speed', 'c. Ability to connect more devices to the network', 'd. Does not require DNS'],
                'jawaban': 'a. Almost unlimited IP addresses'
            }
        ],
        'Fiber Optics': [
            {
                'soal': 'Fiber optics transmits data using...',
                'pilihan': ['a. Microwave waves', 'b. Light', 'c. Electric current', 'd. Radio waves'],
                'jawaban': 'b. Light'
            },
            {
                'soal': 'The main advantage of using fiber optics in networks is...',
                'pilihan': ['a. High speed and resistance to electromagnetic interference', 'b. Very low cost', 'c. Easy to install and lightweight', 'd. Can transmit data over very long distances without maintenance'],
                'jawaban': 'a. High speed and resistance to electromagnetic interference'
            },
            {
                'soal': 'Fiber optics is generally used for...',
                'pilihan': ['a. High-speed and stable internet network connections', 'b. Storing data in Data Centers', 'c. Connecting IoT devices', 'd. Using wireless connections'],
                'jawaban': 'a. High-speed and stable internet network connections'
            }
        ],
        'IoT': [
            {
                'soal': 'What is meant by the Internet of Things (IoT)?',
                'pilihan': ['a. Connecting physical devices to the internet to exchange data', 'b. Storing data securely in the cloud', 'c. Using wired networks to transmit data', 'd. Controlling computers remotely'],
                'jawaban': 'a. Connecting physical devices to the internet to exchange data'
            },
            {
                'soal': 'One of the main challenges in implementing IoT is...',
                'pilihan': ['a. Data security and privacy', 'b. Low bandwidth usage', 'c. Excessive wired connections', 'd. Limited number of devices'],
                'jawaban': 'a. Data security and privacy'
            },
            {
                'soal': 'IoT is widely used in...',
                'pilihan': ['a. Smart homes for controlling electronic devices', 'b. Data storage in Data Centers', 'c. 5G network security', 'd. Sending data between devices using microwave links'],
                'jawaban': 'a. Smart homes for controlling electronic devices'
            }
        ],
        'Data Center': [
            {
                'soal': 'The main function of a Data Center is...',
                'pilihan': ['a. To store, manage, and secure large amounts of data', 'b. Providing internet access to households', 'c. Connecting IoT devices to the network', 'd. Distributing 5G networks to various regions'],
                'jawaban': 'a. To store, manage, and secure large amounts of data'
            },
            {
                'soal': 'Cloud-based Data Centers allow users to...',
                'pilihan': ['a. Access data and applications from anywhere using the internet', 'b. Store data only locally on devices', 'c. Manage physical servers directly', 'd. Reduce the need for servers'],
                'jawaban': 'a. Access data and applications from anywhere using the internet'
            },
            {
                'soal': 'One important issue in Data Center management is...',
                'pilihan': ['a. Ensuring energy efficiency and cost', 'b. Lower transmission speeds', 'c. Using more cables', 'd. Bandwidth limitations in networks'],
                'jawaban': 'a. Ensuring energy efficiency and cost'
            }
        ],
        'Cloud Computing': [
            {
                'soal': 'Cloud Computing allows users to...',
                'pilihan': ['a. Access applications and data via the internet without large local hardware', 'b. Store data only on local computers', 'c. Connect devices directly using wired networks', 'd. Use physical devices as servers'],
                'jawaban': 'a. Access applications and data via the internet without large local hardware'
            },
            {
                'soal': 'The main services in Cloud Computing are...',
                'pilihan': ['a. IaaS, PaaS, and SaaS', 'b. IP, DNS, and HTTP', 'c. HTTP, FTP, and SSH', 'd. OSI, TCP/IP, and UDP'],
                'jawaban': 'a. IaaS, PaaS, and SaaS'
            },
            {
                'soal': 'One of the main advantages of using Cloud Computing is...',
                'pilihan': ['a. Scalability and cost efficiency', 'b. Using expensive local hardware', 'c. Limited bandwidth usage', 'd. Always needing to be connected to a physical network'],
                'jawaban': 'a. Scalability and cost efficiency'
            }
        ],
        'Information Security': [
            {
                'soal': 'Information security includes...',
                'pilihan': ['a. Confidentiality, integrity, and availability of data', 'b. Data transfer speed', 'c. Using secure IP addresses', 'd. Storing data in the cloud'],
                'jawaban': 'a. Confidentiality, integrity, and availability of data'
            },
            {
                'soal': 'DDoS attacks aim to...',
                'pilihan': ['a. Flood servers with traffic to stop the service', 'b. Steal sensitive user data', 'c. Spread IoT devices worldwide', 'd. Increase 5G network security'],
                'jawaban': 'a. Flood servers with traffic to stop the service'
            },
            {
                'soal': 'One way to protect data in a network is...',
                'pilihan': ['a. Using encryption to maintain data confidentiality', 'b. Increasing internet speed', 'c. Using more IoT devices', 'd. Reducing the use of servers'],
                'jawaban': 'a. Using encryption to maintain data confidentiality'
            }
        ]
    }
}

import random
import re
from copy import deepcopy

# ===================== UTIL & CORE =====================

def _strip_label(s: str) -> str:
    """Hapus prefiks seperti 'a. ', 'b.' agar pilihan murni teks."""
    return re.sub(r'^[a-dA-D]\.\s*', '', s).strip()

def _label_of(i: int) -> str:
    return chr(97 + i)  # 0->'a'

def _normalize_user_answer(ans: str) -> str:
    """
    Terima 'a', 'A', 'a. ...' -> 'a'
    Jika tidak valid, kembalikan ''.
    """
    if not ans:
        return ''
    m = re.match(r'\s*([a-dA-D])(?:\s*\..*)?$', str(ans).strip())
    return m.group(1).lower() if m else ''

def _normalisasi_soal(q: dict) -> dict:
    """
    - Buang label pada pilihan & jawaban (jadi teks murni)
    - Acak pilihan
    - Simpan: 'pilihan' (teks), 'jawaban' (huruf), 'jawaban_teks' (teks), 'keterangan'
    """
    opsi_teks = [_strip_label(p) for p in q['pilihan']]
    jawab_target = _strip_label(q['jawaban'])

    # Pastikan jawaban ada di opsi
    try:
        idx_benar_awal = next(i for i, t in enumerate(opsi_teks) if t == jawab_target)
    except StopIteration:
        raise ValueError(f"Jawaban tidak ditemukan dalam pilihan untuk soal:\n{q['soal']}\nJawaban: {q['jawaban']}\nPilihan: {q['pilihan']}")

    # Acak sambil lacak indeks asal
    pasangan = list(enumerate(opsi_teks))  # (idx_asal, teks)
    random.shuffle(pasangan)
    idx_asal_list, opsi_acak = zip(*pasangan)

    # Posisi baru jawaban benar
    idx_benar_baru = idx_asal_list.index(idx_benar_awal)

    # Simpan kembali
    q['pilihan'] = list(opsi_acak)
    q['jawaban'] = _label_of(idx_benar_baru)
    q['jawaban_teks'] = q['pilihan'][idx_benar_baru]
    if not q.get('keterangan'):
        q['keterangan'] = f"Karena {q['jawaban_teks']}."
    return q

def acak_pilihan(soal_data: list) -> list:
    """Normalisasi + acak setiap soal, sinkronkan jawaban & keterangan."""
    return [_normalisasi_soal(deepcopy(soal)) for soal in soal_data]

def tampilkan_soal(soal_data: list, jawaban_user: list):
    """
    Tampilkan soal & opsi berlabel a/b/c/d.
    - Jika benar: ✅ + 'b. teks jawaban' + keterangan
    - Jika salah: ❌ + tampilkan jawaban user (mis. 'a. ...') + jawaban benar (mis. 'b. ...') + keterangan
    """
    for nomor, (soal, jw_user_raw) in enumerate(zip(soal_data, jawaban_user), start=1):
        print(f"{nomor}. {soal['soal']}")
        for i, pilihan in enumerate(soal['pilihan']):
            print(f"   {_label_of(i)}. {pilihan}")

        jw_user = _normalize_user_answer(jw_user_raw)
        jw_benar = soal['jawaban']

        # Susun teks lengkap (huruf + isi)
        def full_option(label: str) -> str:
            idx = ord(label) - 97
            return f"{label}. {soal['pilihan'][idx]}"

        if jw_user == jw_benar:
            print(f"   ✅ Benar: {full_option(jw_benar)}")
            print(f"   Keterangan: {soal['keterangan']}\n")
        else:
            if jw_user in ['a','b','c','d']:
                print(f"   ❌ Salah: {full_option(jw_user)}")
            else:
                print(f"   ❌ Salah: (jawaban tidak valid)")
            print(f"   Jawaban yang benar: {full_option(jw_benar)}")
            print(f"   Keterangan: {soal['keterangan']}\n")

# ===================== PENGACAKAN PER TOPIK =====================

# Kerja pada salinan data agar idempotent bila dipanggil ulang
bank = deepcopy(latihan_soal)

# Acak soal dalam setiap topik
if 'id' in bank:
    for topic in bank['id']:
        bank['id'][topic] = acak_pilihan(bank['id'][topic])

if 'en' in bank:
    for topic in bank['en']:
        bank['en'][topic] = acak_pilihan(bank['en'][topic])

# Contoh jawaban user (3 soal per topik)
jawaban_indo = ['a', 'a', 'a']
jawaban_english = ['a', 'a', 'a']

# ===================== OUTPUT =====================

print("\nSoal Bahasa Indonesia:")
for topic in bank['id']:
    print(f"\nTopik: {topic}")
    tampilkan_soal(bank['id'][topic], jawaban_indo)

print("\nSoal Bahasa Inggris:")
for topic in bank['en']:
    print(f"\nTopik: {topic}")
    tampilkan_soal(bank['en'][topic], jawaban_english)

