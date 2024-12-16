"""Occurence related functions"""
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
    for occurence in models.Occurence.query.all():
        if not occurence.target in target_options:
            target_options.append(occurence.target)
    return target_options


def add_occurence(time: datetime.datetime, location: str, target: str, context: str) -> None:
    """Add a new occurence"""
    new_occurence = models.Occurence(
        time=time,
        location_label=location,
        target=target,
        context=context,
    )
    if new_occurence.location_label not in get_location_options():
        new_location = models.Location(
            label=new_occurence.location_label,
            latitude=None,
            longitude=None
        )
        database.add(new_location)
    database.add(new_occurence)
    database.commit()
