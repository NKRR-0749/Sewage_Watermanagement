"""
treatment_pipeline.py — Purify REAL polluted water through the five treatment phase agents.

Input:  real USGS readings (data/real/usgs_water_quality_multistate_2024.csv) that break
        the water quality limits, sampled from every state.
Flow:   S1 Screening -> S2 Primary -> S3 Secondary -> S4 Chemical -> S5 Tertiary -> PureWaterAgent
Output: data/processed/treatment_pipeline_results.csv
"""

import os
import pandas as pd

from agents.monitoring_agent import MonitoringAgent
from agents.phase_agents import TreatmentPlant
from utils.communication import MessageBus

FEATURES = ["pH", "DO", "turbidity", "temperature"]
SAMPLES_PER_STATE = 25


def load_polluted_samples(csv_path):
    """Pick real readings that break at least one water quality limit, evenly from each state."""
    df = pd.read_csv(csv_path, dtype={"site_no": str})
    df[FEATURES] = df[FEATURES].round(2)
    polluted = df[
        (df["pH"] < 6.0) | (df["pH"] > 8.5) | (df["DO"] < 4.0) | (df["turbidity"] > 30.0)
    ]
    return polluted.groupby("state").sample(n=SAMPLES_PER_STATE, random_state=42).reset_index(drop=True)


def format_readings(r):
    return (f"pH={r['pH']:<5} DO={r['DO']:<6} "
            f"turbidity={r['turbidity']:<7} temp={r['temperature']}")


def print_trace(sample, result):
    """Show how one sample moves through every phase."""
    print(f"\nExample: {sample['station_name']} ({sample['state']}), {sample['datetime_utc']}")
    print(f"  RAW       {format_readings(sample)}")
    for report in result["reports"]:
        line = (f"  P{report['pass']} {report['station']} {report['phase']:<10} "
                f"{format_readings(report['outflow'])}  cycles={report['cycles']}")
        if "ml_status" in report:
            line += f"  ML={report['ml_status']} ({report['ml_score']:.2f})"
        print(line)
    verdict = "PURE WATER" if result["is_pure"] else f"NOT PURE (fails: {result['failing']})"
    print(f"  RESULT    {verdict} after {result['passes']} pass(es)")


def main():
    print("=" * 80)
    print("  Intelligent Sewage Water Monitoring System")
    print("  Phase Agents -- Purify Real Polluted Water (S1 -> S5)")
    print("=" * 80)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, "data", "real", "usgs_water_quality_multistate_2024.csv")
    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at {csv_path}")
        print("Run: python ml/fetch_real_data.py")
        return

    samples = load_polluted_samples(csv_path)
    print(f"Loaded {len(samples)} real polluted samples from {samples['state'].nunique()} states.")

    monitor = MonitoringAgent()
    monitor.USE_ML = True
    monitor.load_ml_model()

    bus = MessageBus()
    plant = TreatmentPlant(bus, monitor=monitor)

    rows = []
    phase_rows = []
    for step, sample in samples.iterrows():
        raw = {f: float(sample[f]) for f in FEATURES}
        result = plant.purify(raw, step=step)

        if step == samples["turbidity"].idxmax():
            print_trace(sample, result)

        intake = result["reports"][0]
        rows.append({
            "state": sample["state"],
            "site_no": sample["site_no"],
            "station_name": sample["station_name"],
            "datetime_utc": sample["datetime_utc"],
            **{f"raw_{f}": raw[f] for f in FEATURES},
            "ml_intake_status": intake["ml_status"],
            "ml_intake_score": intake["ml_score"],
            **{f"final_{f}": result["final"][f] for f in FEATURES},
            "passes": result["passes"],
            "is_pure": result["is_pure"],
            "failing": ",".join(result["failing"]),
        })
        for report in result["reports"]:
            phase_rows.append({
                "phase": f"{report['station']} {report['phase']}",
                "treated": report["cycles"] > 0,
                "cycles": report["cycles"],
                "met": report["status"] == "TARGETS_MET",
            })

    results = pd.DataFrame(rows)
    phases = pd.DataFrame(phase_rows)

    print("\n" + "-" * 80)
    print("  Phase agent performance")
    print("-" * 80)
    phase_summary = phases.groupby("phase", sort=False).agg(
        runs=("cycles", "size"),
        treated_pct=("treated", lambda s: s.mean() * 100),
        avg_cycles=("cycles", "mean"),
        targets_met_pct=("met", lambda s: s.mean() * 100),
    )
    print(phase_summary.round(2).to_string())

    print("\n" + "-" * 80)
    print("  Results by state")
    print("-" * 80)
    state_summary = results.groupby("state").agg(
        samples=("is_pure", "size"),
        ml_flagged_pct=("ml_intake_status", lambda s: (s == "ANOMALY").mean() * 100),
        pure_pct=("is_pure", lambda s: s.mean() * 100),
        avg_passes=("passes", "mean"),
    )
    print(state_summary.round(2).to_string())

    print("\n" + "-" * 80)
    print("  Average water quality: raw vs final")
    print("-" * 80)
    for f in FEATURES:
        print(f"  {f:<12} raw={results[f'raw_{f}'].mean():>8.2f}   final={results[f'final_{f}'].mean():>8.2f}")

    pure = results["is_pure"].sum()
    print(f"\nPure water produced: {pure}/{len(results)} samples ({pure / len(results) * 100:.1f}%)")
    print(f"Messages exchanged on the bus: {len(bus.messages)}")

    out_path = os.path.join(base_dir, "data", "processed", "treatment_pipeline_results.csv")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    results.to_csv(out_path, index=False)
    print(f"Saved results to: {out_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()
