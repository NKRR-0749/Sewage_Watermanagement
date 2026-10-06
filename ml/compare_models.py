import pandas as pd
import os
import time
from agents.monitoring_agent import MonitoringAgent

def compare_systems():
    print("=" * 80)
    print("  Intelligent Sewage Water Monitoring System")
    print("  Phase 17 -- Rule-Based vs ML Comparison")
    print("=" * 80)

    # 1. Load Data
    base_dir = os.path.dirname(os.path.dirname(__file__))
    csv_path = os.path.join(base_dir, 'data', 'processed', 'simulation_results.csv')
    df = pd.read_csv(csv_path)

    # We use the original 'status' column from our simulation as the "Ground Truth"
    ground_truth = df['status'].tolist()

    # Initialize Agent
    agent = MonitoringAgent()

    # --- Evaluate Rule-Based System ---
    agent.USE_ML = False
    start_time = time.time()
    
    rule_predictions = []
    for index, row in df.iterrows():
        readings = {"pH": row["pH"], "DO": row["DO"], "turbidity": row["turbidity"], "temperature": row["temperature"]}
        report = agent.check_readings(row["station"], readings)
        rule_predictions.append(report["status"])
        
    rule_time = time.time() - start_time

    # --- Evaluate ML-Based System ---
    agent.USE_ML = True
    agent.load_ml_model() # Load it outside the loop to properly measure inference time
    start_time = time.time()
    
    ml_predictions = []
    for index, row in df.iterrows():
        readings = {"pH": row["pH"], "DO": row["DO"], "turbidity": row["turbidity"], "temperature": row["temperature"]}
        report = agent.check_readings(row["station"], readings)
        ml_predictions.append(report["status"])
        
    ml_time = time.time() - start_time

    # --- Calculate Metrics Function ---
    def calculate_metrics(predictions, truth):
        correct = 0
        fp = 0  # False Positive: Agent said ANOMALY, but it was NORMAL
        fn = 0  # False Negative: Agent said NORMAL, but it was actually ANOMALY
        for p, t in zip(predictions, truth):
            if p == t:
                correct += 1
            elif p == "ANOMALY" and t == "NORMAL":
                fp += 1
            elif p == "NORMAL" and t == "ANOMALY":
                fn += 1
        accuracy = (correct / len(truth)) * 100
        return accuracy, fp, fn

    rule_acc, rule_fp, rule_fn = calculate_metrics(rule_predictions, ground_truth)
    ml_acc, ml_fp, ml_fn = calculate_metrics(ml_predictions, ground_truth)

    # --- Print Report ---
    print("\n" + "=" * 65)
    print(f"{'METRIC':<20} | {'RULE-BASED':<15} | {'ML (Isolation Forest)':<20}")
    print("-" * 65)
    print(f"{'Accuracy (%)':<20} | {rule_acc:<15.2f} | {ml_acc:<20.2f}")
    print(f"{'False Positives':<20} | {rule_fp:<15} | {ml_fp:<20}")
    print(f"{'False Negatives':<20} | {rule_fn:<15} | {ml_fn:<20}")
    print(f"{'Total Time (sec)':<20} | {rule_time:<15.4f} | {ml_time:<20.4f}")
    print("=" * 65)
    
    print("\nPhase 17 complete.")

if __name__ == '__main__':
    compare_systems()
