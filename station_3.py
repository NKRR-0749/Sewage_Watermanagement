"""
station_3.py — Station S3 Configuration

S3 is the MIDDLE station in the network.
    - Upstream neighbor: S2
    - Downstream neighbor: S4

In our pollution scenarios, S3 is often where we will inject
simulated pollution events to test the system.
"""

from station_config import Station

station_3 = Station(
    name="S3",
    upstream="S2",
    downstream="S4"
)
