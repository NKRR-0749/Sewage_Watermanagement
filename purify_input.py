"""
purify_input.py — Purify YOUR OWN water readings through the five treatment phase agents.

Input:  pH, DO, turbidity and temperature, typed in when prompted or passed as arguments
Flow:   S1 Screening -> S2 Primary -> S3 Secondary -> S4 Chemical -> S5 Tertiary -> PureWaterAgent

Usage:
    python purify_input.py                                   (asks for the readings)
    python purify_input.py --ph 5.2 --do 2.1 --turbidity 400 --temperature 34
"""

import argparse

from agents.monitoring_agent import MonitoringAgent
from agents.phase_agents import TreatmentPlant
from utils.communication import MessageBus

# (prompt label, unit, lowest allowed, highest allowed)
FEATURES = {
    "pH": ("pH", "0-14", 0.0, 14.0),
    "DO": ("Dissolved oxygen", "mg/L", 0.0, 20.0),
    "turbidity": ("Turbidity", "NTU", 0.0, 10000.0),
    "temperature": ("Temperature", "deg C", 0.0, 50.0),
}


def format_readings(r):
    return (f"pH={r['pH']:<5} DO={r['DO']:<6} "
            f"turbidity={r['turbidity']:<7} temp={r['temperature']}")


def ask_value(feature):
    """Keep asking until the user types a number in the allowed range. Returns None to quit."""
    label, unit, low, high = FEATURES[feature]
    while True:
        text = input(f"  {label} ({unit}): ").strip()
        if text.lower() in ("q", "quit", "exit"):
            return None
        try:
            value = float(text)
        except ValueError:
            print("    Please enter a number (or q to quit).")
            continue
        if not low <= value <= high:
            print(f"    Value must be between {low} and {high}.")
            continue
        return value


def ask_readings():
    print("\nEnter the water readings (q to quit):")
    readings = {}
    for feature in FEATURES:
        value = ask_value(feature)
        if value is None:
            return None
        readings[feature] = value
    return readings


def print_result(raw, result):
    """Show how the water moves through every phase."""
    print(f"\n  RAW       {format_readings(raw)}")
    for report in result["reports"]:
        line = (f"  P{report['pass']} {report['station']} {report['phase']:<10} "
                f"{format_readings(report['outflow'])}  cycles={report['cycles']}")
        if report["detected"]:
            line += f"  treated={','.join(report['detected'])}"
        if "ml_status" in report:
            line += f"  ML={report['ml_status']} ({report['ml_score']:.2f})"
        print(line)
    verdict = "PURE WATER" if result["is_pure"] else f"NOT PURE (fails: {result['failing']})"
    print(f"  RESULT    {verdict} after {result['passes']} pass(es)")


def main():
    parser = argparse.ArgumentParser(description="Run your own water readings through the treatment phases.")
    parser.add_argument("--ph", type=float)
    parser.add_argument("--do", type=float)
    parser.add_argument("--turbidity", type=float)
    parser.add_argument("--temperature", type=float)
    args = parser.parse_args()

    print("=" * 80)
    print("  Intelligent Sewage Water Monitoring System")
    print("  Phase Agents -- Purify Your Water (S1 -> S5)")
    print("=" * 80)

    monitor = MonitoringAgent()
    monitor.USE_ML = True
    monitor.load_ml_model()

    bus = MessageBus()
    plant = TreatmentPlant(bus, monitor=monitor)

    given = [args.ph, args.do, args.turbidity, args.temperature]
    if any(v is not None for v in given):
        if any(v is None for v in given):
            parser.error("give all four: --ph, --do, --turbidity and --temperature")
        raw = dict(zip(FEATURES, given))
        print_result(raw, plant.purify(raw, step=0))
        return

    step = 0
    while True:
        raw = ask_readings()
        if raw is None:
            break
        print_result(raw, plant.purify(raw, step=step))
        step += 1

    print(f"\nMessages exchanged on the bus: {len(bus.messages)}")


if __name__ == "__main__":
    main()
