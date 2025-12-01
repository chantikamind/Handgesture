import cv2
import mediapipe as mp
import numpy as np
import os
import csv
import time
import glob

# [PENTING] Import yang benar untuk klien HTTP Roboflow
from inference_sdk import InferenceHTTPClient 


# 1. KONFIGURASI FILE & MODEL

# File untuk menyimpan memori model ART
WEIGHTS_FILE = 'model_art_weights.csv' 
NAMES_FILE = 'model_art_names.csv'      

# Daftar folder dataset CSV (Roboflow dan Custom)
DATASET_FOLDERS = [
    "datasets/roboflow_data",    # Hasil konversi Roboflow dari script convert_roboflow.py
    "datasets/my_custom_data"    # Hasil rekaman Anda sendiri dari script auto_collect_data.py
]

# [ROBOFLOW CONFIG] GANTI DENGAN DATA ANDA
ROBOFLOW_API_KEY = "5vFdrINv9FtzcV3AztHzI" 
# GANTI dengan MODEL ID Hand Detection Anda
ROBOFLOW_MODEL_ID = "object-dect-qhvpj/3" 
ROBOFLOW_URL = "https://detect.roboflow.com"

# Parameter Algoritma Fuzzy ART
RHO = 0.90    # Vigilance (Semakin tinggi, semakin banyak kategori yang terbentuk)
ALPHA = 0.001 # Choice parameter
BETA = 1.0    # Learning Rate (1.0 = Belajar instan/Fast Learning)


# 2. ALGORITMA FUZZY ART (CORE)

class FuzzyART:
    def __init__(self, rho=RHO, alpha=ALPHA, beta=BETA):
        self.rho = rho
        self.alpha = alpha
        self.beta = beta
        self.weights = [] # List of numpy arrays

    def complement_coding(self, x):
        """Transformasi wajib untuk Fuzzy ART: [input, 1-input]"""
        x = np.clip(x, 0, 1)
        return np.concatenate((x, 1 - x))

    def train_single_input(self, x_raw):
        """Melatih model secara inkremental"""
        x = self.complement_coding(x_raw)
        
        if len(self.weights) == 0:
            self.weights.append(x)
            return 0

        # Pattern Matching
        T = []
        for W_j in self.weights:
            fuzzy_and = np.minimum(x, W_j)
            T_j = np.sum(fuzzy_and) / (self.alpha + np.sum(W_j))
            T.append(T_j)
        
        sorted_indices = np.argsort(T)[::-1]

        # Vigilance Test & Resonance
        for j_star in sorted_indices:
            W_jstar = self.weights[j_star]
            match_ratio = np.sum(np.minimum(x, W_jstar)) / np.sum(x)

            if match_ratio >= self.rho:
                # Update Bobot
                new_weight = self.beta * np.minimum(x, W_jstar) + (1 - self.beta) * W_jstar
                self.weights[j_star] = new_weight
                return j_star

        # Reset (Kategori Baru)
        self.weights.append(x)
        return len(self.weights) - 1

    def classify(self, x_raw):
        """Mengklasifikasikan input"""
        if len(self.weights) == 0: return -1
        x = self.complement_coding(x_raw)

        T = []
        for W_j in self.weights:
            fuzzy_and = np.minimum(x, W_j)
            T_j = np.sum(fuzzy_and) / (self.alpha + np.sum(W_j))
            T.append(T_j)
        
        j_star = np.argmax(T)
        W_jstar = self.weights[j_star]
        match_ratio = np.sum(np.minimum(x, W_jstar)) / np.sum(x)

        if match_ratio >= self.rho: return j_star
        else: return -2 # Tidak Dikenal


# 3. FUNGSI MUAT & SIMPAN MODEL (CSV)

def save_model_csv(art_model, gesture_names):
    """Menyimpan bobot dan nama ke dua file CSV."""
    print("\n[INFO] Menyimpan model ke CSV...")
    
    # A. Simpan Bobot (Weights)
    with open(WEIGHTS_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        for w in art_model.weights:
            writer.writerow(w) 
    
    # B. Simpan Nama Gesture (Names)
    with open(NAMES_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["id", "name"]) # Header
        for idx, name in gesture_names.items():
            writer.writerow([idx, name])
            
    print(f" -> Bobot disimpan ke: {WEIGHTS_FILE}")
    print(f" -> Nama disimpan ke : {NAMES_FILE}")

def load_model_csv():
    """Memuat bobot dan nama dari CSV."""
    art = FuzzyART()
    names = {}
    
    # A. Muat Bobot
    if os.path.exists(WEIGHTS_FILE):
        print(f"[INFO] Memuat bobot dari {WEIGHTS_FILE}...")
        with open(WEIGHTS_FILE, 'r') as f:
            reader = csv.reader(f)
            loaded_weights = []
            for row in reader:
                if not row: continue
                try:
                    w_vec = np.array(row, dtype=np.float32)
                    loaded_weights.append(w_vec)
                except ValueError:
                    print(f"[ERROR] Gagal memuat baris: {row}. Cek format CSV.")
            art.weights = loaded_weights
        print(f" -> {len(art.weights)} kategori bobot dimuat.")
    else:
        print(f"[INFO] File bobot {WEIGHTS_FILE} tidak ditemukan. Membuat model baru.")

    # B. Muat Nama
    if os.path.exists(NAMES_FILE):
        print(f"[INFO] Memuat nama dari {NAMES_FILE}...")
        with open(NAMES_FILE, 'r') as f:
            reader = csv.reader(f)
            next(reader, None) # Skip Header
            for row in reader:
                if len(row) >= 2:
                    try:
                        idx = int(row[0])
                        label = row[1]
                        names[idx] = label
                    except ValueError:
                        continue
    
    return art, names


# 4. FUNGSI UTILITAS

def extract_features(results):
    """Mengubah Landmark MediaPipe menjadi Vektor Fitur (42D)"""
    if not results.multi_hand_landmarks: return None
    hand_landmarks = results.multi_hand_landmarks[0]
    base_x = hand_landmarks.landmark[0].x
    base_y = hand_landmarks.landmark[0].y
    feature_vector = []
    for lm in hand_landmarks.landmark:
        norm_x = (lm.x - base_x) + 0.5
        norm_y = (lm.y - base_y) + 0.5
        feature_vector.append(max(0.0, min(1.0, norm_x)))
        feature_vector.append(max(0.0, min(1.0, norm_y)))
    return np.array(feature_vector, dtype=np.float32)

def train_datasets(art_model, gesture_names, folders):
    """Melatih ART dari multiple folder CSV dataset (Pre-training)."""
    print("\n--- CEK DATASET TAMBAHAN (PRE-TRAINING) ---")
    total = 0
    for folder in folders:
        if not os.path.exists(folder): continue
        csv_files = glob.glob(os.path.join(folder, "*.csv"))
        
        for file_path in csv_files:
            label = os.path.basename(file_path).replace(".csv", "")
            with open(file_path, 'r') as f:
                reader = csv.reader(f)
                next(reader, None) # Skip header
                count = 0
                for row in reader:
                    if not row: continue
                    try:
                        vec = np.array(row, dtype=np.float32)
                        idx = art_model.train_single_input(vec)
                        gesture_names[idx] = label
                        count += 1
                        total += 1
                    except: continue
    if total > 0:
        print(f"-> Berhasil mempelajari {total} sampel baru dari dataset.")
    else:
        print("-> Tidak ada data baru dilatih.")


# 5. MAIN LOOP (REAL-TIME INTEGRASI)

def main():
    # --- 1. INISIALISASI ROBOFLOW CLIENT ---
    yolo_client = None
    try:
        yolo_client = InferenceHTTPClient(
            api_url=ROBOFLOW_URL,
            api_key=ROBOFLOW_API_KEY
        )
        print(f"[INFO] Roboflow Inference Client terhubung. Model ID: {ROBOFLOW_MODEL_ID}.")
    except Exception as e:
        print(f"[ERROR] Gagal inisialisasi Roboflow Client. Pastikan API Key dan koneksi internet berfungsi. Detail: {e}")
        
    # --- 2. SETUP MEDIA PIPE & ART ---
    mp_hands = mp.solutions.hands
    mp_draw = mp.solutions.drawing_utils
    hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5) 
    cap = cv2.VideoCapture(0)

    # Load ART model dari CSV dan Pre-train dari folder dataset
    art, gesture_names = load_model_csv()
    train_datasets(art, gesture_names, DATASET_FOLDERS)

    print("\n--- SISTEM ART + ROBOFLOW SIAP ---")

    while cap.isOpened():
        success, frame = cap.read()
        if not success: break
        
        frame = cv2.flip(frame, 1)
        display_frame = frame.copy() 
        
        status = "Mencari Tangan..."
        color = (255, 255, 0)
        vec = None
        cropped_frame = None

        # 3. LOKALISASI TANGAN DENGAN ROBOFLOW (Jika klien aktif)
        if yolo_client:
            try:
                # Inferensi ke Roboflow Cloud
                predictions = yolo_client.infer(
                    display_frame, 
                    model_id=ROBOFLOW_MODEL_ID, 
                    confidence=0.5
                )
            except Exception:
                predictions = None
            
            hand_bb = None
            if predictions and 'predictions' in predictions:
                # Cari bounding box tangan
                hand_predictions = [p for p in predictions['predictions'] if p['class'].lower() == 'hand']
                if hand_predictions:
                    best_pred = max(hand_predictions, key=lambda x: x['confidence'])
                    hand_bb = best_pred
            
            if hand_bb:
                x_min, y_min, x_max, y_max = hand_bb['x_min'], hand_bb['y_min'], hand_bb['x_max'], hand_bb['y_max']
                
                # Tambah Padding
                pad = 30 
                H, W, _ = frame.shape
                x_min = max(0, int(x_min) - pad)
                y_min = max(0, int(y_min) - pad)
                x_max = min(W, int(x_max) + pad)
                y_max = min(H, int(y_max) + pad)
                
                # Gambar Bounding Box
                cv2.rectangle(display_frame, (x_min, y_min), (x_max, y_max), (255, 0, 0), 2)
                
                # Potong Frame (Crop)
                cropped_frame = frame[y_min:y_max, x_min:x_max]
        
        # 4. MEDIA PIPE PADA FRAME TERTARGET
        frame_to_process = cropped_frame if cropped_frame is not None and cropped_frame.size > 0 else frame
        
        rgb_frame = cv2.cvtColor(frame_to_process, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            # Gambar Landmark
            mp_draw.draw_landmarks(display_frame, results.multi_hand_landmarks[0], mp_hands.HAND_CONNECTIONS)
            
            # Ekstraksi Fitur dan Klasifikasi ART
            vec = extract_features(results)
            
            if vec is not None:
                idx = art.classify(vec)     
                
                if idx >= 0:
                    name = gesture_names.get(idx, f"Unknown ({idx})")
                    status = f"Gesture: {name}"
                    color = (0, 255, 0)
                elif idx == -2:
                    status = "Tidak Dikenal"
                    color = (0, 0, 255)

        # UI
        cv2.rectangle(display_frame, (0, 0), (640, 60), (0, 0, 0), -1)
        cv2.putText(display_frame, status, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        cv2.putText(display_frame, f"Data Tersimpan: {len(art.weights)} | Roboflow: {'ON' if yolo_client else 'OFF'}", (20, 75), cv2.FONT_ITALIC, 0.5, (200, 200, 200), 1)
        
        cv2.imshow("Hand Gesture", display_frame)
        
        key = cv2.waitKey(1) & 0xFF
        
        # Save ke CSV
        if key == ord('s'):
            save_model_csv(art, gesture_names)
            
        # Manual Train
        elif key == ord('t') and vec is not None:
            idx = art.train_single_input(vec)
            if idx not in gesture_names:
                gesture_names[idx] = input("Nama Gesture Baru: ")
                
        # Quit
        elif key == ord('q'):
            save_model_csv(art, gesture_names)
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()