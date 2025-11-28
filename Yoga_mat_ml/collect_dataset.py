import serial
import time
import pandas as pd
import numpy as np

# ============================
# CONFIG
# ============================

PORT = "COM10"      # <- Change only if your ESP32 uses a different port
BAUD = 115200
SAMPLES = 150        # Number of frames to record per pose
LABEL = "hand_press"      # <- CHANGE THIS for each pose you record!

OUTPUT_FILE = f"dataset_{LABEL}.csv"

# ============================
# PARSE FRAME FROM ESP32
# ============================

def parse_frame(line):
    if not line.endswith("END"):
        return None

    # Remove END and trailing commas
    clean = line.replace("END", "").strip().strip(",")
    values = clean.split(",")

    if len(values) != 48:
        return None

    try:
        values = list(map(int, values))
    except:
        return None

    return np.array(values)

# ============================
# MAIN LOGIC
# ============================

print(f"\n=== Collecting {SAMPLES} samples for pose: {LABEL} ===")
print("Starting in 3 seconds...")
time.sleep(3)

ser = serial.Serial(PORT, BAUD, timeout=1, rtscts=False, dsrdtr=False)
print("Connected to ESP32\n")

data = []

while len(data) < SAMPLES:
    line = ser.readline().decode(errors="ignore").strip()
    frame = parse_frame(line)

    if frame is not None:
        row = list(frame) + [LABEL]
        data.append(row)

        print(f"Collected: {len(data)}/{SAMPLES}")

df = pd.DataFrame(data)
df.to_csv(OUTPUT_FILE, index=False)

print(f"\nSaved dataset to: {OUTPUT_FILE}")
print("Done!")
