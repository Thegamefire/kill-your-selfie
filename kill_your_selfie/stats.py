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
        if (datetime.now() - timedelta(days=7)).date() <= day[0] <= datetime.now().date():
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
    while i < len(weekdays):  # add empty weekdays that don't appear in the database
        if i >= len(data):
            data.append((weekdays[i], 0))
        elif weekdays[i] != data[i][0]:
            data.insert(i, (weekdays[i], 0))
        i += 1

    return data


def line_data(time_range) -> list:
    data = []
    match time_range:
        case 'month':
            # Get Occurrences per day for the last month
            occurrences_per_day = database.get_sql_data(
                """
                SELECT
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
            # Get Occurrrences per month for the last year
            occurrences_per_month = database.get_sql_data(
                """
                SELECT TO_CHAR(DATE_TRUNC('month', o.time), 'Year') AS year,
                    to_char(DATE_TRUNC('month', o.time), 'Month') AS month,
                    COUNT(o.time) AS amount
                FROM occurrence o
                WHERE o.time >= DATE_TRUNC('month', now() - interval '1 years')
                GROUP BY DATE_TRUNC('month', o.time)
                ORDER BY DATE_TRUNC('month', o.time) ASC
                """
            )
            last_date = None
            for year, month, amount in occurrences_per_month:
                month_index = int(datetime.strptime(month.strip(), '%B').month) - 1

                if last_date and month_index != (last_date[1] + 1) % 12:
                    if year > last_date[0]:
                        month_index += 12

                    for i in range(last_date[1] + 1, month_index):
                        data.append((datetime.strftime(datetime(1900, i % 12 + 1, 1), '%B'), 0))

                last_date = (year, month_index)
                data.append((month, amount))

    return data


def location_map_data() -> str:
    """Data for location map"""
    data = []
    occurrences_per_location = database.get_sql_data(
        """
        SELECT
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
        if location[1] is not None and location[2] is not None:  # Coordinates are in database
            # Add Latitude, Longitude and Amount
            data.append((location[1], location[2], location[3]))

    location_map = folium.Map([51.05, 3.43], zoom_start=9)
    folium.plugins.HeatMap(data).add_to(location_map)
    # noinspection PyProtectedMember
    return location_map.get_root()._repr_html_()  # TODO: use different function because _repr_html_ is protected
