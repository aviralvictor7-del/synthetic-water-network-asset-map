"""
select_isolated_service_lines.py

Problem
    In a utility network, some service lines may not be connected to any
    consumer meter or to any other service line. These “isolated” service lines
    can indicate abandoned assets, digitizing errors, or incomplete edits that
    require QA.

Goal
    Select all service lines that:
        - Do NOT intersect any other service line, and
        - Do NOT intersect any consumer meter.

Layers (generic, safe for public repositories)
    Service_Line_FC    - line feature class representing service lines
    Consumer_Meter_FC  - point feature class representing consumer meters

Usage
    1. Add Service_Line_FC and Consumer_Meter_FC to the active map.
    2. Open the Python window in ArcGIS Pro (or run as a script tool).
    3. Run this script. The isolated service lines remain selected in the map.

Note
    The connectivity rule here is simple geometric intersection. For strict
    endpoint-only logic, this can be extended using more advanced geometry
    checks or Utility Network traces.
"""

import arcpy

arcpy.env.overwriteOutput = True

SERVICE_LAYER_NAME = "Service_Line_FC"
METER_LAYER_NAME = "Consumer_Meter_FC"

aprx = arcpy.mp.ArcGISProject("CURRENT")
m = aprx.activeMap

service_layer = None
meter_layer = None

for lyr in m.listLayers():
    if not lyr.isFeatureLayer:
        continue
    if lyr.name == SERVICE_LAYER_NAME:
        service_layer = lyr
    elif lyr.name == METER_LAYER_NAME:
        meter_layer = lyr

if service_layer is None:
    raise RuntimeError(f"Layer '{SERVICE_LAYER_NAME}' not found in the active map.")

if meter_layer is None:
    raise RuntimeError(f"Layer '{METER_LAYER_NAME}' not found in the active map.")

# Clear existing selection
arcpy.management.SelectLayerByAttribute(service_layer, "CLEAR_SELECTION")

# Step 1: select service lines that intersect ANY other service line
arcpy.management.SelectLayerByLocation(
    in_layer=service_layer,
    overlap_type="INTERSECT",
    select_features=service_layer,
    search_distance=None,
    selection_type="NEW_SELECTION"
)

# Invert the selection to keep only service lines with NO intersecting neighbors
arcpy.management.SelectLayerByAttribute(service_layer, "SWITCH_SELECTION")

# Step 2: remove any line that touches a consumer meter (those are not isolated)
arcpy.management.SelectLayerByLocation(
    in_layer=service_layer,
    overlap_type="INTERSECT",
    select_features=meter_layer,
    search_distance=None,
    selection_type="REMOVE_FROM_SELECTION"
)

count = int(arcpy.management.GetCount(service_layer)[0])
print(f"Selected {count} isolated service lines (no neighbor line, no meter).")
