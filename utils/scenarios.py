"""
utils/scenarios.py — Predefined simulation pollution scenarios
"""

def apply_scenario(model, scenario_name, local_step):
    """
    Applies custom pollution injections according to the scenario and local step.

    Scenarios:
      - scenario_1: Normal operations (baseline fluctuations)
      - scenario_2: Chemical acidic discharge at Station 1 (steps 2-5)
      - scenario_3: Severe organic shock & hypoxia at Station 3 (steps 3-6)
      - scenario_4: Industrial effluent propagating from Station 2 (steps 2-7)
      - scenario_5: Multi-station severe contamination (steps 4-8)
    """
    if scenario_name == "scenario_1":
        # Clean baseline operation
        pass

    elif scenario_name == "scenario_2":
        # Acidic discharge at S1
        if 2 <= local_step <= 5:
            model.inject_pollution("S1", {
                "pH": 4.8,
                "DO": 3.8,
                "turbidity": 48.0,
                "temperature": 27.5
            })

    elif scenario_name == "scenario_3":
        # Severe hypoxia at S3
        if 3 <= local_step <= 6:
            model.inject_pollution("S3", {
                "pH": 6.8,
                "DO": 1.9,
                "turbidity": 55.0,
                "temperature": 28.0
            })

    elif scenario_name == "scenario_4":
        # Propagating pollution starting at S2
        if 2 <= local_step <= 4:
            model.inject_pollution("S2", {
                "pH": 5.4,
                "DO": 3.2,
                "turbidity": 42.0,
                "temperature": 26.5
            })
        elif 5 <= local_step <= 7:
            # Propagating downstream to S3
            model.inject_pollution("S3", {
                "pH": 5.8,
                "DO": 3.5,
                "turbidity": 38.0,
                "temperature": 26.0
            })

    elif scenario_name == "scenario_5":
        # Multi-point heavy contamination
        if 4 <= local_step <= 8:
            model.inject_pollution("S1", {
                "pH": 5.1,
                "DO": 2.5,
                "turbidity": 60.0,
                "temperature": 29.0
            })
            model.inject_pollution("S4", {
                "pH": 9.2,
                "DO": 2.8,
                "turbidity": 52.0,
                "temperature": 27.0
            })
