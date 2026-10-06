import os
import joblib
import warnings

# Suppress sklearn warnings about feature names for cleaner output
warnings.filterwarnings("ignore", category=UserWarning)

class MonitoringAgent:
    """
    Agent responsible for analyzing sensor data to detect anomalies.
    """
    def __init__(self):
        # PHASE 16 REQUIREMENT: Toggle for ML vs Rules
        self.USE_ML = False
        self.ml_model = None
        
        # Hard-coded rule thresholds (Baseline)
        self.thresholds = {
            "pH_min": 6.0, "pH_max": 8.5,
            "DO_min": 4.0,
            "turbidity_max": 30.0
        }

    def load_ml_model(self):
        model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ml', 'saved_model.pkl')
        if os.path.exists(model_path):
            self.ml_model = joblib.load(model_path)
            print("MonitoringAgent: ML Model loaded successfully!")
        else:
            print("MonitoringAgent: ML model not found. Falling back to rule-based.")
            self.USE_ML = False

    def check_readings(self, station_name, current_readings, previous_readings=None):
        """Main analysis function. Routes to Rules or ML based on toggle."""
        if self.USE_ML:
            if self.ml_model is None:
                self.load_ml_model()
            return self._ml_detection(station_name, current_readings)
        else:
            return self._rule_based_detection(station_name, current_readings)
            
    def _rule_based_detection(self, station_name, current_readings):
        """Uses hard-coded scientific thresholds."""
        abnormal_params = []
        score = 0.0

        if current_readings["pH"] < self.thresholds["pH_min"] or current_readings["pH"] > self.thresholds["pH_max"]:
            abnormal_params.append("pH")
            score += 0.3
        if current_readings["DO"] < self.thresholds["DO_min"]:
            abnormal_params.append("DO")
            score += 0.4
        if current_readings["turbidity"] > self.thresholds["turbidity_max"]:
            abnormal_params.append("turbidity")
            score += 0.3

        status = "ANOMALY" if len(abnormal_params) > 0 else "NORMAL"

        return {
            "station": station_name,
            "status": status,
            "parameters": abnormal_params,
            "anomaly_score": round(score, 2)
        }
        
    def _ml_detection(self, station_name, current_readings):
        """Uses the trained Isolation Forest ML model."""
        # Format the data exactly as the model expects (pH, DO, Turbidity, Temp)
        features = [[
            current_readings["pH"], 
            current_readings["DO"], 
            current_readings["turbidity"], 
            current_readings["temperature"]
        ]]
        
        # predict() returns 1 for Normal (inlier), -1 for Anomaly (outlier)
        prediction = self.ml_model.predict(features)[0]
        
        # score_samples() gives raw anomaly score. We convert it to a 0.0 - 1.0 format
        raw_score = self.ml_model.score_samples(features)[0]
        anomaly_score = max(0.0, min(1.0, abs(raw_score) * 1.5))

        status = "ANOMALY" if prediction == -1 else "NORMAL"
        abnormal_params = ["ML_DETECTED"] if status == "ANOMALY" else []

        return {
            "station": station_name,
            "status": status,
            "parameters": abnormal_params,
            "anomaly_score": round(anomaly_score, 2)
        }
