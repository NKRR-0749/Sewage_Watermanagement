"""
fetch_real_data.py -- Download REAL water quality measurements from USGS, multi-state.

Source: USGS National Water Information System (public, no API key)
        Site search:  https://waterservices.usgs.gov/nwis/site/
        Readings:     https://waterservices.usgs.gov/nwis/iv/

Parameters (USGS parameter codes) matching the four features used by the agents:
    00400  pH                        (standard units)
    00300  Dissolved oxygen          (mg/L)
    63680  Turbidity, near-IR LED    (FNU)
    00010  Water temperature         (deg C)

Quality control applied, in order:
    1. Only sites that report ALL four parameters are considered.
    2. Missing-value flags (-999999) are removed.
    3. 15-minute readings are averaged to hourly values so the four parameters line up.
    4. Hours where any parameter is missing are dropped.
    5. Physically impossible values are removed.
    6. Sites with less than MIN_COVERAGE of the year are dropped.

Output: data/real/usgs_water_quality_multistate_2024.csv
"""

import os
import csv
import io
import json
import http.client
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

import pandas as pd

# States covering different regions of the US (East, Mid-Atlantic, Midwest, South, West)
STATES = ["MD", "VA", "PA", "NY", "OH", "FL", "TX", "CA"]

# How many qualifying sites to keep per state
SITES_PER_STATE = 5

PARAMS = {
    "00400": "pH",
    "00300": "DO",
    "63680": "turbidity",
    "00010": "temperature",
}

START_DATE = "2024-01-01"
END_DATE = "2024-12-31"

# Keep a site only if it has readings for at least this share of the hours in the year
MIN_COVERAGE = 0.80
HOURS_IN_YEAR = 366 * 24

# Physically possible ranges. Anything outside these is a sensor fault, not water quality.
VALID_RANGES = {
    "pH": (0.0, 14.0),
    "DO": (0.0, 20.0),
    "turbidity": (0.0, 1000.0),
    "temperature": (-1.0, 40.0),
}

MISSING_VALUE_FLAG = -999999.0


def read_url(url, attempts=3):
    """Read a URL, retrying on transient network errors (large USGS responses can be cut off)."""
    for attempt in range(1, attempts + 1):
        try:
            with urllib.request.urlopen(url, timeout=300) as response:
                return response.read()
        except (urllib.error.URLError, http.client.HTTPException, TimeoutError):
            if attempt == attempts:
                raise


def discover_sites(state):
    """Return the list of (site_no, station_name) in a state that report all four parameters."""
    url = (
        "https://waterservices.usgs.gov/nwis/site/?format=rdb"
        f"&stateCd={state}&siteType=ST&siteStatus=active&hasDataTypeCd=iv"
        f"&parameterCd={','.join(PARAMS)}"
    )
    text = read_url(url).decode("utf-8")

    lines = [line for line in text.splitlines() if not line.startswith("#")]
    reader = csv.DictReader(io.StringIO("\n".join(lines)), delimiter="\t")
    rows = [row for row in reader if row.get("site_no") and not row["site_no"].endswith("s")]
    return [(row["site_no"], row["station_nm"]) for row in rows]


def fetch_site(site_no, station_name, state):
    """Download all four parameter series for one site, quality-control, and return hourly rows."""
    url = (
        "https://waterservices.usgs.gov/nwis/iv/?format=json"
        f"&sites={site_no}"
        f"&parameterCd={','.join(PARAMS)}"
        f"&startDT={START_DATE}&endDT={END_DATE}"
    )
    payload = json.loads(read_url(url))

    hourly = {}
    for series in payload["value"]["timeSeries"]:
        code = series["variable"]["variableCode"][0]["value"]
        name = PARAMS[code]
        readings = [
            (item["dateTime"], float(item["value"]))
            for item in series["values"][0]["value"]
            if float(item["value"]) != MISSING_VALUE_FLAG
        ]
        if not readings:
            continue
        times, values = zip(*readings)
        raw = pd.Series(values, index=pd.to_datetime(list(times), utc=True)).sort_index()
        hourly[name] = raw.resample("h").mean()

    if set(hourly) != set(PARAMS.values()):
        return None

    table = pd.DataFrame(hourly).dropna()
    if len(table) < MIN_COVERAGE * HOURS_IN_YEAR:
        return None

    table.insert(0, "state", state)
    table.insert(1, "site_no", site_no)
    table.insert(2, "station_name", station_name)
    table.index.name = "datetime_utc"
    return table.reset_index()


def safe_fetch_site(site_no, station_name, state):
    """Like fetch_site, but a site that still fails after retries is skipped instead of stopping the run."""
    try:
        return fetch_site(site_no, station_name, state)
    except (urllib.error.URLError, http.client.HTTPException, TimeoutError, KeyError, ValueError) as error:
        print(f"  skipped {site_no}: {error}")
        return None


def collect_state(state):
    """Fetch up to SITES_PER_STATE qualifying sites for one state."""
    candidates = discover_sites(state)
    print(f"{state}: {len(candidates)} candidate sites found")

    # Fetch in small batches so we stop downloading once enough sites qualify
    kept = []
    with ThreadPoolExecutor(max_workers=8) as pool:
        for start in range(0, len(candidates), 8):
            batch = candidates[start:start + 8]
            results = pool.map(lambda c: safe_fetch_site(c[0], c[1], state), batch)
            kept.extend(table for table in results if table is not None)
            if len(kept) >= SITES_PER_STATE:
                break
    kept = kept[:SITES_PER_STATE]
    print(f"{state}: kept {len(kept)} sites")
    return kept


def main():
    print("=" * 80)
    print("  Intelligent Sewage Water Monitoring System")
    print("  Fetch Real Water Quality Data (USGS NWIS, multi-state)")
    print("=" * 80)

    frames = []
    for state in STATES:
        frames.extend(collect_state(state))

    if not frames:
        print("Error: no usable sites returned data.")
        return

    data = pd.concat(frames, ignore_index=True)
    print(f"\nTotal hourly records before range check: {len(data)}")

    before = len(data)
    for column, (low, high) in VALID_RANGES.items():
        data = data[data[column].between(low, high)]
    print(f"Removed {before - len(data)} physically impossible records.")

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = os.path.join(base_dir, "data", "real")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "usgs_water_quality_multistate_2024.csv")
    data.to_csv(out_path, index=False)

    print(f"Saved {len(data)} real records from {data['site_no'].nunique()} sites "
          f"in {data['state'].nunique()} states to:\n{out_path}")
    print("\nFetch complete.")


if __name__ == "__main__":
    main()
