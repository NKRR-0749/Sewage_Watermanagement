"""
station_1.py — Station S1 Configuration

S1 is the UPSTREAM-MOST station.
    - It has NO upstream neighbor (water enters the network here).
    - Its downstream neighbor is S2.
"""

from station_config import Station

# Create the S1 station object using our reusable Station class
station_1 = Station(
    name="S1",
    upstream=None,      # No station before S1 — this is where sewage enters
    downstream="S2"     # Water flows from S1 to S2
)
