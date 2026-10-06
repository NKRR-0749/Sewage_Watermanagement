import pandas as pd
import os

def calculate_metrics():
    print("=" * 80)
    print("  Intelligent Sewage Water Monitoring System")
    print("  Phase 13 -- Performance Metrics")
    print("=" * 80)

    # Resolve CSV path
    base_dir = os.path.dirname(os.path.dirname(__file__))
    csv_path = os.path.join(base_dir, 'data', 'processed', 'simulation_results.csv')

    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at {csv_path}")
        print("Please run the main simulation first.")
        return

    df = pd.read_csv(csv_path)

    # 1. Treatment Success Rate
    # Calculate for rows where treatment was required
    treatment_events = df[df['treatment_required'] == True]
    if len(treatment_events) > 0:
        success_count = len(treatment_events[treatment_events['treatment_success'] == True])
        success_rate = (success_count / len(treatment_events)) * 100
    else:
        success_rate = 100.0  # No treatment needed means 100% naturally successful

    # 2. Average Number of Treatment Cycles
    # Only average over events that actually required treatment
    if len(treatment_events) > 0:
        avg_cycles = treatment_events['treatment_cycles'].mean()
    else:
        avg_cycles = 0.0

    # 3. Anomaly Detection Count
    # Number of times status was not NORMAL
    anomaly_count = len(df[df['status'] != 'NORMAL'])

    # 4. Propagation Detection Count
    propagation_count = len(df[df['propagation_detected'] == True])

    print("\n--- SYSTEM PERFORMANCE REPORT ---")
    print(f"Total Simulation Steps Recorded:  {len(df['step'].unique())}")
    print(f"Total Station Observations:       {len(df)}")
    print(f"Total Anomalies Detected:         {anomaly_count}")
    print(f"Pollution Propagations Detected:  {propagation_count}")
    print(f"Treatments Activated:             {len(treatment_events)}")
    print(f"Treatment Success Rate:           {success_rate:.2f}%")
    print(f"Average Treatment Cycles (when needed): {avg_cycles:.2f}")
    print("---------------------------------")
    print("\nPhase 13 metrics calculation complete.")

if __name__ == '__main__':
    calculate_metrics()
