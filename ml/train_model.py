import pandas as pd
import os
from sklearn.ensemble import IsolationForest
import joblib

def train_anomaly_detector():
    print("=" * 80)
    print("  Intelligent Sewage Water Monitoring System")
    print("  Phase 15 -- Train ML Anomaly Detection Model")
    print("=" * 80)

    # 1. Load the dataset
    base_dir = os.path.dirname(os.path.dirname(__file__))
    csv_path = os.path.join(base_dir, 'data', 'processed', 'simulation_results.csv')

    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at {csv_path}")
        return

    df = pd.read_csv(csv_path)

    # 2. Select Features for Training
    # We only want the ML model to look at the water quality numbers.
    features = ['pH', 'DO', 'turbidity', 'temperature']
    X = df[features]

    print(f"Training Data Shape: {X.shape} (rows, columns)")
    print("Training Isolation Forest model...")

    # 3. Initialize and Train the Model
    # contamination = 0.1 means we expect roughly 10% of our data to be anomalies
    model = IsolationForest(contamination=0.1, random_state=42)
    model.fit(X)

    # 4. Save the trained model to a file
    model_path = os.path.join(os.path.dirname(__file__), 'saved_model.pkl')
    joblib.dump(model, model_path)

    print(f"Success! Model trained and saved to: {model_path}")
    print("\nPhase 15 training complete.")

if __name__ == '__main__':
    train_anomaly_detector()
