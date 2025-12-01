import cv2
import mediapipe as mp
import numpy as np
import os
import csv
import time
import glob

# [PENTING] Import yang benar untuk klien HTTP Roboflow
from inference_sdk import InferenceHTTPClient

CLIENT = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key="5vFdrINv9FtzcV3AztHz"
)





# ==========================================
# 1. KONFIGURASI FILE & MODEL
# ==========================================
# File untuk menyimpan memori model ART
WEIGHTS_FILE = 'model_art_weights.csv' 
NAMES_FILE = 'model_art_names.csv'      

# Daftar folder dataset CSV (Roboflow dan Custom)
DATASET_FOLDERS = [
    "datasets/roboflow_data",    # CSV hasil konversi dari data Roboflow
    "datasets/my_custom_data"    # CSV hasil rekaman manual kamera
]

# [ROBOFLOW CONFIG] PASTIKAN INI ADALAH DATA VALID DAN MODEL HAND DETECTION
ROBOFLOW_API_KEY = "5vFdrINv9FtzcV3AztHzI" 
# Ganti dengan MODEL ID yang mendeteksi tangan (misal: "hand-detection-model/1")
ROBOFLOW_MODEL_ID = "object-dect-qhvpj/3" 
ROBOFLOW_URL = "https://detect.roboflow.com"
ROBOFLOW_SERVERLESS_URL = "https://serverless.roboflow.com"  # For serverless inference (no server needed)

# Parameter Algoritma Fuzzy ART
RHO = 0.90    # Vigilance (Kewaspadaan)
ALPHA = 0.001 # Choice parameter
BETA = 1.0    # Learning Rate (Fast Learning)

# ==========================================
# 2. ALGORITMA FUZZY ART (CORE)
# ==========================================
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

# ==========================================
# 3. FUNGSI MUAT & SIMPAN MODEL (CSV)
# ==========================================
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

# ==========================================
# 4. FUNGSI UTILITAS
# ==========================================
def test_inference(image_urls=None, model_id=None):
    """
    Test Roboflow inference on one or more images.
    Args:
        image_urls: List of image URLs or single URL string
        model_id: Model ID in format "project/version"
    """
    if model_id is None:
        model_id = ROBOFLOW_MODEL_ID
    
    if image_urls is None:
        # Default test images
        image_urls = [
            "https://source.roboflow.com/MADpQ3Hao1cYUHceGeNrCZOcl6k1/sMeu89vrsUkigz3q8gMQ/original.jpg"
        ]
    elif isinstance(image_urls, str):
        image_urls = [image_urls]
    
    print("\n" + "="*60)
    print("ROBOFLOW INFERENCE TEST")
    print("="*60)
    print(f"Model ID: {model_id}")
    print(f"API URL: {ROBOFLOW_SERVERLESS_URL}")
    print(f"Testing {len(image_urls)} image(s)...\n")
    
    try:
        client = InferenceHTTPClient(
            api_url=ROBOFLOW_SERVERLESS_URL,
            api_key=ROBOFLOW_API_KEY
        )
    except Exception as e:
        print(f"[ERROR] Failed to initialize Roboflow client: {e}")
        return None
    
    all_results = []
    for i, url in enumerate(image_urls, 1):
        print(f"[{i}/{len(image_urls)}] Testing: {url[:80]}...")
        try:
            result = client.infer(url, model_id=model_id)
            all_results.append(result)
            
            # Parse results
            if 'predictions' in result:
                predictions = result['predictions']
                print(f"    ✓ Success! Found {len(predictions)} prediction(s)")
                for pred in predictions:
                    print(f"      - {pred.get('class', 'unknown')}: confidence={pred.get('confidence', 0):.2%}")
            else:
                print(f"    ✓ Success! No predictions found")
            
            print(f"    Inference time: {result.get('time', 0):.3f}s\n")
        except Exception as e:
            print(f"    ✗ Error: {e}\n")
    
    print("="*60)
    return all_results

# ==========================================
# 5. FUNGSI UTILITAS
# ==========================================
def extract_features(results):
    """Mengubah Landmark MediaPipe menjadi Vektor Fitur (42D)"""
    if not results.multi_hand_landmarks: return None
    hand_landmarks = results.multi_hand_landmarks[0]
    base_x = hand_landmarks.landmark[0].x
    base_y = hand_landmarks.landmark[0].y
    feature_vector = []
    for lm in hand_landmarks.landmark:
        # Normalisasi Relatif terhadap pergelangan tangan (wrist)
        norm_x = (lm.x - base_x) + 0.5
        norm_y = (lm.y - base_y) + 0.5
        feature_vector.append(max(0.0, min(1.0, norm_x)))
        feature_vector.append(max(0.0, min(1.0, norm_y)))
    return np.array(feature_vector, dtype=np.float32)

def train_datasets(art_model, gesture_names, folders):
    """Melatih ART dari multiple folder CSV dataset (Non-Real-Time/Pre-training)."""
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
                        # Pelatihan inkremental non-real-time
                        idx = art_model.train_single_input(vec) 
                        gesture_names[idx] = label
                        count += 1
                        total += 1
                    except: continue
    if total > 0:
        print(f"-> Berhasil mempelajari {total} sampel baru dari dataset.")
    else:
        print("-> Tidak ada data baru dilatih.")


# ==========================================
# 6. MAIN LOOP (REAL-TIME INTEGRASI)
# ==========================================
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
    # min_detection_confidence=0.5 adalah default yang baik untuk deteksi
    hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5) 
    cap = cv2.VideoCapture(0)

    # TAHAP NON-REAL-TIME (PRE-TRAINING)
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
                predictions = yolo_client.infer(
                    display_frame, 
                    model_id=ROBOFLOW_MODEL_ID, 
                    confidence=0.5
                )
            except Exception:
                predictions = None
            
            hand_bb = None
            if predictions and 'predictions' in predictions:
                # Cari bounding box tangan (Asumsi: class di Roboflow adalah 'hand' atau nama gesture)
                hand_predictions = [p for p in predictions['predictions'] if p['class'].lower() == 'hand']
                if not hand_predictions:
                    # Coba ambil prediksi dengan confidence tertinggi, apapun namanya
                    all_predictions = predictions['predictions']
                    if all_predictions:
                        hand_predictions.append(max(all_predictions, key=lambda x: x['confidence']))


                if hand_predictions:
                    best_pred = max(hand_predictions, key=lambda x: x['confidence'])
                    hand_bb = best_pred
            
            if hand_bb:
                x_min, y_min, x_max, y_max = hand_bb['x_min'], hand_bb['y_min'], hand_bb['x_max'], hand_bb['y_max']
                
                # Tambah Padding agar MediaPipe tidak memotong jari
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
                # TAHAP REAL-TIME (KLASIFIKASI)
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
            
        # Manual Train (REAL-TIME ADAPTATION)
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
    import sys
    
    # Allow command-line arguments for testing
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Test inference on sample images
        test_urls = [
            "https://source.roboflow.com/MADpQ3Hao1cYUHceGeNrCZOcl6k1/sMeu89vrsUkigz3q8gMQ/original.jpg",
        ]
        test_inference(test_urls)
    else:
        # Run the main gesture recognition loop
        main()