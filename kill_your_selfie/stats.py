"""functions to get statistics"""
from datetime import datetime, timedelta

import folium
import folium.plugins

from . import database


def weekly_bar_data() -> list:
    """Data for weekly bar graph"""
    data=[]
    occurences_per_week = database.get_sql_data(
        """
        SELECT extract(dow FROM o.time) AS DAY,
            count(o.time) AS amount
        FROM occurence o
        WHERE extract('week' FROM o.time) = extract('week' FROM now())-1
        GROUP BY o.time
        """
    )
    weekdays = [
        "Sunday",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
    ]

    for i in range(7):
        if len(occurences_per_week) <=i:
            occurences_per_week.insert(i, (i, 0))
        elif occurences_per_week[i][0] != i:
            occurences_per_week.insert(i, (i, 0))

    occurences_per_week=occurences_per_week[1:] + occurences_per_week[:1]

    for day in occurences_per_week:
        print(f">>>{day[0]} {day[1]}")
        data.append((weekdays[int(day[0])], day[1]))

    return data


def location_map_data() -> str:
    """Data for location map"""
    data = []
    occurences_per_location = database.get_sql_data(
        """SELECT
            l.label,
            l.latitude,
            l.longitude,
            COUNT(o.time) as amount
        FROM "location" l
        JOIN "occurence" o ON
            o.location_label = l.label
        GROUP BY l.label, l.latitude, l.longitude
        """
    )
    for location in occurences_per_location:
        if location[1] is not None and location[2] is not None: # Coordinates are in database
            # Add Latitude, Longitude and Amount
            data.append((location[1], location[2], location[3]))

    location_map = folium.Map([51.05, 3.73], zoom_start=6)
    folium.plugins.HeatMap(data).add_to(location_map)
    # pylint: disable=W0212
    return location_map.get_root()._repr_html_()


def statistics_overview_data() -> dict:
    """Returns dictionary with data for statistics overview"""
    data = {}
    ## Get Streaks of sequential dates on which it occured
    streaks = database.get_sql_data(
        """WITH RECURSIVE consecutive_days AS
            (SELECT date_trunc('day', "time") AS date,
                date_trunc('day', "time") AS chain_start_date,
                1 AS chain_length
            FROM occurence o
            UNION SELECT date_trunc('day', o2.time),
                cd.chain_start_date,
                cd.chain_length+1
            FROM consecutive_days cd
            JOIN occurence o2 ON date_trunc('day', o2.time) = cd.date + interval '1 day'),
                streaks AS
            (SELECT chain_start_date,
                max(chain_length) AS streak
            FROM consecutive_days
            GROUP BY chain_start_date)
            SELECT *
            FROM streaks
            ORDER BY streak DESC
            """
    )
    data["Max Streak"]= streaks[0][1]
    ## Get Current Streak
    current_streak = 0
    for streak in streaks:
        if streak[0] >= (datetime.today()-timedelta(days=1)) and streak[1] > current_streak:
            current_streak = streak[1]
    data["Current Streak"] = current_streak
    ## Get Total Occurences
    total_amount = database.get_sql_data(
        """
        SELECT COUNT(time)
        FROM occurence
        """
    )
    data["Total Occurences"] = total_amount[0][0]
    ## Get Average Occurence per day
    total_days = database.get_sql_data(
        """
        WITH minimum_date AS
            (SELECT date_trunc('day', o.time) AS date
            FROM occurence o
            ORDER BY o.time ASC FETCH FIRST 1 ROW ONLY)
        SELECT extract('day' FROM (now()-md.date))
        FROM minimum_date md
        """
    )
    data["Average Per Day"] = total_amount[0][0]/total_days[0][0]
    ## Day With Most Occurences
    max_days_query = database.get_sql_data(
        """
        SELECT date_trunc('day', o.time) AS date,
            COUNT(o.time) AS amount
        FROM occurence o
        GROUP BY date_trunc('day', o.time)
        ORDER BY amount DESC
        FETCH FIRST 1 ROW WITH TIES;
        """
    )
    max_days={}
    for day in max_days_query:
        max_days[day[0]]=day[1]
    data["Most Popular Days"]=max_days
    ## Most Popular Location
    most_popular_locations_query = database.get_sql_data(
        """
        SELECT o.location_label, COUNT(o.time) AS amount
        FROM occurence o
        GROUP BY o.location_label
        ORDER BY amount DESC
        FETCH FIRST 1 ROW WITH TIES;
        """
    )
    most_popular_locations={}
    for location in most_popular_locations_query:
        most_popular_locations[location[0]]=location[1]
    data["Most Popular Locations"]=most_popular_locations
    ## Most Popular Targets
    most_popular_targets_query = database.get_sql_data(
        """
        SELECT o.target, COUNT(o.time) AS amount
        FROM occurence o
        GROUP BY o.target
        ORDER BY amount DESC
        FETCH FIRST 1 ROW WITH TIES;
        """
    )
    most_popular_targets={}
    for target in most_popular_targets_query:
        most_popular_targets[target[0]]=target[1]
    data["Most Popular Targets"]=most_popular_targets
    ## Difference with last week
    week_gains = database.get_sql_data(
        """
        WITH weeks AS
            (SELECT extract('week' FROM o.time) AS WEEK,
                count(o.time) AS amount
            FROM occurence o
            GROUP BY extract('week' FROM o.time))
        SELECT weeks.amount-weeks2.amount AS difference
        FROM weeks
        JOIN weeks AS weeks2 ON weeks.week-1 = weeks2.week
        WHERE weeks.week = extract('week' FROM now())-1
        """
    )
    data["Difference with Last Week"] = week_gains[0][0]

    print(data)
