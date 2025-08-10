
import csv                          # csv handles quoted fields and embedded commas correctly
from classes import Body, Spacecraft  # import your domain classes (assumed to be defined in classes.py)

# Path constants (change these to point at your actual files)
EARTH_CSV_PATH = r"C:/Users/jacks/Documents/Astrodynamics Engine/Sim Presets/earth_system.csv"
SPACECRAFT_CSV_PATH = r"C:/Users/jacks/Documents/Astrodynamics Engine/Sim Presets/spacecraft.csv"


# -----------------------------
# Load bodies from CSV
# -----------------------------
bodies = []  # final list of Body instances we will build from the CSV rows

# open the CSV file using newline='' (recommended when using csv module) and an explicit encoding
with open(EARTH_CSV_PATH, mode='r', newline='', encoding='utf-8') as csvfile:
    # Create a csv.reader. skipinitialspace=True removes spaces after delimiters (e.g. "a, b" -> "b" stripped)
    reader = csv.reader(csvfile, skipinitialspace=True)

    # Iterate over rows returned by csv.reader
    for row in reader:
        # row is a list of strings representing the CSV fields for that line

        # Skip entirely empty rows (row might be [] or contain only empty strings)
        if not row or all(not cell.strip() for cell in row):
            # nothing to parse on this row: move to the next line
            continue

        # Allow comment lines beginning with '#' in the first cell (helpful for annotated CSVs)
        first_cell = row[0].strip()
        if first_cell.startswith('#'):
            # This row is a comment; skip it
            continue

        # At this point row is a candidate body row.
        # Expected format (per your original code): x, y, vx, vy, m, r, name, color
        # Check length to avoid IndexError and detect malformed rows
        if len(row) < 8:
            # If there are fewer than 8 fields, skip the row and optionally print a warning.
            # Using print here for simplicity; you could use logging instead.
            print(f"Skipping malformed body row (expected >= 8 columns): {row}")
            continue

        # Parse numeric fields safely with try/except to handle malformed numbers
        try:
            # Convert the first 6 fields to float as appropriate
            x = float(row[0].strip())   # x position
            y = float(row[1].strip())   # y position
            vx = float(row[2].strip())  # x velocity
            vy = float(row[3].strip())  # y velocity
            m = float(row[4].strip())   # mass
            r = float(row[5].strip())   # radius
        except ValueError as exc:
            # If conversion fails, skip this row and report the problem
            print(f"Skipping body row due to number conversion error: {row} -> {exc}")
            continue

        # The remaining fields are expected to be string-like (name and color).
        # csv.reader already handles quotes, so a field like "\"Voyager\"" will be returned as 'Voyager'.
        name = row[6].strip()
        color = row[7].strip()

        # Create Body instance using the parsed values
        body = Body(x, y, vx, vy, m, r, name, color)

        # Append the Body to our collection
        bodies.append(body)


# -----------------------------
# Load spacecraft from CSV
# -----------------------------
# We'll read only the first non-empty, non-comment row as the spacecraft properties,
# then collect remaining rows (if any) as burn commands (each burn should have +t, Δv_x, Δv_y).
spacecrafts = []  # resulting list of Spacecraft objects (you previously created one; we follow that pattern)

with open(SPACECRAFT_CSV_PATH, mode='r', newline='', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile, skipinitialspace=True)

    # Build a filtered list of rows that are neither empty nor commented out.
    # This makes it easy to take the first row as properties and the rest as burns.
    meaningful_rows = []
    for row in reader:
        # skip blank rows
        if not row or all(not cell.strip() for cell in row):
            continue
        # skip comment rows that begin with '#' in the first cell
        if row[0].strip().startswith('#'):
            continue
        # otherwise collect the row
        meaningful_rows.append(row)

    # If there are no meaningful rows, nothing to construct
    if not meaningful_rows:
        # You may want to raise an exception or log a warning instead
        print(f"No spacecraft data found in {SPACECRAFT_CSV_PATH!r}")
    else:
        # The first meaningful row is treated as the spacecraft properties line
        prop_row = meaningful_rows[0]

        # Expected CSV order (per your latest format): 
        # name, color, x, y, vx, vy, m, m_p, r, Isp, thrust
        expected_prop_count = 11  # number of expected fields
        if len(prop_row) < expected_prop_count:
            # If there are fewer fields than expected, warn and attempt to proceed conservatively.
            print(f"Warning: spacecraft properties row has {len(prop_row)} fields (expected {expected_prop_count}). Row: {prop_row}")

        # Helper to safely get a field by index (returns "" if missing)
        def get_field(row_list, idx):
            try:
                return row_list[idx].strip()
            except IndexError:
                return ""

        # Extract each property with safe indexing
        name = get_field(prop_row, 0)       # csv.reader already unquotes quoted fields
        color = get_field(prop_row, 1)
        x_str = get_field(prop_row, 2)
        y_str = get_field(prop_row, 3)
        vx_str = get_field(prop_row, 4)
        vy_str = get_field(prop_row, 5)
        m_str = get_field(prop_row, 6)
        m_p_str = get_field(prop_row, 7)
        r_str = get_field(prop_row, 8)
        Isp_str = get_field(prop_row, 9)
        thrust_str = get_field(prop_row, 10)

        # Convert numeric strings to floats with error handling. If conversion fails, set to 0.0 (or choose another sentinel)
        def to_float_or_default(s, default=0.0):
            """Convert s to float, returning default if conversion fails or s is empty."""
            if s == "":
                return default
            try:
                return float(s)
            except ValueError:
                print(f"Warning: could not convert '{s}' to float; using default {default}")
                return default

        x = to_float_or_default(x_str)
        y = to_float_or_default(y_str)
        vx = to_float_or_default(vx_str)
        vy = to_float_or_default(vy_str)
        m = to_float_or_default(m_str)
        m_p = to_float_or_default(m_p_str)
        r = to_float_or_default(r_str)
        Isp = to_float_or_default(Isp_str)
        thrust = to_float_or_default(thrust_str)

        # Construct Spacecraft instance.
        # Note: I'm passing the arguments in the same order you used previously:
        # Spacecraft(name, color, x, y, vx, vy, m, m_p, r, Isp, thrust)
        spacecraft = Spacecraft(name, color, x, y, vx, vy, m, m_p, r, Isp, thrust)

        # Now parse burn commands from the remaining rows (if any)
        burns = []  # list of (t, dvx, dvy) tuples

        for burn_row in meaningful_rows[1:]:
            # Each burn row is expected to have at least 3 columns: +t, Δv_x, Δv_y
            if len(burn_row) < 3:
                print(f"Skipping malformed burn row (expected >=3 columns): {burn_row}")
                continue

            # Extract strings, then convert to floats where appropriate
            t_str = burn_row[0].strip()
            dvx_str = burn_row[1].strip()
            dvy_str = burn_row[2].strip()

            # Convert to floats using the helper (defaults to 0.0 on error)
            t = to_float_or_default(t_str)
            dvx = to_float_or_default(dvx_str)
            dvy = to_float_or_default(dvy_str)

            burns.append((t, dvx, dvy))

        # Attach burns to the spacecraft object if you want to keep them together.
        # This assumes Spacecraft is ok with a 'burns' attribute - if not, you can manage burns separately.
        spacecraft.burns = burns

        # Finally, add this spacecraft to the collection
        spacecrafts.append(spacecraft)


# At this point:
# - `bodies` is a list of Body objects loaded from earth_system.csv
# - `spacecrafts` is a list containing one Spacecraft (from spacecraft.csv) whose .burns is a list of tuples
#
# You can now proceed to use `bodies` and `spacecrafts` in the rest of your simulation.
#
# Example quick-check prints (optional)
print(f"Loaded {len(bodies)} bodies.")
print(f"Loaded {len(spacecrafts)} spacecraft(s).")
if spacecrafts:
    print(f"First spacecraft name: {spacecrafts[0].name!r}, burns: {len(spacecrafts[0].burns)}")
