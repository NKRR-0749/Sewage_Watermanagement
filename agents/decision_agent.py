"""
agents/decision_agent.py — Decision Formulation & Treatment Prescription
"""

from utils.communication import Message

class DecisionAgent:
    """
    Evaluates diagnosis messages and prescribes treatment commands
    with specific chemical, biological, or physical interventions.
    """
    def __init__(self):
        pass

    def process_diagnosis(self, diagnosis_msg):
        """
        Translates diagnosis into actionable treatment commands.
        """
        diag = diagnosis_msg.content or {}
        status = diag.get("status", "NORMAL")
        params = diag.get("parameters", [])
        severity = diag.get("severity", "NORMAL")

        treatment_required = (status == "ANOMALY")
        prescriptions = []

        if treatment_required:
            for p in params:
                if p == "DO":
                    prescriptions.append("AERATION")
                elif p == "turbidity":
                    prescriptions.append("FILTRATION")
                elif p == "pH":
                    prescriptions.append("NEUTRALIZATION")
                elif p == "temperature":
                    prescriptions.append("COOLING")
                elif p == "ML_DETECTED":
                    prescriptions.extend(["AERATION", "FILTRATION"])

            if not prescriptions:
                prescriptions.append("GENERAL_PURIFICATION")

        decision_content = {
            "station": diagnosis_msg.station,
            "treatment_required": treatment_required,
            "prescriptions": list(set(prescriptions)),
            "severity": severity,
            "status": status
        }

        return Message(
            sender="DecisionAgent",
            receiver="TreatmentAgent",
            step=diagnosis_msg.step,
            station=diagnosis_msg.station,
            msg_type="DECISION_COMMAND",
            content=decision_content
        )
