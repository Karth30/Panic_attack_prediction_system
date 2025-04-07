# train_model.py
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
import numpy as np

# ---------- Synthetic Data Generation ----------
np.random.seed(42)
data = []

for _ in range(1000):
    bpm = np.random.randint(40, 160)                # Simulated BPM
    gsr = np.random.uniform(0.1, 2.0)                # GSR Voltage in Volts
    temp = np.random.uniform(34.5, 38.5)             # Temperature in °C

    # Rule-based labeling for panic detection
    if bpm > 120 and gsr > 0.5 and temp > 36.5:
        label = 1  # Panic
    else:
        label = 0  # Normal

    data.append([bpm, gsr, temp, label])

# ---------- Create DataFrame ----------
df = pd.DataFrame(data, columns=["BPM", "GSR Voltage", "Temperature", "Panic"])

# ---------- Train-Test Split ----------
X = df[["BPM", "GSR Voltage", "Temperature"]]
y = df["Panic"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# ---------- Train Random Forest Classifier ----------
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)
y_predict = model.predict(X_test)

# ---------- Save Trained Model ----------
joblib.dump(model, "panic_model.pkl")
print("Model trained and saved.")
print("Accuracy:", accuracy_score(y_test, y_predict))
