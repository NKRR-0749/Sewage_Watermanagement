import pandas as pd
import os

def inspect_dataset():
    print("=" * 80)
    print("  Intelligent Sewage Water Monitoring System")
    print("  Phase 14 -- Dataset Inspection")
    print("=" * 80)

    # Resolve CSV path
    base_dir = os.path.dirname(os.path.dirname(__file__))
    csv_path = os.path.join(base_dir, 'data', 'processed', 'simulation_results.csv')

    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at {csv_path}")
        return

    df = pd.read_csv(csv_path)

    print("\n1. COLUMNS & DATA TYPES:")
    print("-" * 30)
    print(df.dtypes)

    print("\n2. MISSING VALUES:")
    print("-" * 30)
    print(df.isnull().sum())

    print("\n3. STATION INFORMATION:")
    print("-" * 30)
    print(f"Stations found: {df['station'].unique()}")

    print("\n4. LABELS AVAILABLE:")
    print("-" * 30)
    # We generated these labels in our simulation
    print("Status labels (Target for supervised, ignore for unsupervised):")
    print(df['status'].value_counts())

    print("\n5. PARAMETER RANGES (Water Quality Features):")
    print("-" * 30)
    features = ['pH', 'DO', 'turbidity', 'temperature']
    print(df[features].describe().loc[['min', 'max', 'mean']])
    
    print("\nPhase 14 inspection complete.")

if __name__ == '__main__':
    inspect_dataset()
