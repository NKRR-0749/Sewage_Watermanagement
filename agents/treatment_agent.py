"""
agents/treatment_agent.py — Simulated Water Treatment & Purification
"""

from utils.communication import Message

class TreatmentAgent:
    """
    Simulates water purification interventions:
      - Aeration: Boosts Dissolved Oxygen (DO).
      - Filtration: Reduces Turbidity.
      - Neutralization: Restores pH to neutral (7.0).
      - Cooling: Brings high temperatures down.
    """
    def __init__(self):
        pass

    def process_decision(self, decision_msg, current_readings):
        """
        Executes treatment based on prescribed actions and updates readings.
        Returns:
            (dict, Message): (post_treatment_readings, treatment_report_msg)
        """
        dec = decision_msg.content or {}
        prescriptions = dec.get("prescriptions", [])
        post = current_readings.copy()

        applied_actions = []

        for action in prescriptions:
            if action == "AERATION":
                # Increase DO toward normal (~6.0)
                post["DO"] = round(min(8.0, post["DO"] + 2.5), 2)
                applied_actions.append("AERATION_APPLIED")
            elif action == "FILTRATION":
                # Reduce turbidity toward normal (~20.0)
                post["turbidity"] = round(max(15.0, post["turbidity"] - 25.0), 2)
                applied_actions.append("FILTRATION_APPLIED")
            elif action == "NEUTRALIZATION":
                # Nudge pH toward 7.0
                if post["pH"] < 7.0:
                    post["pH"] = round(min(7.0, post["pH"] + 1.2), 2)
                else:
                    post["pH"] = round(max(7.0, post["pH"] - 1.2), 2)
                applied_actions.append("NEUTRALIZATION_APPLIED")
            elif action == "COOLING":
                post["temperature"] = round(max(24.0, post["temperature"] - 3.0), 2)
                applied_actions.append("COOLING_APPLIED")
            elif action == "GENERAL_PURIFICATION":
                post["DO"] = round(min(7.0, post["DO"] + 1.5), 2)
                post["turbidity"] = round(max(18.0, post["turbidity"] - 15.0), 2)
                applied_actions.append("GENERAL_PURIFICATION_APPLIED")

        treatment_content = {
            "station": decision_msg.station,
            "actions_applied": applied_actions,
            "pre_readings": current_readings,
            "post_readings": post,
            "status": "TREATMENT_APPLIED"
        }

        report_msg = Message(
            sender="TreatmentAgent",
            receiver="MonitoringAgent",
            step=decision_msg.step,
            station=decision_msg.station,
            msg_type="TREATMENT_REPORT",
            content=treatment_content
        )

        return post, report_msg
