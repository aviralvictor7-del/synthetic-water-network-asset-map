"""
total_accurate_pipe_length.py

Problem
    In a utility network, not all mapped pipes are considered accurate.
    Some may be provisional, legacy, or awaiting survey. For reporting
    and QA, it is useful to know the total length of only those pipes
    flagged as accurate.

Goal
    Sum the total length of all "accurate" pipes and report the result.
    Accuracy is defined by an attribute flag (e.g., AccurateFlag = 'Y').

Layers and fields (generic, safe for public repositories)
    Distribution_Pipe_FC  - line feature class representing distribution pipes
    AccurateFlag          - text field storing 'Y' for accurate, 'N' for others
    Pipe_Length           - optional numeric field storing per-pipe length
                            (for example calculated via Shape.STLength())

Usage
    1. Add Distribution_Pipe_FC to the active map in ArcGIS Pro.
    2. Ensure the layer is stored in a projected coordinate system
       with linear units (e.g. meters or feet).
    3. Run this script in the Python window or as a script tool.
    4. Review the printed totals in the Python console.

Notes
    - The script uses the SHAPE@LENGTH geometry token to read each
      feature's length in the layer's coordinate system units.
    - If a length field (Pipe_Length) exists, the script will also
      compute a second total from that field for comparison.
"""

import arcpy

arcpy.env.overwriteOutput = True

# --- Configuration (rename here if your layer/fields differ) ---
PIPE_LAYER_NAME   = "Distribution_Pipe_FC"
ACCURATE_FIELD    = "AccurateFlag"   # text field with 'Y' for accurate
LENGTH_FIELD_NAME = "Pipe_Length"    # optional; set to None if you don't have it

# --- Get active map and pipe layer ---
aprx = arcpy.mp.ArcGISProject("CURRENT")
m = aprx.activeMap

pipe_layer = None
for lyr in m.listLayers():
    if lyr.isFeatureLayer and lyr.name == PIPE_LAYER_NAME:
        pipe_layer = lyr
        break

if pipe_layer is None:
    raise RuntimeError(f"Layer '{PIPE_LAYER_NAME}' not found in the active map.")

# --- Build where clause: only accurate pipes (AccurateFlag = 'Y') ---
where_clause = (
    f"{arcpy.AddFieldDelimiters(pipe_layer, ACCURATE_FIELD)} = 'Y'"
)

# --- Decide which fields to read ---
fields = ["SHAPE@LENGTH"]
has_length_field = False

if LENGTH_FIELD_NAME is not None:
    field_names = [f.name for f in arcpy.ListFields(pipe_layer)]
    if LENGTH_FIELD_NAME in field_names:
        fields.append(LENGTH_FIELD_NAME)
        has_length_field = True

total_geom_length = 0.0     # from SHAPE@LENGTH
total_field_length = 0.0    # from Pipe_Length (if present)

# --- Iterate over accurate pipes and accumulate length ---
with arcpy.da.SearchCursor(pipe_layer, fields, where_clause) as cursor:
    for row in cursor:
        geom_length = float(row[0]) if row[0] is not None else 0.0
        total_geom_length += geom_length

        if has_length_field:
            field_length = row[1]
            if field_length is not None:
                total_field_length += float(field_length)

# --- Report results ---
units_note = " (layer coordinate units, e.g. meters or feet)"

print("=== Accurate pipe length ===")
print(f"Geometry total (SHAPE@LENGTH): {total_geom_length:.3f}{units_note}")

if has_length_field:
    print(f"Field total ({LENGTH_FIELD_NAME}):  {total_field_length:.3f}{units_note}")
    diff = total_geom_length - total_field_length
    print(f"Difference (geom - field):      {diff:.6f}{units_note}")
else:
    print(f"No '{LENGTH_FIELD_NAME}' field found; only geometry total reported.")
