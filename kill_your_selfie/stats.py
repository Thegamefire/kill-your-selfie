"""functions to get statistics"""
from datetime import datetime, timedelta

import folium
import folium.plugins

from . import database


def weekly_bar_data() -> list:
    """Data for weekly bar graph"""
    data = []
    occurrences_per_day = database.get_sql_data(
        """SELECT
            DATE_TRUNC('day', time)::date AS day,
            COUNT(time) AS amount
        FROM occurrence
        GROUP BY DATE_TRUNC('day', time)
        ORDER BY DATE_TRUNC('day', time) ASC
        """
    )
    # filter selection on days from last 7 days
    for day in occurrences_per_day:
        if (
            day[0] >= (datetime.now() - timedelta(days=7)).date()
            and day[0] <= datetime.now().date()
        ):
            # add tuple consisting of name of weekday and amount of uses on that day
            data.append((day[0].strftime("%A"), day[1]))

    # add the weekdays without entries to the data
    weekdays = [
        "Sunday",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
    ]
    # get the index of the first weekday of our selection
    first_day = int((datetime.now() - timedelta(days=7)).strftime("%w")) + 1
    # shift the array to start with the first weekday we want
    weekdays = weekdays[first_day:] + weekdays[:first_day]

    i = 0
    while i < len(weekdays): # add empty weekdays that don't appear in the database
        if i>=len(data):
            data.append((weekdays[i], 0))
        elif weekdays[i] != data[i][0]:
            data.insert(i, (weekdays[i], 0))
        i += 1

    return data

def line_data(range) -> list:
    data=[]
    match range:
        case 'month':
            # Get Occurrences per day for the last month
            occurrences_per_day = database.get_sql_data(
                """SELECT
                    EXTRACT('day' FROM DATE_TRUNC('day', o.time)) AS day,
                    COUNT(o.time) AS amount
                FROM occurrence o
                WHERE o.time BETWEEN DATE_TRUNC('day', now()- interval '2 months') AND DATE_TRUNC('day', now()- interval '1 month' + interval '1 day')
                GROUP BY DATE_TRUNC('day', o.time)
                ORDER BY DATE_TRUNC('day', o.time) ASC
                """
            )
            for day in occurrences_per_day:
                data.append((day[0], day[1]))
        case 'year':
            # Get Occurrences per day for the last year
            occurrences_per_day = database.get_sql_data(
                """SELECT
                    TO_CHAR(DATE_TRUNC('day', o.time), 'Month') AS month_of_day,
                    COUNT(o.time) AS amount
                FROM occurrence o
                WHERE o.time BETWEEN DATE_TRUNC('day', now()- interval '2 years') AND DATE_TRUNC('day', now() - interval '1 year' + interval '1 day')
                GROUP BY DATE_TRUNC('day', o.time)
                ORDER BY DATE_TRUNC('day', o.time) ASC
                """
            )
            ## Add (name of month, value) if it's the first day of the month, else just ("", value)
            current_month=""
            for day in occurrences_per_day:
                if current_month != day[0]:
                    current_month = day[0]
                    data.append((day[0], day[1]))
                else:
                    data.append(("", day[1]))
        case 'life':
            occurrences_per_day = database.get_sql_data(
                """SELECT
                    EXTRACT('year' FROM DATE_TRUNC('day', o.time)) AS year,
                    TO_CHAR(DATE_TRUNC('day', o.time), 'Month') AS month_of_day,
                    COUNT(o.time) AS amount
                FROM occurrence o
                GROUP BY DATE_TRUNC('day', o.time)
                ORDER BY DATE_TRUNC('day', o.time) ASC
                """
            )
            current_year=""
            for day in occurrences_per_day:
                if current_year != day[0]:
                    current_year = day[0]
                    data.append((day[0], day[2]))
                else:
                    data.append(("", day[2]))
    return data


def location_map_data() -> str:
    """Data for location map"""
    data = []
    occurrences_per_location = database.get_sql_data(
        """SELECT
            l.label,
            l.latitude,
            l.longitude,
            COUNT(o.time) as amount
        FROM "location" l
        JOIN "occurrence" o ON
            o.location_label = l.label
        GROUP BY l.label, l.latitude, l.longitude
        """
    )
    for location in occurrences_per_location:
        if location[1] is not None and location[2] is not None: # Coordinates are in database
            # Add Latitude, Longitude and Amount
            data.append((location[1], location[2], location[3]))

    location_map = folium.Map([51.05, 3.73], zoom_start=6)
    folium.plugins.HeatMap(data).add_to(location_map)
    return location_map.get_root()._repr_html_()  # TODO: use different function because _repr_html_ is protected



def all_occurences() -> list:
    data = database.get_sql_data(
        """
        SELECT *
        FROM occurrence
        """
    )
    data = list(data)
    data.insert(0, ('time', 'location_label', 'target', 'context'))
    return data