import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from tensorflow.keras import layers, models

# ----------------------------------------
# Load datasets
# ----------------------------------------

poses = ["empty","hand_press"]

dfs = []
for pose in poses:
    file = f"dataset_{pose}.csv"
    print("Loading:", file)
    df = pd.read_csv(file)
    dfs.append(df)

df = pd.concat(dfs, ignore_index=True)

# ----------------------------------------
# Split into X and y
# ----------------------------------------

X = df.iloc[:, :-1].values
y = df.iloc[:, -1].values

# Convert labels to numbers
label_map = {name: i for i, name in enumerate(poses)}
y = np.array([label_map[v] for v in y])

# reshape for CNN
X = X.reshape((-1, 48, 1))

# ----------------------------------------
# Train-test split
# ----------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, shuffle=True
)

# ----------------------------------------
# Build Model
# ----------------------------------------

model = models.Sequential([
    layers.Conv1D(32, 3, activation='relu', input_shape=(48, 1)),
    layers.Conv1D(32, 3, activation='relu'),
    layers.MaxPooling1D(2),
    layers.Conv1D(64, 3, activation='relu'),
    layers.Flatten(),
    layers.Dense(64, activation='relu'),
    layers.Dense(len(poses), activation='softmax')
])

model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# ----------------------------------------
# Train
# ----------------------------------------

model.fit(X_train, y_train, epochs=15, validation_data=(X_test, y_test))

# ----------------------------------------
# Save Model
# ----------------------------------------

model.save("yoga_model.h5")
print("Model saved as yoga_model.h5")
