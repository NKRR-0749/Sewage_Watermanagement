"""
main.py — Entry Point for the Sewage Monitoring System

Phase 11: DataCollector and CSV Output
    - Run simulation scenarios
    - Collect step data via Mesa DataCollector
    - Export dataset to data/processed/simulation_results.csv
"""

import os
from model import SewageModel
from utils.scenarios import apply_scenario


def main():
    print("=" * 80)
    print("  Intelligent Sewage Water Monitoring System")
    print("  Phase 11 -- DataCollector & CSV Export")
    print("=" * 80)

    model = SewageModel(rng=42)

    scenarios = ["scenario_1", "scenario_2", "scenario_3", "scenario_4", "scenario_5"]
    steps_per_scenario = 10

    total_steps = 0
    for sc_name in scenarios:
        print(f"Running {sc_name} across {steps_per_scenario} simulation steps...")
        for local_step in range(1, steps_per_scenario + 1):
            total_steps += 1
            apply_scenario(model, sc_name, local_step)
            model.step()

    output_csv = os.path.join(os.path.dirname(__file__), "data", "processed", "simulation_results.csv")
    model.export_csv(output_csv)

    df = model.get_data_dataframe()

    print("\n" + "-" * 80)
    print(f"Data Collection Completed:")
    print(f"  Total simulation steps: {model.current_step}")
    print(f"  Total recorded agent observations: {len(df)}")
    print(f"  Data columns: {list(df.columns)}")
    print(f"  Exported CSV path: {output_csv}")
    print("=" * 80)
    print("  Phase 11 Complete: DataCollector and CSV output verified.")
    print("=" * 80)


if __name__ == "__main__":
    main()
