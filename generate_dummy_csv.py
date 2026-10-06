import pandas as pd
import numpy as np
import os

os.makedirs('data/processed', exist_ok=True)

stations = ['S1', 'S2', 'S3', 'S4', 'S5']
data = []
for step in range(1, 51):
    for s in stations:
        is_anomaly = np.random.rand() > 0.8
        data.append({
            'Unnamed: 0': len(data),
            'step': step,
            'station': s,
            'pH': round(np.random.normal(7.0, 0.2), 2),
            'DO': round(np.random.normal(6.0, 0.5) - (2.0 if is_anomaly else 0.0), 2),
            'turbidity': round(np.random.normal(20.0, 2.0) + (30.0 if is_anomaly else 0.0), 2),
            'temperature': round(np.random.normal(25.0, 1.0), 2),
            'status': 'ANOMALY' if is_anomaly else 'NORMAL',
            'anomaly_score': round(np.random.uniform(0.7, 1.0) if is_anomaly else np.random.uniform(0.0, 0.3), 2),
            'suspected_source': s if is_anomaly else 'NONE',
            'propagation_detected': False,
            'treatment_required': is_anomaly,
            'treatment_cycles': np.random.randint(1, 4) if is_anomaly else 0,
            'treatment_success': True
        })

df = pd.DataFrame(data)
df.to_csv('data/processed/simulation_results.csv', index=False)
print('Generated dummy data.')
