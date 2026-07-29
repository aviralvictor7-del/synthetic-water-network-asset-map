"""
layer_check_template.py

Utility
    Helper functions for validating the presence of required layers in the
    active ArcGIS Pro map. Intended for reuse across QA and automation scripts.

Usage
    from layer_check_template import get_layer_or_raise

    service_layer = get_layer_or_raise("Service_Line_FC")
    meter_layer = get_layer_or_raise("Consumer_Meter_FC")
"""

import arcpy


def get_layer_or_raise(layer_name: str) -> arcpy.mp.Layer:
    """
    Return the feature layer with the given name from the active map.

    Raises
    ------
    RuntimeError
        If the layer is not found or is not a feature layer.
    """
    aprx = arcpy.mp.ArcGISProject("CURRENT")
    m = aprx.activeMap

    for lyr in m.listLayers():
        if lyr.isFeatureLayer and lyr.name == layer_name:
            return lyr

    raise RuntimeError(
        f"Required layer '{layer_name}' was not found in the active map. "
        "Check that the layer is added and its name matches this script."
    )
