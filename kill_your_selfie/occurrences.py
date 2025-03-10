"""Occurrence related functions"""
import datetime
from . import models, database


class InvalidTimeError(Exception):
    """Error when something's wrong with the inputted time"""
    def __init__(self, *args):
        super().__init__(*args)


def get_location_options() -> list:
    """Get history for location field"""
    location_options=[]
    for location in models.Location.query.all():
        if not location.label in location_options:
            location_options.append(location.label)
    return location_options


def get_target_options() -> list:
    """Get history for target field"""
    target_options = []
    for occurrence in models.Occurrence.query.all():
        if not occurrence.target in target_options:
            target_options.append(occurrence.target)
    return target_options


def add_occurrence(time: datetime.datetime, location: str, target: str, context: str) -> None:
    """Add a new occurrence"""
    new_occurrence = models.Occurrence(
        time=time,
        location_label=location,
        target=target,
        context=context,
    )
    if new_occurrence.location_label not in get_location_options():
        new_location = models.Location(
            label=new_occurrence.location_label,
            latitude=None,
            longitude=None
        )
        database.add(new_location)
    database.add(new_occurrence)
    database.commit()


def map_location(location: str, latitude: float, longitude: float) -> None:
    """Map a location to geographical coordinates"""
    location = models.Location.query.filter_by(label=location).first()
    location.latitude = latitude
    location.longitude = longitude
    database.commit()
