"""
station_5.py — Station S5 Configuration

S5 is the DOWNSTREAM-MOST station.
    - Upstream neighbor: S4
    - It has NO downstream neighbor (treated water exits the network here).
"""

from station_config import Station

station_5 = Station(
    name="S5",
    upstream="S4",
    downstream=None     # No station after S5 — water exits the network here
)
