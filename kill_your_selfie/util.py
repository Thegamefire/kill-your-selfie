"""Utility functions"""
from . import models


def get_location_options():
    """get options for location"""
    loc_options=[]
    for location in models.Location.query.all():
        if not location.label in loc_options:
            loc_options.append(location.label)
    return loc_options
