# AUTO-SAVE FEATURE - DOKUMENTASI LENGKAP

## 1. FITUR AUTOSAVE DI WEB INTERFACE (app.py)

### Tombol Toggle Auto-Save
- **Lokasi**: Panel kontrol utama di halaman web
- **Nama**: "🤖 Auto-save: OFF/ON"
- **Cara kerja**:
  - Klik tombol untuk toggle
  - Status ditampilkan dengan warna:
    * **GREEN (#4caf50)**: Auto-save ENABLED
    * **GRAY (#808080)**: Auto-save DISABLED

### Cara Kerja di Web
1. User klik tombol "🤖 Auto-save: OFF"
2. Tombol berubah menjadi "🤖 Auto-save: ON" (hijau)
3. Ketika gesture TIDAK DIKENAL (merah "Tidak Dikenal"):
   - Gesture otomatis disimpan
   - Nama: unknown_0, unknown_1, unknown_2, dst
   - Status berubah: "Auto-saved: unknown_X" (oranye)
   - File JSON tersimpan di folder gesture_data/
   - Model Fuzzy ART otomatis dilatih
4. Toggle lagi untuk menonaktifkan

### API Endpoints
```
POST /api/auto_save/toggle
  Response: {auto_save_enabled, message}

GET /api/auto_save/status
  Response: {auto_save_enabled, unknown_counter, total_categories}

POST /api/auto_save/reset
  Response: {message}
```

---

## 2. FITUR AUTOSAVE DI DESKTOP APP (capture_gestures.py)

### Keyboard Controls
```
[t] - Simpan gesture saat ini dengan auto-naming (gesture_0, gesture_1, ...)
[n] - Simpan dengan custom name (input via terminal)
[s] - Simpan model ke CSV
[a] - TOGGLE AUTO-SAVE untuk gesture yang tidak dikenal
[r] - Reset counter
[q] - Quit
```

### Cara Kerja
1. Tekan **[a]** untuk toggle auto-save
2. Terminal menampilkan: "[INFO] Auto-save: ENABLED" atau "[INFO] Auto-save: DISABLED"
3. Ketika gesture TIDAK DIKENAL (idx == -2) dan auto-save ENABLED:
   - Gesture otomatis disimpan sebagai: unknown_0, unknown_1, dst
   - Status window berubah: "Auto-saved: unknown_X" (oranye)
   - Console log: "[OK] Gesture 'unknown_X' saved! (File: unknown_X_timestamp.json)"
   - Unknown_counter naik otomatis

### Safety Features
- **Deduplikasi**: Gesture yang sama tidak disimpan 2x
  - Menggunakan `vec.tobytes()` untuk membandingkan
  - Hanya save jika berbeda dari last_saved_gesture_bytes

### Global Variables (capture_gestures.py)
```python
auto_save_unknown = False          # Toggle status
unknown_counter = 0                # Counter untuk unknown gestures
last_saved_gesture_bytes = None    # Hash gesture terakhir (deduplikasi)
```

---

## 3. WORKFLOW CONTOH

### Skenario: Menggunakan Desktop App dengan Autosave

```
1. Jalankan: python capture_gestures.py
2. Tekan [a] → "[INFO] Auto-save: ENABLED"
3. Tunjukkan gesture baru yang belum dikenal
4. Console: "Tidak Dikenal" (merah)
5. Otomatis tersimpan:
   - File: gesture_data/unknown_0_1765377123456.json
   - Status: "Auto-saved: unknown_0" (oranye)
6. Tunjukkan gesture berbeda
7. Otomatis tersimpan: unknown_1, unknown_2, dst
8. Tekan [s] → Simpan model
9. Tekan [a] → Toggle off
10. Tekan [q] → Keluar
```

---

## 4. STRUKTUR DATA JSON (gesture_data/)

```json
{
  "gesture": "unknown_0",
  "timestamp": 1765377123456,
  "features": [
    0.52, 0.48, 0.51, 0.49, ...  // 42 float values
  ]
}
```

---

## 5. FITUR TAMBAHAN

### Reset Unknown Counter
- **Di Web**: POST /api/auto_save/reset
- **Di Desktop**: Tekan [r] hanya reset gesture_counter, unknown_counter reset otomatis saat aplikasi restart

### View Status Auto-Save
- **Di Web**: GET /api/auto_save/status
- **Di Desktop**: Lihat console log saat toggle [a]

---

## 6. PERBANDINGAN DENGAN FITUR SEBELUMNYA

| Fitur | Sebelum | Sekarang (dengan Autosave) |
|-------|---------|---------------------------|
| Save Mode | Manual (tekan [t]/[n]) | Manual + Otomatis |
| Unknown Gesture | User ambil keputusan | Auto-save jika enabled |
| Deduplikasi | Tidak ada | Ada (vec.tobytes()) |
| Counter | gesture_counter | gesture_counter + unknown_counter |
| Naming | gesture_0, gesture_1 | gesture_0, gesture_1 + unknown_0, unknown_1 |
| UI Feedback | "Tidak Dikenal" | "Auto-saved: unknown_X" |

---

## 7. TIPS PENGGUNAAN

✅ **DO**
- Gunakan autosave untuk mengumpulkan gesture baru dengan cepat
- Reset counter atau tekan [a] untuk toggle sesuai kebutuhan
- Save model ([s] atau Save Model button) setelah collecting gestures baru

❌ **DON'T**
- Jangan biarkan autosave ON selamanya (bisa save gesture accidental)
- Jangan lupa save model setelah collecting banyak gesture baru
- Jangan close aplikasi tanpa tekan [q] (bisa incomplete)

---

## 8. FILES YANG DIMODIFIKASI

- ✅ `app.py`: Auto-save logic, API endpoints, global variables
- ✅ `templates/index.html`: Toggle button, toggleAutoSave() function
- ✅ `capture_gestures.py`: Auto-save logic, keyboard handler [a]
