"""
station_2.py — Station S2 Configuration

S2 is the second station in the network.
    - Upstream neighbor: S1
    - Downstream neighbor: S3
"""

from station_config import Station

station_2 = Station(
    name="S2",
    upstream="S1",
    downstream="S3"
)
