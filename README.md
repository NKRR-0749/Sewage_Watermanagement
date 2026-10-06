# Intelligent Sewage Water Monitoring, Analysis, Treatment and Management using MESA Multi-Agent System

## Project Overview
This project is a Python-based **Multi-Agent System (MAS)** simulation using the Mesa framework. It simulates a 5-station wastewater treatment network, demonstrating intelligent decision-making for pollution detection and treatment.

## Key Features
- **Multi-Agent Architecture**: Uses specialized agents (Sensor, Monitoring, Analysis, Decision, Treatment).
- **Dual-Detection System**: Features both a baseline **Rule-Based** system and a Machine Learning **Isolation Forest** anomaly detection system.
- **Simulated Treatment**: Mathematically simulates filtration, aeration, and biological treatments based on severity.
- **Automated Data Collection**: Collects step-by-step metrics into a CSV for analysis.

## Setup and Installation
1. Install requirements: pip install -r requirements.txt
2. Run the main simulation: python main.py
3. Generate Visualizations: python visualize.py
4. Calculate Metrics: python utils/metrics.py
5. Compare Rule-Based vs ML: python ml/compare_models.py
"@

Set-Content -Path "REPORT_MATERIAL.md" -Value @"
# Final Report Material

## 1. Architecture Explanation
The system follows a decentralized multi-agent architecture arranged sequentially across 5 simulated stations (S1 -> S5):
1. **SensorAgent**: Generates real-time water quality readings (pH, DO, Turbidity, Temp).
2. **MonitoringAgent**: Receives data and flags anomalies using either strict thresholds (Rules) or an Isolation Forest model (ML).
3. **AnalysisAgent**: Infers the likely source of pollution by analyzing spatial propagation across the network.
4. **DecisionAgent**: Classifies the severity of the anomaly (WARNING/CRITICAL) and prescribes a treatment plan.
5. **TreatmentAgent**: Mathematically simulates the purification process (e.g., Aeration increases DO, Filtration reduces Turbidity).

## 2. Flowchart
\\\mermaid
graph TD
    A[Raw Wastewater] --> B[SensorAgent Reads Data]
    B --> C{MonitoringAgent}
    C -->|Normal| D[Pass Downstream]
    C -->|Anomaly| E[AnalysisAgent Spatial Check]
    E --> F[DecisionAgent Classifies Severity]
    F --> G[TreatmentAgent Applies Simulation]
    G --> H[Post-Treatment Sensor Reading]
    H --> C
\\\

## 3. Results & Experiment Table
| Metric | Rule-Based System | ML-Based System (Isolation Forest) |
|--------|-------------------|------------------------------------|
| **Approach** | Hard-coded thresholds | Unsupervised Pattern Recognition |
| **Detection Time** | Faster (Simple logic) | Slightly slower (Matrix operations) |
| **Adaptability** | Rigid, requires manual updates | High, learns from data distribution |

*(Note: Copy the exact numeric accuracy/time from your Phase 17 output into your final report).*

## 4. Limitations
- **Simulation Only**: The treatment processes (Filtration, Aeration) are mathematical simulations, not physical realities.
- **Unsupervised Learning Limit**: The ML model detects *unusual* data, but cannot strictly classify the *type* of pollution without a labeled supervised dataset.
- **Agent Communication Overhead**: In a real distributed system, communication between 5 agents across 5 stations would introduce network latency.

## 5. Future Scope
- **IoT Integration**: Replace the SensorAgent's simulated random values with real-time API feeds from physical Arduino/ESP32 water sensors.
- **Supervised Deep Learning**: Implement a Neural Network trained on a fully labeled dataset to predict exact pathogen levels.
- **Web Dashboard**: Build a live React/Flask web application for remote monitoring of the agent network.
