"""
agents/analysis_agent.py — Spatial Network Analysis & Anomaly Source Localization
"""

from utils.communication import Message

class AnalysisAgent:
    """
    Analyzes spatial propagation across stations (S1 -> S5) to determine
    the root source of pollution and evaluate network health.
    """
    def __init__(self):
        self.station_order = ["S1", "S2", "S3", "S4", "S5"]

    def analyze_network(self, step_reports, current_step):
        """
        Analyzes the reports across all stations for spatial correlation.
        """
        anomalous_stations = [
            s for s in self.station_order
            if step_reports.get(s, {}).get("status") == "ANOMALY"
        ]

        if not anomalous_stations:
            return {
                "suspected_source": "NONE",
                "propagation_detected": False,
                "network_status": "CLEAN"
            }

        # Root source is the most upstream station showing an anomaly
        suspected_source = anomalous_stations[0]
        propagation_detected = len(anomalous_stations) > 1

        return {
            "suspected_source": suspected_source,
            "propagation_detected": propagation_detected,
            "network_status": "POLLUTED"
        }

    def process_alert(self, alert_msg, network_analysis=None):
        """
        Processes an individual ANOMALY_ALERT from a station MonitoringAgent
        and constructs a DIAGNOSIS message for the DecisionAgent.
        """
        network_analysis = network_analysis or {}
        content = alert_msg.content or {}
        status = content.get("status", "NORMAL")
        score = content.get("anomaly_score", 0.0)

        if status == "ANOMALY":
            severity = "CRITICAL" if score >= 0.7 else "WARNING"
        else:
            severity = "NORMAL"

        diagnosis_content = {
            "station": alert_msg.station,
            "status": status,
            "severity": severity,
            "anomaly_score": score,
            "parameters": content.get("parameters", []),
            "suspected_source": network_analysis.get("suspected_source", alert_msg.station if status == "ANOMALY" else "NONE"),
            "propagation_detected": network_analysis.get("propagation_detected", False)
        }

        return Message(
            sender="AnalysisAgent",
            receiver="DecisionAgent",
            step=alert_msg.step,
            station=alert_msg.station,
            msg_type="DIAGNOSIS",
            content=diagnosis_content
        )
