from agents.monitoring_agent import MonitoringAgent

def test_phase16():
    print("=" * 80)
    print("  Intelligent Sewage Water Monitoring System")
    print("  Phase 16 -- Connecting ML to MonitoringAgent")
    print("=" * 80)

    # Initialize the Agent
    monitor = MonitoringAgent()
    
    # We will feed it a simulated "Polluted" water reading
    polluted_water = {
        "pH": 6.8,          # Normal
        "DO": 2.5,          # Very Low (Polluted)
        "turbidity": 45.0,  # Very High (Polluted)
        "temperature": 26.0
    }

    print("\n--- 1. Testing with Baseline RULE-BASED System (USE_ML = False) ---")
    monitor.USE_ML = False
    rule_report = monitor.check_readings("S3", polluted_water)
    print(f"Report: {rule_report}")

    print("\n--- 2. Testing with MACHINE LEARNING System (USE_ML = True) ---")
    monitor.USE_ML = True
    ml_report = monitor.check_readings("S3", polluted_water)
    print(f"Report: {ml_report}")
    
    print("\nPhase 16 testing complete.")

if __name__ == '__main__':
    test_phase16()
