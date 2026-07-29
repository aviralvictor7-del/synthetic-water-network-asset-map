"""
select_meters_without_services.py

Problem
    In a utility network, some consumer meters may exist without any associated
    service line. These “orphan” meters often indicate data entry errors,
    incomplete edits, or legacy features that need review.

Goal
    Select all consumer meters that are not attached to any service line, using
    a simple geometric intersection rule (meter point intersects service line).

Layers (generic, safe for public repositories)
    Consumer_Meter_FC  - point feature class representing consumer meters
    Service_Line_FC    - line feature class representing service lines

Usage
    1. Add Consumer_Meter_FC and Service_Line_FC to the active map.
    2. Open the Python window in ArcGIS Pro (or run as a script tool).
    3. Run this script. The orphan meters remain selected in the map.

Note
    Replace the layer names below if your map uses different names.
"""

import arcpy

arcpy.env.overwriteOutput = True

# Names of the layers in the active map
METER_LAYER_NAME = "Consumer_Meter_FC"
SERVICE_LAYER_NAME = "Service_Line_FC"

# Get the current map
aprx = arcpy.mp.ArcGISProject("CURRENT")
m = aprx.activeMap

# Locate the meter and service layers
meter_layer = None
service_layer = None

for lyr in m.listLayers():
    if not lyr.isFeatureLayer:
        continue
    if lyr.name == METER_LAYER_NAME:
        meter_layer = lyr
    elif lyr.name == SERVICE_LAYER_NAME:
        service_layer = lyr

if meter_layer is None:
    raise RuntimeError(f"Layer '{METER_LAYER_NAME}' not found in the active map.")

if service_layer is None:
    raise RuntimeError(f"Layer '{SERVICE_LAYER_NAME}' not found in the active map.")

# Clear any existing selection on meters
arcpy.management.SelectLayerByAttribute(meter_layer, "CLEAR_SELECTION")

# Select meters that intersect at least one service line
arcpy.management.SelectLayerByLocation(
    in_layer=meter_layer,
    overlap_type="INTERSECT",
    select_features=service_layer,
    selection_type="NEW_SELECTION"
)

# Switch selection to get meters that do NOT intersect any service line
arcpy.management.SelectLayerByAttribute(
    in_layer_or_view=meter_layer,
    selection_type="SWITCH_SELECTION"
)

# Report result
count = int(arcpy.management.GetCount(meter_layer)[0])
print(f"Selected {count} consumer meters with no connected service line.")
