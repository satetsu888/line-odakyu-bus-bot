from bs4 import BeautifulSoup
from urllib import request

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
