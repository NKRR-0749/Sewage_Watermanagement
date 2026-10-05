"""
station_config.py — Reusable Station Class

This file defines the Station class, which is the BLUEPRINT for all five
stations in our simulated sewage network.

WHY a reusable class?
    Instead of writing the same code five times (once per station), we write
    ONE class and create five OBJECTS from it. This is called DRY —
    "Don't Repeat Yourself". If we need to change how stations work, we
    change ONE file instead of five.

Each station has:
    - name:       A label like "S1", "S2", etc.
    - upstream:   The station BEFORE this one (where water comes from)
    - downstream: The station AFTER this one (where water goes)
    - readings:   Current water quality values (pH, DO, turbidity, temperature)
"""


class Station:
    """
    Represents one location in the simulated sewage/wastewater network.

    Attributes:
        name (str):           Station identifier, e.g. "S1"
        upstream (str|None):  Name of the upstream station, or None if first
        downstream (str|None): Name of the downstream station, or None if last
        readings (dict):      Current water quality readings
    """

    def __init__(self, name, upstream=None, downstream=None):
        """
        Constructor — runs automatically when you create a Station object.

        Args:
            name (str):       Station name, e.g. "S1"
            upstream (str):   Name of upstream station (None for the first station)
            downstream (str): Name of downstream station (None for the last station)
        """
        self.name = name                # Store the station name
        self.upstream = upstream        # Store who is before us
        self.downstream = downstream    # Store who is after us

        # Initialize water quality readings with default "normal" values.
        # These are simulation starting values, NOT real-world measurements.
        self.readings = {
            "pH": 7.0,            # Neutral pH (scale 0-14)
            "DO": 6.0,            # Dissolved Oxygen in mg/L
            "turbidity": 20.0,    # Turbidity in NTU (Nephelometric Turbidity Units)
            "temperature": 25.0   # Temperature in degrees Celsius
        }

    def get_info(self):
        """
        Returns a dictionary with all station information.
        Useful for printing/logging the station state.
        """
        return {
            "name": self.name,
            "upstream": self.upstream,
            "downstream": self.downstream,
            "readings": self.readings
        }

    def __repr__(self):
        """
        Controls what you see when you print() a Station object.
        Without this, print(s1) would show something like:
            <station_config.Station object at 0x7f...>
        With this, it shows:
            Station(S1, upstream=None, downstream=S2)
        """
        return (
            f"Station({self.name}, "
            f"upstream={self.upstream}, "
            f"downstream={self.downstream})"
        )
