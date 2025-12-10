# 🤖 Hand Gesture Recognition - Real-Time Deployment

Sistem deteksi gesture tangan dengan Roboflow dan Fuzzy ART yang dapat dilatih secara real-time melalui web interface.

## 🚀 Fitur Utama

- **Real-Time Detection**: Deteksi gesture tangan secara langsung dari webcam
- **Roboflow Integration**: Menggunakan model YOLO Roboflow untuk lokalisasi tangan
- **Fuzzy ART Learning**: Algoritma pembelajaran adaptif untuk mengidentifikasi gesture
- **Live Training**: Tambah gesture baru langsung dari web interface
- **Model Persistence**: Simpan dan load model dari CSV

## 📋 Requirements

- Python 3.9+
- Webcam / Camera
- Internet connection (untuk Roboflow API)

## 🔧 Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Konfigurasi Roboflow API

Edit file `app.py` dan ganti dengan API key Anda:

```python
ROBOFLOW_API_KEY = "YOUR_API_KEY_HERE"
ROBOFLOW_MODEL_ID = "YOUR_MODEL_ID/VERSION"
```

### 3. Jalankan Server

**Option A: Batch Script (Windows)**
```bash
run.bat
```

**Option B: PowerShell**
```powershell
powershell -ExecutionPolicy Bypass -File run.ps1
```

**Option C: Direct Python**
```bash
python app.py
```

### 4. Akses Web Interface

Buka browser dan navigasi ke:
```
http://localhost:5000
```

## 📖 Cara Menggunakan

### Mode Deteksi

1. Buka web interface
2. Izinkan akses kamera
3. Arahkan tangan ke kamera
4. Sistem akan menampilkan gesture yang terdeteksi

### Mode Training (Menambah Gesture Baru)

1. Klik tombol **🎓 Training** di web interface
2. Masukkan nama gesture baru (contoh: "Peace", "ThumbsUp", "Ok")
3. Klik **▶️ Mulai Training**
4. Perlihatkan gesture di depan kamera (kumpulkan 20-30 sampel)
5. Sistem akan otomatis mengumpulkan sampel saat hand landmark terdeteksi
6. Klik **⏹️ Selesai Training** untuk menyelesaikan
7. Gesture baru akan tersimpan dan siap digunakan

### Menyimpan Model

- Klik **💾 Save Model** untuk menyimpan semua gesture ke file CSV
- Model akan disimpan otomatis saat menggunakan training

## 📁 File Structure

```
Handgesture/
├── app.py                          # Flask server dengan video streaming
├── templates/
│   └── index.html                  # Web interface
├── model_art_weights.csv           # Bobot model Fuzzy ART
├── model_art_names.csv             # Nama gesture
├── requirements.txt                # Python dependencies
├── run.bat                         # Startup script (Windows)
├── run.ps1                         # Startup script (PowerShell)
└── README.md                       # Dokumentasi
```

## 🎯 API Endpoints

### Detection
- `GET /` - Web interface utama
- `GET /video_feed` - MJPEG video stream
- `GET /api/gesture` - Status gesture saat ini

### Model Management
- `POST /api/save_model` - Simpan model ke CSV
- `GET /api/gestures/list` - List semua gesture

### Training
- `POST /api/training/start` - Mulai training mode
- `POST /api/training/stop` - Selesaikan training dan simpan
- `POST /api/training/cancel` - Batalkan training
- `GET /api/training/status` - Status training saat ini

## ⚙️ Konfigurasi Lanjutan

Edit parameter di `app.py`:

```python
# Fuzzy ART Parameters
RHO = 0.90      # Vigilance (0-1, lebih tinggi = lebih banyak kategori)
ALPHA = 0.001   # Choice parameter
BETA = 1.0      # Learning rate (1.0 = fast learning)
```

## 🐛 Troubleshooting

### Camera tidak terdeteksi
```bash
# Cek device ID kamera
python -c "import cv2; cap = cv2.VideoCapture(0); print(cap.isOpened())"
```

### Roboflow API Error
- Pastikan API key valid dan terbaru
- Periksa koneksi internet
- Cek model ID Roboflow

### Model tidak menyimpan
- Pastikan folder writable
- Cek permission file

## 📊 Performa

- **Latency**: ~100-200ms per frame
- **FPS**: 5-10 FPS (tergantung CPU)
- **Akurasi**: ~85-95% (tergantung training samples)

## 📝 License

MIT License - Bebas digunakan dan dimodifikasi

## 👨‍💻 Author

Created dengan ❤️ untuk Hand Gesture Recognition Project

---

**Tip**: Untuk hasil terbaik, latih setiap gesture dengan 30-50 sampel dari berbagai sudut dan jarak.
