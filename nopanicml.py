# train_model.py
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib
import numpy as np

# Generate synthetic data
np.random.seed(42)
data = []

for _ in range(1000):
    raw = np.random.uniform(30000, 100000)
    gsr = np.random.uniform(0.1, 2.0)
    temp = np.random.uniform(34.5, 38.5)

    # Rule-based labeling
    if raw > 80000 and gsr > 1.5 and temp > 36.5:
        label = 1  # Panic
    else:
        label = 0  # Normal

    data.append([raw, gsr, temp, label])

df = pd.DataFrame(data, columns=["Raw Value", "GSR Voltage", "Temperature", "Panic"])

# Train-test split
X = df[["Raw Value", "GSR Voltage", "Temperature"]]
y = df["Panic"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Train model
model = RandomForestClassifier()
model.fit(X_train, y_train)

# Save model
joblib.dump(model, "panic_model.pkl")
print("Model trained and saved.")
