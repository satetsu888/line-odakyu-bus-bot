import re
from bs4 import BeautifulSoup
from urllib import request, parse

def build_bus_text(bus_data, limit):
    head = '{time}\n{pole}\n'.format(**bus_data)
    body = ''
    for data in bus_data['bus'][:limit]:
        body+= '{table_time} {destination}行きは、{description}\n'.format(**data)

    return head + body


def fetch_bus_data():
    response = request.urlopen('http://www.odakyubus-navi.com/blsys/loca?VID=ldt&EID=nt&DSMK=83&DK=2j_6u_1b&DK=2j_6u_6q')
    body = response.read()
    soup = BeautifulSoup(body)
    result_div = soup.find('div', {'class': 'resultBox'})
    if result_div is None:
        return None
    # print(result_div)
    time = result_div.find('p', {'class': 'time'})
    # print(time.string)
    pole = result_div.find('h3', {'class': 'pole'})
    # print(pole.string)
    table = result_div.find('table', { 'class': 'resultTbl'})
    # print(table.string)
    bus = []
    for tr in table.find_all('tr'):
        if len(tr.find_all('td')) != 0:
            (table_time, predict_time, destination, bus_type, description) = [th.string for th in tr.find_all('td')]
            # print(table_time)
            # print(predict_time)
            # print(destination)
            # print(bus_type)
            # print(description)
            bus.append({
                'table_time': table_time,
                'predict_time': predict_time,
                'destination': destination,
                'bus_type': bus_type,
                'description': description,
                })
    return {
        'time': time.string,
        'pole': pole.string,
        'bus': bus,
        }

def search_pole(query):
    poles = []

    url = 'http://www.odakyubus-navi.com/blsys/loca?VID=ssp&EID=nt&ARK=9&DSN={}'.format(parse.quote_plus(query, encoding='sjis'))
    # print(url)
    response = request.urlopen(url)
    body = response.read()
    # print(body)
    soup = BeautifulSoup(body)

    # find result script
    result_script_pattern = re.compile('document.SubmitForm.DSMK.value = "(?P<DSMK>\d+)"')
    result_script = soup.find(string=result_script_pattern)
    # print(result_script)
    if result_script is not None:
        match = re.search(result_script_pattern, result_script.string)
        code = match.groupdict()['DSMK']
        poles.append({
            'name': query, # not accurate :(
            'code': code,
            })
    else:
        # find select box
        result_select = soup.find('select', {'class': 'fs110'})
        # print(result_select.string)
        options = result_select.find_all('option')
        for option in options:
            # print(option.string)
            poles.append({
                'name': option.string,
                'code': option['value'],
                })

    return {
        'query': query,
        'poles': poles,
    }
