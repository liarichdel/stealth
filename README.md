# Top-Down Stealth Roguelite Game

Sebuah proyek game aksi penyusupan dari sudut pandang atas (*top-down*) yang memadukan elemen *stealth* taktis dengan mekanik *roguelite*. Game ini dikembangkan menggunakan bahasa pemrograman **Python** dan *library* **Pygame** dengan fokus utama pada penerapan konsep Pemrograman Berbasis Objek (OOP) yang mendalam.

---

# 👥 Anggota Kelompok

*   Nailah Salsabila Ramadhani Kusnadi - 25051204075 / kelas TI 2025 A
*   Johana Putri Adelia - 25051204053 / kelas TI 2025 A
*   Aisyah Miyuki Anastasya Syafila - 25051204172 / kelas TI 2025 A

---

# 🎯 Fitur Utama

*   **Procedural Map Generation:** Tata letak ruangan, dinding, rintangan, dan koridor digenerasikan secara acak setiap kali permainan baru dimulai, memberikan tantangan yang unik di setiap *run*.
*   **Dynamic AI State Machine:** Musuh memiliki kecerdasan buatan dinamis yang merespons aksi pemain (melihat atau mendengar langkah kaki) dengan transisi perilaku yang halus.
*   **Advanced Vision System (FOV):** Mekanik *Field of View* (FOV) berbasis perhitungan geometri 2D nyata untuk menciptakan efek *Fog of War* (area yang tidak terlihat oleh penjaga atau kamera akan menggelap).
*   **Hacking & Inventory System:** Pemain dapat meretas terminal keamanan untuk membuka jalan atau menonaktifkan kamera, serta mengumpulkan *item* acak dari *factory drop*.

---

# 🛠️ Penjelasan Implementasi OOP

Proyek ini dirancang dengan arsitektur berorientasi objek yang kuat, menerapkan beberapa *Design Pattern* standar industri:

# 1. State Machine Pattern (Kecerdasan Buatan Musuh)
Perilaku musuh diisolasi ke dalam beberapa *class state* terpisah yang diturunkan dari *abstract class* `EnemyState`. Hal ini menghindari percabangan `if-else` yang rumit di kelas utama:
*   `PatrolState`: Musuh bergerak secara periodik di antara titik-titik rute patroli yang sudah ditentukan.
*   `ChaseState`: Terpicu saat `VisionSystem` mendeteksi pemain. Kecepatan musuh meningkat dan langsung memburu posisi pemain.
*   `SearchState`: Terpicu jika musuh kehilangan jejak pemain. Musuh akan menginvestigasi area sekitar titik terakhir pemain terlihat selama beberapa detik sebelum kembali ke mode patroli.

# 2. Factory Pattern (Manajemen Objek)
Menggunakan class `ObjectFactory` untuk mengotomatisasi pembuatan instansiasi objek di dalam map (seperti `Enemy`, `Item`, `Terminal`, dan `SecurityCamera`). *Factory* ini bertugas mengatur atribut acak objek berdasarkan tingkat kesulitan (*difficulty level*) agar permainan tetap seimbang.

# 3. Inheritance & Polymorphism (Struktur Entitas)
Semua objek bergerak di dalam game diturunkan dari satu *superclass* utama, yaitu `Entity`. 
*   Class `Player` dan `Enemy` mewarisi properti dasar seperti koordinat (`x`, `y`), `rect` (untuk sistem *collision* Pygame), serta fungsi `move()`.
*   Prinsip *Polymorphism* diterapkan pada method `update()` dan `draw()`, di mana setiap objek anak mendefinisikan ulang cara mereka memperbarui logika dan menampilkan visualnya masing-masing di layar.

---

## 🚀 Cara Menjalankan Project

### Prasyarat
Pastikan Anda sudah menginstal **Python (versi 3.8 atau yang lebih baru)** di komputer Anda.

### Langkah-Langkah Instalasi

1.  **Clone Repositori Ini**
    git clone https://github.com/miyuki-cell/stealth.git
    cd stealth

2. **Buat & aktifkan Virtual environments (Direkomendasikan)**
   - Windows
     python -m venv venv
     venv\Scripts\activate

   - macOS/Linux
     python3 -m venv venv
     source venv/bin/activate

3.  **Instal Dependensi**
    Game ini hanya membutuhkan library Pygame. Instal menggunakan perintah berikut:
    pip install pygame

4. **Jalankan Game**
   Eksekusi file utama proyek untuk memulai permainan:
   python stealth.py

   atau

   python3 stealth.py


   
