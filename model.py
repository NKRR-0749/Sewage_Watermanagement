"""
model.py — Mesa Model Implementation for Sewage Monitoring System

This module defines the Mesa Model (SewageModel) and Agent wrappers
compatible with Mesa 3.x.

Key Classes:
    - SewageStationAgent (mesa.Agent): Represents a station node holding SensorAgent and MonitoringAgent
    - SewageModel (mesa.Model): The multi-agent simulation environment
"""

import mesa

from station_1 import station_1
from station_2 import station_2
from station_3 import station_3
from station_4 import station_4
from station_5 import station_5

from agents.sensor_agent import SensorAgent
from agents.monitoring_agent import MonitoringAgent
from agents.analysis_agent import AnalysisAgent
from agents.decision_agent import DecisionAgent
from agents.treatment_agent import TreatmentAgent
from utils.communication import Message, MessageBus


class SewageStationAgent(mesa.Agent):
    """
    A Mesa Agent representing one Station node in the sewage network.
    Wraps SensorAgent and MonitoringAgent.
    """

    def __init__(self, model, station_config):
        super().__init__(model)
        self.station_config = station_config
        self.station_name = station_config.name

        self.sensor = SensorAgent(self.station_name)
        self.monitor = MonitoringAgent()

        self.last_report = None
        self.last_decision = None
        self.last_treatment = None

    def step(self):
        """
        Step logic:
        1. SensorAgent reads/generates water quality.
        2. MonitoringAgent checks readings.
        3. If anomaly detected, send Message -> AnalysisAgent -> DecisionAgent.
        """
        if self.model.pollution_event and self.model.pollution_target == self.station_name:
            self.sensor.previous_readings = self.sensor.current_readings.copy()
            self.sensor.current_readings = self.model.pollution_data.copy()
            self.sensor.step_count += 1
        else:
            self.sensor.generate_readings()

        # Monitoring Agent Check
        self.last_report = self.monitor.check_readings(
            station_name=self.station_name,
            current_readings=self.sensor.get_readings(),
            previous_readings=self.sensor.get_previous_readings()
        )

        # ── Communication Pipeline ─────────────────────────────────────────
        # Create ANOMALY_ALERT message from MonitoringAgent
        alert_msg = Message(
            sender=f"MonitoringAgent_{self.station_name}",
            receiver="AnalysisAgent",
            step=self.model.current_step,
            station=self.station_name,
            msg_type="ANOMALY_ALERT",
            content=self.last_report
        )
        self.model.message_bus.send_message(alert_msg)

        # AnalysisAgent processes alert and generates diagnosis
        diagnosis_msg = self.model.analysis_agent.process_alert(alert_msg)
        self.model.message_bus.send_message(diagnosis_msg)

        # DecisionAgent processes diagnosis and generates command
        decision_msg = self.model.decision_agent.process_diagnosis(diagnosis_msg)
        self.model.message_bus.send_message(decision_msg)

        self.last_decision = decision_msg.content


class SewageModel(mesa.Model):
    """
    Mesa Simulation Model for the 5-Station Sewage Network.
    """

    def __init__(self, rng=None):
        super().__init__(rng=rng)

        self.current_step = 0
        self.message_bus = MessageBus()
        self.analysis_agent = AnalysisAgent()
        self.decision_agent = DecisionAgent()
        self.treatment_agent = TreatmentAgent()

        self.station_configs = [station_1, station_2, station_3, station_4, station_5]
        self.stations = {}

        for cfg in self.station_configs:
            agent = SewageStationAgent(model=self, station_config=cfg)
            self.stations[cfg.name] = agent

        self.pollution_injections = {}
        self.latest_network_analysis = {
            "suspected_source": "NONE",
            "propagation_detected": False,
            "network_status": "CLEAN"
        }

        # Initialize Mesa DataCollector with a custom agent reporter function
        self.datacollector = mesa.DataCollector(
            agent_reporters={
                "step": lambda a: a.model.current_step,
                "station": lambda a: a.station_name,
                "pH": lambda a: a.sensor.get_readings().get("pH"),
                "DO": lambda a: a.sensor.get_readings().get("DO"),
                "turbidity": lambda a: a.sensor.get_readings().get("turbidity"),
                "temperature": lambda a: a.sensor.get_readings().get("temperature"),
                "status": lambda a: a.last_report.get("status") if a.last_report else "NORMAL",
                "anomaly_score": lambda a: a.last_report.get("anomaly_score") if a.last_report else 0.0,
                "suspected_source": lambda a: a.model.latest_network_analysis.get("suspected_source"),
                "propagation_detected": lambda a: a.model.latest_network_analysis.get("propagation_detected"),
                "treatment_required": lambda a: a.last_decision.get("treatment_required") if a.last_decision else False,
                "treatment_cycles": lambda a: getattr(a, "treatment_cycles", 0),
                "treatment_success": lambda a: getattr(a, "treatment_success", True)
            }
        )

    def inject_pollution(self, station_name, pollution_data):
        """
        Injects custom pollution data into a specific station for the next step.
        """
        self.pollution_injections[station_name] = pollution_data

    def clear_pollution_injection(self):
        """Clears active manual injection dictionary."""
        self.pollution_injections = {}

    def step(self):
        """
        Advance the simulation by one step.
        Calls step() on all station agents in topological order (S1 -> S5).
        """
        self.current_step += 1

        # Pass 1: Sensor reading updates & local monitoring checks
        step_reports = {}
        for cfg in self.station_configs:
            agent = self.stations[cfg.name]

            if cfg.name in self.pollution_injections:
                agent.sensor.previous_readings = agent.sensor.current_readings.copy()
                agent.sensor.current_readings = self.pollution_injections[cfg.name].copy()
                agent.sensor.step_count += 1
            else:
                agent.sensor.generate_readings()

            agent.last_report = agent.monitor.check_readings(
                station_name=cfg.name,
                current_readings=agent.sensor.get_readings(),
                previous_readings=agent.sensor.get_previous_readings()
            )
            step_reports[cfg.name] = agent.last_report

        # Pass 2: Spatial Network Analysis across S1 -> S5
        self.latest_network_analysis = self.analysis_agent.analyze_network(step_reports, self.current_step)

        # Pass 3: Communication, Treatment & Post-Treatment Feedback Loop
        MAX_TREATMENT_CYCLES = 3

        for cfg in self.station_configs:
            agent = self.stations[cfg.name]

            cycle_count = 0
            treatment_success = False

            while cycle_count < MAX_TREATMENT_CYCLES:
                # 1. Monitoring Agent Check on current water state
                agent.last_report = agent.monitor.check_readings(
                    station_name=cfg.name,
                    current_readings=agent.sensor.get_readings(),
                    previous_readings=agent.sensor.get_previous_readings()
                )

                # Send ANOMALY_ALERT message
                alert_msg = Message(
                    sender=f"MonitoringAgent_{cfg.name}",
                    receiver="AnalysisAgent",
                    step=self.current_step,
                    station=cfg.name,
                    msg_type="ANOMALY_ALERT",
                    content=agent.last_report
                )
                self.message_bus.send_message(alert_msg)

                # 2. AnalysisAgent Diagnosis
                diagnosis_msg = self.analysis_agent.process_alert(alert_msg, self.latest_network_analysis)
                self.message_bus.send_message(diagnosis_msg)

                # 3. DecisionAgent Command
                decision_msg = self.decision_agent.process_diagnosis(diagnosis_msg)
                self.message_bus.send_message(decision_msg)
                agent.last_decision = decision_msg.content

                # Check if decision calls for treatment
                if not decision_msg.content["treatment_required"]:
                    treatment_success = True
                    break  # Water is clean, no further treatment cycles needed

                cycle_count += 1

                # 4. Treatment Agent Execution
                post_treatment_readings, treatment_report_msg = self.treatment_agent.process_decision(
                    decision_msg, agent.sensor.get_readings()
                )
                self.message_bus.send_message(treatment_report_msg)
                agent.last_treatment = treatment_report_msg.content

                # Update current station state with post-treatment readings
                agent.sensor.current_readings = post_treatment_readings

                # 5. Post-Treatment Monitoring Verification
                post_check_report = agent.monitor.check_readings(
                    station_name=cfg.name,
                    current_readings=post_treatment_readings,
                    previous_readings=None
                )

                if post_check_report["status"] == "NORMAL":
                    treatment_success = True
                    agent.last_treatment["status"] = "TREATED_SUCCESSFULLY"
                    break
                else:
                    agent.last_treatment["status"] = "ADDITIONAL_TREATMENT_REQUIRED"

            agent.treatment_cycles = cycle_count
            agent.treatment_success = treatment_success

        # Collect step metrics into Mesa DataCollector
        self.datacollector.collect(self)

        # Clear injection flag after step completes
        self.clear_pollution_injection()

    def get_data_dataframe(self):
        """Returns collected simulation data as a Pandas DataFrame."""
        return self.datacollector.get_agent_vars_dataframe()

    def export_csv(self, filepath):
        """
        Exports collected simulation data to a CSV file.

        Args:
            filepath (str): Absolute or relative output CSV filepath.
        """
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        df = self.get_data_dataframe()
        df.to_csv(filepath)
        return filepath
