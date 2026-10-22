import pandas as pd
import os
from sklearn.ensemble import IsolationForest
import joblib

FEATURES = ['pH', 'DO', 'turbidity', 'temperature']

# Standard water quality limits used by the rule-based MonitoringAgent
RULE_VIOLATION = (
    lambda df: (df['pH'] < 6.0) | (df['pH'] > 8.5) | (df['DO'] < 4.0) | (df['turbidity'] > 30.0)
)

def evaluate_by_state(df):
    """
    Leave-one-state-out evaluation.
    For each state, the model is trained on the OTHER states and then scores the held-out state.
    This tests whether the model still works on river conditions it has never seen.
    """
    print("\n" + "-" * 80)
    print("  Per-state results (trained on other states, tested on held-out state)")
    print("-" * 80)
    print(f"{'STATE':<7} | {'ROWS':>7} | {'ML FLAGGED %':>13} | {'RULE VIOLATION %':>17} | {'ML FLAGS ALSO RULE %':>21}")
    print("-" * 80)

    for state in sorted(df['state'].unique()):
        train = df[df['state'] != state]
        test = df[df['state'] == state]

        model = IsolationForest(contamination=0.1, random_state=42)
        model.fit(train[FEATURES])

        flagged = model.predict(test[FEATURES]) == -1
        rule = RULE_VIOLATION(test).values

        flagged_pct = flagged.mean() * 100
        rule_pct = rule.mean() * 100
        overlap_pct = (flagged & rule).sum() / max(flagged.sum(), 1) * 100

        print(f"{state:<7} | {len(test):>7} | {flagged_pct:>13.2f} | {rule_pct:>17.2f} | {overlap_pct:>21.2f}")

    print("-" * 80)

def train_anomaly_detector():
    print("=" * 80)
    print("  Intelligent Sewage Water Monitoring System")
    print("  Phase 15 -- Train ML Anomaly Detection Model")
    print("=" * 80)

    # 1. Load the REAL multi-state dataset (USGS measurements, see ml/fetch_real_data.py)
    base_dir = os.path.dirname(os.path.dirname(__file__))
    csv_path = os.path.join(base_dir, 'data', 'real', 'usgs_water_quality_multistate_2024.csv')

    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at {csv_path}")
        print("Run: python ml/fetch_real_data.py")
        return

    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} real records from {df['site_no'].nunique()} sites "
          f"in {df['state'].nunique()} states.")

    # 2. Select Features for Training
    # We only want the ML model to look at the water quality numbers.
    X = df[FEATURES]

    print(f"Training Data Shape: {X.shape} (rows, columns)")

    # 3. Evaluate on each state separately before the final fit
    evaluate_by_state(df)

    print("\nTraining final Isolation Forest model on all states...")

    # 4. Initialize and Train the Model
    # contamination = 0.1 means we expect roughly 10% of our data to be anomalies
    model = IsolationForest(contamination=0.1, random_state=42)
    model.fit(X)

    # 5. Save the trained model to a file
    model_path = os.path.join(os.path.dirname(__file__), 'saved_model.pkl')
    joblib.dump(model, model_path)

    print(f"Success! Model trained and saved to: {model_path}")
    print("\nPhase 15 training complete.")

if __name__ == '__main__':
    train_anomaly_detector()
