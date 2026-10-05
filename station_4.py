"""
station_4.py — Station S4 Configuration

S4 is the fourth station in the network.
    - Upstream neighbor: S3
    - Downstream neighbor: S5
"""

from station_config import Station

station_4 = Station(
    name="S4",
    upstream="S3",
    downstream="S5"
)
