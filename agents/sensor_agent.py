import random

class SensorAgent:
    """
    Simulates a hardware sensor module at a sewage station.
    It reads/generates water quality data (pH, DO, Turbidity, Temperature).
    """
    
    def __init__(self, station_name):
        self.station_name = station_name
        
        # We start with normal baseline readings
        self.current_readings = {
            "pH": 7.0,
            "DO": 6.0,
            "turbidity": 20.0,
            "temperature": 25.0
        }
        # Keep track of previous readings for temporal analysis later
        self.previous_readings = None

    def generate_readings(self):
        """
        Simulates taking a new sensor reading. 
        For now, we add small random variations to the current readings.
        """
        self.previous_readings = self.current_readings.copy()
        
        # Simulate slight natural variations in water quality
        self.current_readings["pH"] += random.uniform(-0.1, 0.1)
        self.current_readings["DO"] += random.uniform(-0.2, 0.2)
        self.current_readings["turbidity"] += random.uniform(-1.0, 1.0)
        self.current_readings["temperature"] += random.uniform(-0.1, 0.1)
        
        # Ensure values stay within physically realistic bounds
        self.current_readings["pH"] = round(max(0, min(14, self.current_readings["pH"])), 2)
        self.current_readings["DO"] = round(max(0, self.current_readings["DO"]), 2)
        self.current_readings["turbidity"] = round(max(0, self.current_readings["turbidity"]), 2)
        self.current_readings["temperature"] = round(self.current_readings["temperature"], 2)
        
    def get_readings(self):
        return self.current_readings

    def get_previous_readings(self):
        return self.previous_readings
