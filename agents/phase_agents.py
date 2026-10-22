"""
agents/phase_agents.py — Treatment Phase Agents (one agent per treatment phase)

Water flows through five treatment phases, one per station (S1 -> S5).
Each phase agent:
    1. DETECTS which parameters in the incoming water miss that phase's targets
    2. TREATS the water, repeating treatment cycles until the targets are met
    3. HANDS OFF the treated water to the next phase via the MessageBus

After the last phase, the PureWaterAgent checks the water against drinking
water standards. If it is not pure yet, the water is recirculated to S1.

Phase       Station  Process                              Targets
---------------------------------------------------------------------------------
Screening   S1       Bar screens + grit removal (+ ML)    turbidity <= 150
Primary     S2       Sedimentation tanks                  turbidity <= 30
Secondary   S3       Biological aeration                  DO >= 6.0, turbidity <= 10
Chemical    S4       pH neutralization + cooling          pH 6.5-8.5, temperature <= 30
Tertiary    S5       Filtration + disinfection            turbidity <= 1.0, DO >= 6.0
"""

from utils.communication import Message


def do_saturation(temperature):
    """Maximum dissolved oxygen (mg/L) fresh water can hold at a given temperature (deg C)."""
    t = temperature
    return 14.62 - 0.3898 * t + 0.006969 * t ** 2 - 0.00005897 * t ** 3


def aerate(readings, efficiency):
    """Move DO toward saturation. Aeration cannot push DO above what the water can hold."""
    saturation = do_saturation(readings["temperature"])
    if readings["DO"] < saturation:
        readings["DO"] = round(readings["DO"] + efficiency * (saturation - readings["DO"]), 2)
    return readings


class PhaseAgent:
    """
    Base class for one treatment phase.
    Subclasses define failing_parameters() (detection) and treat() (one treatment cycle).
    """
    name = "Phase"
    station = ""
    process = ""
    max_cycles = 5

    def __init__(self, monitor=None):
        # Only the intake phase gets the ML MonitoringAgent: the model was trained on raw
        # river water, so it is meaningful for incoming water, not for already-treated water.
        self.monitor = monitor

    def failing_parameters(self, readings):
        """Return the parameters that do not yet meet this phase's targets."""
        raise NotImplementedError

    def treat(self, readings):
        """Apply one treatment cycle and return the new readings."""
        raise NotImplementedError

    def process_water(self, readings, step, bus, next_receiver):
        """Detect, treat until targets are met, then hand the water off to the next phase."""
        inflow = dict(readings)
        current = dict(readings)

        report = {"phase": self.name, "station": self.station, "process": self.process}

        if self.monitor is not None:
            ml_report = self.monitor.check_readings(self.station, inflow)
            report["ml_status"] = ml_report["status"]
            report["ml_score"] = float(ml_report["anomaly_score"])

        detected = self.failing_parameters(current)
        cycles = 0
        while self.failing_parameters(current) and cycles < self.max_cycles:
            current = self.treat(current)
            cycles += 1

        remaining = self.failing_parameters(current)
        report.update({
            "detected": detected,
            "cycles": cycles,
            "inflow": inflow,
            "outflow": current,
            "remaining": remaining,
            "status": "TARGETS_MET" if not remaining else "TARGETS_NOT_MET",
        })

        bus.send_message(Message(
            sender=f"{self.name}Agent",
            receiver=next_receiver,
            step=step,
            station=self.station,
            msg_type="PHASE_HANDOFF",
            content=report
        ))
        return current, report


class ScreeningAgent(PhaseAgent):
    """S1 — Removes large solids and grit. Also runs the ML anomaly check on raw water."""
    name = "Screening"
    station = "S1"
    process = "Bar screens + grit removal"

    def failing_parameters(self, readings):
        return ["turbidity"] if readings["turbidity"] > 150.0 else []

    def treat(self, readings):
        readings = dict(readings)
        readings["turbidity"] = round(readings["turbidity"] * 0.75, 2)
        return readings


class PrimaryTreatmentAgent(PhaseAgent):
    """S2 — Settling tanks let suspended solids sink out of the water."""
    name = "Primary"
    station = "S2"
    process = "Sedimentation"

    def failing_parameters(self, readings):
        return ["turbidity"] if readings["turbidity"] > 30.0 else []

    def treat(self, readings):
        readings = dict(readings)
        readings["turbidity"] = round(readings["turbidity"] * 0.5, 2)
        return readings


class SecondaryTreatmentAgent(PhaseAgent):
    """S3 — Aeration tanks restore oxygen; microbes break down organic matter, which settles out."""
    name = "Secondary"
    station = "S3"
    process = "Biological aeration"

    def failing_parameters(self, readings):
        failing = []
        if readings["DO"] < 6.0:
            failing.append("DO")
        if readings["turbidity"] > 10.0:
            failing.append("turbidity")
        return failing

    def treat(self, readings):
        readings = aerate(dict(readings), efficiency=0.6)
        readings["turbidity"] = round(readings["turbidity"] * 0.7, 2)
        return readings


class ChemicalTreatmentAgent(PhaseAgent):
    """S4 — Doses acid or alkali to bring pH into range, and cools hot water."""
    name = "Chemical"
    station = "S4"
    process = "pH neutralization + cooling"

    def failing_parameters(self, readings):
        failing = []
        if not 6.5 <= readings["pH"] <= 8.5:
            failing.append("pH")
        if readings["temperature"] > 30.0:
            failing.append("temperature")
        return failing

    def treat(self, readings):
        readings = dict(readings)
        # Move pH toward 7.2 by at most 1.0 unit per dose
        gap = 7.2 - readings["pH"]
        readings["pH"] = round(readings["pH"] + max(-1.0, min(1.0, gap)), 2)
        if readings["temperature"] > 30.0:
            readings["temperature"] = round(readings["temperature"] - 2.0, 2)
        return readings


class TertiaryTreatmentAgent(PhaseAgent):
    """S5 — Sand/membrane filtration polishes turbidity, post-aeration tops up DO, then disinfection."""
    name = "Tertiary"
    station = "S5"
    process = "Filtration + disinfection"

    def failing_parameters(self, readings):
        failing = []
        if readings["turbidity"] > 1.0:
            failing.append("turbidity")
        if readings["DO"] < 6.0:
            failing.append("DO")
        return failing

    def treat(self, readings):
        readings = aerate(dict(readings), efficiency=0.6)
        readings["turbidity"] = round(max(0.05, readings["turbidity"] * 0.2), 2)
        return readings

    def process_water(self, readings, step, bus, next_receiver):
        current, report = super().process_water(readings, step, bus, next_receiver)
        # Pathogens are not measured by the four sensors, so disinfection is always applied
        report["disinfection"] = "UV + chlorine contact applied"
        return current, report


class PureWaterAgent:
    """
    Final quality gate. Checks treated water against drinking water standards
    (WHO / US EPA): pH 6.5-8.5, turbidity <= 1 NTU. DO >= 6 mg/L and
    temperature <= 30 C are added so the water is also fresh and stable.
    """
    STANDARDS = {
        "pH": (6.5, 8.5),
        "turbidity": (0.0, 1.0),
        "DO": (6.0, float("inf")),
        "temperature": (float("-inf"), 30.0),
    }

    def verify(self, readings):
        """Return the list of parameters that fail the pure water standards."""
        return [
            param for param, (low, high) in self.STANDARDS.items()
            if not low <= readings[param] <= high
        ]


class TreatmentPlant:
    """
    Runs water through all five phase agents in order (S1 -> S5) and verifies the result.
    Water that is not pure after a pass is recirculated, up to max_passes times.
    """
    def __init__(self, bus, monitor=None, max_passes=3):
        self.bus = bus
        self.phases = [
            ScreeningAgent(monitor),
            PrimaryTreatmentAgent(),
            SecondaryTreatmentAgent(),
            ChemicalTreatmentAgent(),
            TertiaryTreatmentAgent(),
        ]
        self.verifier = PureWaterAgent()
        self.max_passes = max_passes

    def purify(self, readings, step):
        """
        Returns:
            dict: final readings, purity verdict, number of passes and every phase report.
        """
        current = dict(readings)
        reports = []

        for pass_no in range(1, self.max_passes + 1):
            for index, phase in enumerate(self.phases):
                is_last = index == len(self.phases) - 1
                next_receiver = "PureWaterAgent" if is_last else f"{self.phases[index + 1].name}Agent"
                current, report = phase.process_water(current, step, self.bus, next_receiver)
                report["pass"] = pass_no
                reports.append(report)

            failing = self.verifier.verify(current)
            if not failing:
                self.bus.send_message(Message(
                    sender="PureWaterAgent", receiver="Distribution", step=step, station="S5",
                    msg_type="PURE_WATER_CERTIFICATE", content={"readings": current, "passes": pass_no}
                ))
                return {"is_pure": True, "passes": pass_no, "final": current, "failing": [], "reports": reports}

            self.bus.send_message(Message(
                sender="PureWaterAgent", receiver="ScreeningAgent", step=step, station="S5",
                msg_type="RECIRCULATE", content={"readings": current, "failing": failing}
            ))

        return {"is_pure": False, "passes": self.max_passes, "final": current, "failing": failing, "reports": reports}
