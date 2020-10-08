"""Python 3.7. Parsing of the web site https://www.evelop.com/."""

import argparse
import datetime
import json
import re
import requests
import unicodedata

from lxml import html


def check_flight_type(flight_type):
    """Check that flight type is valid."""

    try:
        flight_type = flight_type.upper()
    except AttributeError:
        return False
    if flight_type in {'ONE_WAY', 'ROUND_TRIP'}:
        return True
    print(
        'Incorrect flight type. Please, '
        'enter a correct one(ONE_WAY/ROUND_TRIP).'
    )

    return False


def check_cities(dep_city, arr_city):
    """Check that IATA codes are valid."""

    try:
        dep_city = dep_city.upper()
        arr_city = arr_city.upper()
    except AttributeError:
        return False
    if dep_city not in AVAILABLE_ROUTES:
        print('Incorrect departure city.')
        return False
    elif arr_city not in AVAILABLE_ROUTES[dep_city]:
        print('No such routes.')
        print('Available routes: ')
        for dep_airport in AVAILABLE_ROUTES:
            print(dep_airport, 'to', *AVAILABLE_ROUTES[dep_airport])
        return False
    elif dep_city == arr_city:
        print("Departure city mustn't be same with arrival city.")
        return False

    return True


def check_dates(*dates):
    """Check if dates are valid."""

    today = datetime.datetime.now().date()
    for date in dates:
        try:
            date = re.findall(
                r'\b(\d{2})[.-/](\d{2})[.-/](\d{4})\b', date)[0]
        except IndexError:
            print('Incorrect date.')
            return False
        except TypeError:
            print('You did not enter a date.')
            return False
        try:
            date = datetime.date(*map(int, reversed(date)))
        except ValueError:
            print('The date value entered is invalid.')
            return False
        if not date:
            print('Incorrect date')
            return False
        if date <= today:
            print(
                'Departure date must be greater than today '
                'and return date greater than departure date.'
            )
            return False
        today = date

    return True


def check_passengers(adults, children, infants):
    """Check number of passengers."""

    try:
        adults = int(adults)
        children = int(children)
        infants = int(infants)
    except ValueError:
        print('Number of passengers must be integer number.')
        return False
    except TypeError:
        print('You did not enter number of adults, children or infants.')
        return False

    if adults <= 0 or adults > 9:
        print(
            'Number of adults must be more '
            'or equal 1 and less or equal 9.'
        )
        return False

    if children < 0 or children + adults > 9:
        print(
            'Number of children must be more or equal 0 '
            'and less or equal number of adults, and '
            'sum of number of adults and children must '
            'not be more than 9.'
        )
        return False

    if infants < 0 or infants > adults or infants > 5:
        print(
            'Number of infants must be more or equal '
            '0 and less or equal number of adults.'
        )
        return False

    return True


def get_query_params_from_command_line():
    """Parse and check arguments of command line."""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-f',
        '--flight_type', help='input flight type("ONE_WAY" or "ROUND_TRIP")'
    )
    parser.add_argument(
        '-d', '--dep_city', help='input departure city(three-digit IATA code)')
    parser.add_argument(
        '-a', '--arr_city', help='input arrival city(three-digit IATA code)')
    parser.add_argument('-d_d', '--dep_date', help='input departure date')
    parser.add_argument('-r', '--ret_date', help='input return date')
    parser.add_argument('-n_a', '--num_adults', help='input number of adults')
    parser.add_argument('-n_c', '--num_child', help='input number of children')
    parser.add_argument(
        '-n_i', '--num_infants', help='input number of infants')

    args = parser.parse_args()

    if not check_flight_type(args.flight_type):
        return None

    if not check_cities(args.dep_city, args.arr_city):
        return None

    if args.flight_type.upper() == 'ONE_WAY':
        if not check_dates(args.dep_date):
            return None
        args.ret_date = args.dep_date
    else:
        if not check_dates(args.dep_date, args.ret_date):
            return None

    if not check_passengers(args.num_adults, args.num_child, args.num_infants):
        return None

    return {
        'flight_type': args.flight_type.upper(),
        'dep_city': args.dep_city.upper(),
        'arr_city': args.arr_city.upper(),
        'dep_date': args.dep_date,
        'ret_date': args.ret_date,
        'adults': args.num_adults,
        'children': args.num_child,
        'infants': args.num_infants
    }


def manual_input():
    """Get query params from manual input."""

    while True:
        flight_type = input(
            'Please, enter type of flight ("ONE_WAY" or "ROUND_TRIP"): '
        ).upper()

        if check_flight_type(flight_type):
            break

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
        dep_date = input('Please, enter departure date(dd/mm/yyyy): ').upper()

        if flight_type == 'ROUND_TRIP':
            ret_date = input('Please, enter return date(dd/mm/yyyy): ')
            if check_dates(dep_date, ret_date):
                break
        else:
            if check_dates(dep_date):
                ret_date = dep_date
                break

    while True:
        adults = input(
            'Please, enter a number of adults'
            '(number must be more than 0 and less or equal 9): '
        )
        children = input(
            'Please, enter a number of children (number must be more or '
            'equal than 0 and less or equal number of adults): '
        )
        infants = input(
            'Please, enter a number of infants (number must be more or '
            'equal than 0 and less or equal number of adults): '
        )

        if check_passengers(adults, children, infants):
            break

    return {
        'flight_type': flight_type,
        'dep_city': dep_city,
        'arr_city': arr_city,
        'dep_date': dep_date,
        'ret_date': ret_date,
        'adults': adults,
        'children': children,
        'infants': infants
    }


def get_available_routes():
    """Generate list of available routes."""

    response = requests.get('https://en.evelop.com/', verify=False).content

    routes_json = re.findall(r'routesWebSale = ({.+});', str(response))[0]
    routes = re.split(';', routes_json)[0]
    routes_json = json.loads(routes)

    return routes_json


def generate_request_params(search_params):
    """Generate params for get web-page with search results."""

    return {
        'buscadorVuelosEsb.tipoTransicion': 'S',
        'buscadorVuelosEsb.routeType': search_params['flight_type'],
        'buscadorVuelosEsb.origen': search_params['dep_city'],
        'buscadorVuelosEsb.destino': search_params['arr_city'],
        'buscadorVuelosEsb.fsalida': search_params['dep_date'],
        'buscadorVuelosEsb.fregreso': search_params['ret_date'],
        'buscadorVuelosEsb.numadultos': search_params['adults'],
        'buscadorVuelosEsb.numninos': search_params['children'],
        'buscadorVuelosEsb.numbebes': search_params['infants']
    }


def get_data_page(search_params, session):
    """Get html page from web-site."""

    params = generate_request_params(search_params)
    tree = html.fromstring(
        session.post(
            'https://en.evelop.com/b2c/pages/flight/'
            'disponibilidadSubmit.html?',
            params,
            verify=False
        ).content
    )

    return tree


def parse_results(data_page, search_params, session):
    """Get and generate quotes."""

    try:
        data = data_page.xpath(
            '/html/body/div[@id="content"]/div/div'
            '/form[@id="formularioValoracion"]/div/div[@class="flexcols"]'
            '/section/div[@id="tabs2"]/div/div'
        )[0]
    except IndexError:
        return None
    quotes = []
    if search_params['flight_type'] == 'ONE_WAY':

        results = data.xpath(
            'ol/li/div[@class="vuelo-wrap vuelo-wrap3"]/div[@class="flexcols"]'
        )

        for result in results:
            quote = {}

            flight_data = parse_data_div(
                result.xpath(
                    'div[@class="flexcol-main datos"]/div')[0],
                search_params['flight_type']
            )

            flight_data['flight_time'] = generate_flight_time(
                flight_data['dep_time'], flight_data['arr_time'])
            flight_data['date'] = search_params['dep_date']
            quote['Outbound'] = flight_data

            #  Variable "radio_date" using for get price.
            radio_data = result.xpath(
                'div[@class="flexcol-right acciones3 clearfix"]/div/a'
            )[0].get('onclick')
            radio_data = re.findall(r'idSeleccionado=(\d+)', radio_data)[0]

            flight_data['radio'] = radio_data
            quote['price'] = get_price(
                session, search_params, flight_data['radio'])
            quotes.append(quote)
    else:
        # The result consists of two nested lists.
        # The first one contains "outbound" (flight_ob) flights,
        # the second one contains "return" (flight_ib) flights.
        results = data.xpath(
            'div[@class="wrap-sel-custom combinado"]'
            '/div[@class="grid-cols clearfix"]/div'
        )
        data_xpath = 'div[@class="datos"]/div[not(contains(@class, ' \
                     '"detalles-vuelo-wrap roundedtop clearfix"))]'
        # Generate flights combinations.
        ob_lst = [
            parse_data_div(flight) for
            flight in results[0].xpath(data_xpath)
        ]
        ib_lst = [
            parse_data_div(flight) for
            flight in results[1].xpath(data_xpath)
        ]

        for flight_ob in ob_lst:
            for flight_ib in ib_lst:

                flight_ob['flight_time'] = generate_flight_time(
                    flight_ob['dep_time'], flight_ob['arr_time'])
                flight_ib['flight_time'] = generate_flight_time(
                    flight_ib['dep_time'], flight_ib['arr_time'])

                flight_ob['date'] = search_params['dep_date']
                flight_ib['date'] = search_params['ret_date']

                quotes.append(
                    {
                        'Outbound': flight_ob,
                        'Return': flight_ib,
                        'price': get_price(
                            session, search_params,
                            flight_ob['radio'], flight_ib['radio']
                        )
                    }
                )

    return quotes


def parse_data_div(data_div, flight_type='ROUND_TRIP'):
    """Parse div elements with data from web page."""

    route = data_div.xpath(
        'div[@class="aerolinea"]/text()|div[@class="aerop"]/span/text()'
    )[0]
    dep_city, arr_city = route.replace(
        ' ', '').replace('\n', '').replace('\t', '').split('-')
    dep_time = data_div.xpath(
        'div[@class="salida"]/span[@class="hora"]/text()')[0].strip()
    arr_time = data_div.xpath(
        'div[@class="llegada"]/span[@class="hora"]/text()')[0].strip()
    cabin_class = data_div.xpath(
        'div[@class="clase"]/span[@class="left clearfix clase"]'
        '/span[@class="tipo-clase"]/text()|'
        'div[@class="left clearfix clase "]/span[@class="tipo-clase"]/text()'
    )[0]

    data_from_div = {
        'dep_city': dep_city,
        'arr_city': arr_city,
        'dep_time': dep_time,
        'arr_time': arr_time,
        'cabin_class': cabin_class
    }
    if flight_type == 'ROUND_TRIP':
        #  Find the necessary data for query parameters.
        radio_data = data_div.xpath(
            'div[@class="radio"]/input')[0].get('onclick')
        radio_data = radio_data.split('(')[1].replace("'", '').replace(
            '\n', '').replace(r'\s+', '').split(',')
        direction = radio_data[1]
        radio_data = '#'.join(
            radio_data[i].strip() for i in (0, 3, 4))
        radio_data = {'flightId': radio_data, 'direction': direction}
        data_from_div['radio'] = radio_data

    return data_from_div


def generate_flight_time(dep_time, arr_time):
    """Calculate flight time."""

    dep_time = dep_time.split(':')
    arr_time = arr_time.split(':')
    dep_time = datetime.timedelta(
        hours=float(dep_time[0]), minutes=float(dep_time[1]))
    arr_time = datetime.timedelta(
        hours=float(arr_time[0]), minutes=float(arr_time[1]))

    return re.findall(r'\w{1,2}:\w{2}', str(arr_time - dep_time))[0]


def get_price(session, search_params, *params_for_requests):
    """Get price for round trip way."""

    param_for_get_price = {
        'fechaSalida': search_params['dep_date'],
        'fechaRegreso': search_params['ret_date'],
        'idOrigen': search_params['dep_city'],
        'idDestino': search_params['arr_city'],
        'numeroAdultos': search_params['adults'],
        'numeroNinios': search_params['children'],
        'numeroBebes': search_params['infants'],
        'routeType': search_params['flight_type'],
    }

    id_session = re.findall('IDSESION="(\w+)', str(session.cookies))[0]
    param_for_price = {'sesion': id_session}

    if search_params['flight_type'] == 'ONE_WAY':
        param_for_get_price['idSeleccionado'] = params_for_requests[0]
        session.get(
            'https://en.evelop.com/b2c/pages/flight/valoracion_esb.html?',
            params=param_for_get_price
        )
        get_price_request = session.get(
            'https://secure.evelop.com/b2c/pages/flight'
            '/pasajerosReload_esb.html?',
            params=param_for_price
        )

        tree = html.fromstring(get_price_request.content)
        price = tree.xpath(
            '/html/body/aside/div'
            '/div[@class="box box-color2 rounded ticket-vuelos-precio"]'
            '/div[@class="subbox rounded escalas"]/div'
            '/div[@class="line separa total"]'
            '/div[@class="unit lastUnit t-right precio"]/text()')
        price = unicodedata.normalize(
            'NFKC', ''.join(price)
        ).encode('latin-1').decode('utf-8').replace('\n', '').replace('  ', '')
    else:
        session.get(
            'https://en.evelop.com/b2c/pages/flight/valoracion_esb.html?',
            params=param_for_get_price
        )
        for param in params_for_requests:
            session.get(
                'https://en.evelop.com/b2c/pages/flight/'
                'availabilitySelectFlight.html?',
                params=param,
                verify=False
            )

        session.get(
            'https://en.evelop.com/b2c/pages/flight/valoracion_esb.html?',
            params=param_for_get_price)

        get_price_request = session.get(
            'https://secure.evelop.com/b2c/pages/flight/pasajerosReload_esb.html?',
            params=param_for_price).text

        tree = html.fromstring(get_price_request)

        price = ''.join(tree.xpath(
            '/html/body/aside/div'
            '/div[@class="box box-color2 rounded ticket-vuelos-precio"]'
            '/div[@class="subbox rounded escalas"]/div'
            '/div[@class="line separa total"]'
            '/div[@class="unit lastUnit t-right precio"]/text()'
        )).strip()
        price = ' '.join(re.findall(r'([0-9.,]+)\n\s+.(.)', price)[0])

    return price


def scrape(search_params):
    """Get search params if necessary and return quotes."""

    if not search_params:
        search_params = manual_input()
    session = requests.session()
    data_page = get_data_page(search_params, session)
    quotes = parse_results(data_page, search_params, session)

    return quotes


def print_results(quotes):
    """Print results."""

    if not quotes:
        print(
            'There is not availability enough for the '
            'selected flights. Please select another date.'
        )
    else:
        for quote in quotes:
            for key, value in quote.items():
                if key != 'price':
                    print(key, '\n')
                    print(
                        'Route: {0} - {1}'.format(
                            value['dep_city'], value['arr_city'])
                    )
                    print('Date:', value['date'])
                    print('Departure time:', value['dep_time'])
                    print('Arrival time:', value['arr_time'])
                    print('Flight time:', value['flight_time'])
                    print('Class:', value['cabin_class'], '\n')
            print('Price:', quote['price'])
            print('-------------------------------------------')


if __name__ == '__main__':
    AVAILABLE_ROUTES = get_available_routes()
    QUERY_PARAMS = get_query_params_from_command_line()
    while True:
        QUOTES = scrape(QUERY_PARAMS)
        print_results(QUOTES)
        QUERY_PARAMS = None
        if input(
            'Enter "EXIT" to close program. For continue press "Enter". '
        ).upper() == 'EXIT':
            break
