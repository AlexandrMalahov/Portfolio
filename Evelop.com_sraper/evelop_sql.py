"""Python 3.7. Database of flight schedule."""

import argparse
import datetime
import json
import evelop_scraper
import re
import requests
import os
import sqlite3


def check_cities(dep_city, arr_city):
    """Check that flight type is valid."""

    try:
        dep_city = dep_city.upper()
        arr_city = arr_city.upper()
    except AttributeError:
        return False
    if dep_city not in AVAILABLE_ROUTES:
        print('Incorrect departure city.')
        return False
    elif arr_city not in AVAILABLE_ROUTES:
        print('Incorrect arrival city.')
        return False
    elif arr_city not in AVAILABLE_ROUTES[dep_city]:
        print('No such routes.')
        print('Available routes: ')
        for dep_airport in AVAILABLE_ROUTES:
            print(dep_airport, 'to', AVAILABLE_ROUTES[dep_airport])
        return False
    elif dep_city == arr_city:
        print("Departure city mustn't be same with arrival city.")
        return False

    return True


def manual_input():
    """Get query params from manual input."""

    while True:
        dep_city = input(
            'Please, enter IATA code of departure city({}): '.format(
                ', '.join(AVAILABLE_ROUTES))
        ).upper()

        arr_city = input(
            'Please, enter IATA code of arrival city({}): '.format(
                ', '.join(AVAILABLE_ROUTES))
        ).upper()

        if check_cities(dep_city, arr_city):
            break

    while True:
        dep_date = input('Enter departure date: ')
        if evelop_scraper.check_dates(dep_date):
            break

    return {'dep_city': dep_city, 'arr_city': arr_city, 'dep_date': dep_date}


def input_query_params():
    """Parse and check arguments of command line."""

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dep_city', help='Input departure city.')
    parser.add_argument('-a', '--arr_city', help='Input arrival city.')
    parser.add_argument('-d_d', '--dep_date', help='Input departure date.')
    args = parser.parse_args()
    try:
        dep_city = args.dep_city.upper()
        arr_city = args.arr_city.upper()
    except AttributeError:
        return None
    if not check_cities(dep_city, arr_city):
        return None
    if not evelop_scraper.check_dates(args.dep_date):
        return None

    return dep_city, arr_city


def find_available_dates():
    """Get available dates from page."""

    # must check regex
    response = requests.get('https://en.evelop.com/').content
    dates = re.findall(r'routesWebSale = ({.+});', str(response))[0]
    dates = re.split(';', dates)[1]
    dates = re.findall(r'\[(.+)]', dates)[0]
    dates = re.sub(r'}(,){', ' ', dates).split()
    list_of_dicts = []
    for flight in dates:
        flight = re.search(r'[^{](.+)[^}]', flight).group()
        list_of_dicts.append(json.loads('{' + flight + '}'))

    return list_of_dicts


def find_info_on_query(search_params):
    """Get flight information on request from the page"""

    #  Converting the entered date into a format suitable
    #  for comparison with data on the site.
    dep_date = re.sub(r'[./]', '-', search_params['dep_date'])
    dep_day_list = ['-', '-', '-', '-', '-', '-', '-']
    for flight in DICT_WITH_DATES:
        if search_params['dep_city'] == flight['origin'] and \
                search_params['arr_city'] == flight['destination'] and \
                dep_date in flight['dates']:
            for date in flight['dates']:
                date = datetime.datetime.strptime(date, '%d-%m-%Y')
                day = datetime.datetime.weekday(date)
                dep_day_list[day] = '+'
            flight_dict = {
                'dep_city': flight['origin'],
                'arr_city': flight['destination'],
                'schedule': ''.join(dep_day_list)
            }

            return flight_dict


def create_table():
    """Create table in database."""

    conn = sqlite3.connect('fly_database.db')
    cursor = conn.cursor()
    cursor.execute(
        'CREATE TABLE Flight_schedule(ID INTEGER PRIMARY '
        'KEY AUTOINCREMENT, Dep_airport, Arr_airport, flight_schedule)'
    )


def insert_table(schedule_data):
    """Insert data into table."""

    conn = sqlite3.connect('fly_database.db')
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO Flight_schedule(Dep_airport, Arr_airport, '
        'flight_schedule) VALUES (?, ?, ?)', [*schedule_data.values()]
    )
    conn.commit()
    print('Data has been added to the table.', '\n')


def select_data_table(search_params):
    """Select data from table."""

    conn = sqlite3.connect('fly_database.db')
    cursor = conn.cursor()
    sql = "SELECT * FROM Flight_schedule WHERE Dep_airport=? AND Arr_airport=?"

    try:
        cursor.execute(
            sql, [search_params['dep_city'], search_params['arr_city']])
    except sqlite3.OperationalError:
        create_table()
        return None

    try:
        result = cursor.fetchall()[0]
        result = {
            'dep_city': result[1], 'arr_city': result[2], 'schedule': result[3]
        }
    except IndexError:
        return None

    return result


def get_schedule_data(search_params):
    """Get schedule dict."""

    if not search_params:
        search_params = manual_input()

    if not os.path.isfile('fly_database.db'):
        create_table()

    data_from_table = select_data_table(search_params)
    data_from_page = find_info_on_query(search_params)

    if data_from_table and data_from_page:
        print('Data from the table:', '\n')
        schedule_data = data_from_table
    else:
        print('Data not found in the table.', '\n')
        schedule_data = data_from_page
        insert_table(schedule_data) if schedule_data else None

    return schedule_data


def print_result(schedule_data):
    """Print result."""

    if not schedule_data:
        print('This date is not available.')
        print('--------------------------------------------')
    else:
        print('Departure city:', schedule_data['dep_city'])
        print('Arrival city:', schedule_data['arr_city'])
        print('Flight schedule:', schedule_data['schedule'])
        print('--------------------------------------------')


if __name__ == '__main__':
    AVAILABLE_ROUTES = evelop_scraper.get_available_routes()
    DICT_WITH_DATES = find_available_dates()
    QUERY_PARAMS = input_query_params()
    while True:
        SCHEDULE_DATA = get_schedule_data(QUERY_PARAMS)
        print_result(SCHEDULE_DATA)
        QUERY_PARAMS = None
        if input(
                'For exit enter "exit". For exit press "Enter".'
        ).upper() == 'EXIT':
            break
