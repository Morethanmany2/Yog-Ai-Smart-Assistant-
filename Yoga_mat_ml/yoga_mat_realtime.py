import serial
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from tensorflow.keras.models import load_model
import time

# ============================
# CONFIGURATION
# ============================

PORT = "COM10"
BAUD = 115200

MODEL_PATH = "yoga_model.h5"   # trained model
SAVE_DATA = False
SAVE_FILE = "realtime_log.csv"

poses = ["empty","hand_pressed"]

# ============================
# PARSE ESP32 FRAME
# ============================

def parse_frame(line):
    if not line.endswith("END"):
        return None

    line = line.replace("END", "").strip().strip(",")
    parts = line.split(",")

    if len(parts) != 48:
        return None

    values = list(map(int, parts))
    mat = np.array(values).reshape((8, 6))

    # 🔥 Optional fix: flip/rotate if your mat is physically rotated
    # mat = np.flipud(mat)       # flip vertically
    # mat = np.fliplr(mat)       # flip horizontally
    # mat = mat.T                # transpose if needed

    return mat

# ============================
# LOAD MODEL
# ============================

print("Loading ML model...")
model = load_model(MODEL_PATH)
print("Model loaded.")

# ============================
# SETUP SERIAL
# ============================

print("Connecting to ESP32 on", PORT)
ser = serial.Serial(PORT, BAUD, timeout=1, rtscts=False, dsrdtr=False)
print("Connected.\n")

# ============================
# OPTIONAL CSV LOG
# ============================

if SAVE_DATA:
    df_log = pd.DataFrame()
    print("Logging enabled →", SAVE_FILE)
else:
    print("Logging disabled.")

# ============================
# HEATMAP SETUP
# ============================

plt.ion()
fig, ax = plt.subplots(figsize=(5, 6))

buffer = ""

# ============================
# MAIN LOOP
# ============================

while True:
    try:
        # read incoming characters
        chunk = ser.read().decode(errors="ignore")
        if not chunk:
            continue

        buffer += chunk

        # process one complete frame
        if "END" not in buffer:
            continue

        frame_line = buffer.split("END")[0]
        buffer = ""

        mat = parse_frame(frame_line + "END")
        if mat is None:
            continue

        # ML prediction
        x = mat.flatten().reshape((1, 48, 1))
        pred = model.predict(x, verbose=0)[0]
        pose = poses[np.argmax(pred)]
        confidence = round(max(pred) * 100, 2)

        print(f"Pose: {pose} | Confidence: {confidence}%")

        # ============================
        # FIXED HEATMAP CODE (NO DISTORTION)
        # ============================

        ax.cla()  # clears axes but keeps figure stable

        sns.heatmap(
            mat,
            cmap="turbo",
            vmin=0,
            vmax=4095,
            cbar=True,
            square=True,   # 🔥 ensures proper square grid
            ax=ax
        )

        ax.set_title(f"Pose: {pose} ({confidence}%)", fontsize=14)
        ax.set_xlabel("")
        ax.set_ylabel("")
        plt.tight_layout()

        plt.pause(0.001)

        # ============================
        # SAVE LOG IF ENABLED
        # ============================

        if SAVE_DATA:
            row = list(mat.flatten()) + [pose, confidence]
            df_log = pd.concat([df_log, pd.DataFrame([row])], ignore_index=True)
            df_log.to_csv(SAVE_FILE, index=False)

    except KeyboardInterrupt:
        print("\nStopped by user.")
        break

    except Exception as e:
        print("Error:", e)
