import urllib.parse, urllib.request, urllib.error, json
import keys as keys

def pretty(obj):
    return json.dumps(obj, sort_keys=True, indent=2)

#safeGet method
def safeGet(url):
    try:
        #header = {'User-Agent': 'aerismi17@gmail.com'}
        req = urllib.request.Request(url)#, headers = header)
        completeRequest = urllib.request.urlopen(req)
        return(json.load(completeRequest))
    except urllib.error.HTTPError as e:
        print("No such place found!")
        print("Error code: ", e.code)
    except urllib.error.URLError as e:
        print("We failed to reach a server.")
        print("Reason: ", e.reason)
    return None

def clayerREST(currencies = 'USD', baseurl = 'http://api.currencylayer.com/live',
               access_key = keys.currency_key):
    params = {}
    params['access_key'] = access_key
    if currencies != 'USD':
        params['currencies'] = currencies
    url = baseurl + '?' + urllib.parse.urlencode(params)
    return safeGet(url)

#MAPS API
def gmapsREST(destination,
              baseurl = 'https://www.google.com/maps/embed/v1/place',
              access_key = keys.g_key):
    params = {}
    params['key'] = access_key
    params['q'] = destination
    url = baseurl + '?' + urllib.parse.urlencode(params)
    return url

#WEATHER API
def oweatherREST(lat = 0, lon = 0, baseurl = 'https://api.openweathermap.org/data/2.5/onecall',
                 access_key = keys.weather_key, units = 'imperial'): #exclude = [minutely, hourly,alerts] ):
    params = {}
    params['lat'] = lat
    params['lon'] = lon
    params['units'] = units
    params['appid'] = access_key
    url = baseurl + '?' + urllib.parse.urlencode(params)
    return safeGet(url)

#GEOCODING API
def get_coord(search, baseurl = 'https://maps.googleapis.com/maps/api/geocode/json',
              access_key = keys.coord_key):
    params = {}
    params['address'] = search
    params['key'] = access_key
    url = baseurl + '?' + urllib.parse.urlencode(params)
    return safeGet(url)

from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods = ['GET', 'POST'])
def main_handler():
    if request.method == 'POST':
        search = request.form.get('search')
        #if search is filled out
        if search:
            data = get_coord(search)
            coords = data["results"][0]["geometry"]["location"]
            return render_template('travelsupport.html',
                                   page_title = 'Details for %s'%search,
                                   iframe = gmapsREST(search),
                                   weatherinfo = 'Current Weather',
                                   weather_info = weatherhandler(coords),
                                   temperature = temperaturefind(coords),
                                   currency = 'Currency Evaluation',
                                   detail = '1USD is equivalent to...',
                                   currencyinfo = currencyhandler(data))
        elif request.form.get('hotspot'):
            search = request.form.get('hotspot')
            data = get_coord(search)
            coords = data["results"][0]["geometry"]["location"]
            return render_template('travelsupport.html',
                                   page_title='Details for %s' % search,
                                   iframe=gmapsREST(search),
                                   weatherinfo = 'Current Weather',
                                   weather_info=weatherhandler(coords),
                                   temperature = temperaturefind(coords),
                                   currency = 'Currency Evaluation',
                                   detail = '1USD is equivalent to...',
                                   currencyinfo = currencyhandler(data))
        else:
            return render_template('travelsupport.html',
                                   page_title = 'Enter or choose a location')
    else: return render_template('travelsupport.html', page_title = 'Find details for a city')

def weatherhandler(coords):
    dic = oweatherREST(coords['lat'], coords['lng'])
    iconcode = dic['current']['weather'][0]['icon']
    url = 'http://openweathermap.org/img/wn/' + iconcode + '@2x.png'
    return url

def temperaturefind(coords):
    dic = oweatherREST(coords['lat'], coords['lng'])
    temp = dic['current']['weather'][0]['main']
    return temp

def currencyhandler(data):
    country = ''
    for info in data['results'][0]['address_components']:
        if 'country' in info['types']:
            country = info['long_name']
    print(country)
    if country != 'United States':
        clayernames = clayerREST('USD', 'http://api.currencylayer.com/list')
        names = clayernames['currencies']
        abb = getcurrency(country, names)
        cdic = clayerREST(abb)
        translation = 'USD' + abb
        return cdic['quotes'][translation]
    else:
        return 'No currency translation needed!'

def getcurrency(country, names):
    EU = ['Austria', 'Belgium', 'Cyprus', 'Estonia', 'Finland', 'France',
          'Germany', 'Greece', 'Ireland', 'Italy', 'Latvia', 'Lithuania',
          'Luxembourg', 'Malta', 'Netherlands', 'Portugal', 'Slovakia',
          'Slovenia', 'Spain']
    if country in EU:
        return 'EUR'
    elif country == 'United Kingdom':
        return 'GBP'
    else:
        abbrv = ''
        for abb, curr in names.items():
            print(abb, curr)
            if curr.find(country) != -1:
                abbrv = abb
                return abbrv
            elif curr.find(country[:(len(country))-1]) != -1:
                abbrv = abb
                return abbrv
            elif curr.find(country[:4]) > -1:
                abbrv = abb
                return abbrv
            elif curr.find(country[:3]) > -1:
                abbrv = abb
                return abbrv
        return 'DKK'

if __name__ == '__main__':
    app.run(host='localhost', port=3080, debug=True)