# -*- coding: utf-8 -*-

import jsonUtil
import key


from google.appengine.ext import ndb
from geo import geomodel
import date_time_util as dtu
import utility
from utility import convertToUtfIfNeeded


class Mensa(geomodel.GeoModel, ndb.Model):
    #id: #name = ndb.StringProperty()
    # location = ndb.GeoPtProperty() # inherited from geomodel.GeoModel
    latitude = ndb.ComputedProperty(lambda self: self.location.lat if self.location else None)
    longitude = ndb.ComputedProperty(lambda self: self.location.lon if self.location else None)
    address = ndb.StringProperty()
    capacity = ndb.IntegerProperty()
    taken_seats = ndb.IntegerProperty(default=0)
    opening_time_lunch = ndb.StringProperty()
    opening_time_dinner = ndb.StringProperty()
    menu_image_id = ndb.StringProperty()
    menu_image_last_update_datetime = ndb.DateTimeProperty(default=dtu.getDatetime('01012010'))
    menu_image_last_update_userinfo = ndb.StringProperty()
    queue_image_id = ndb.StringProperty()
    queue_image_last_update_datetime = ndb.DateTimeProperty(default=dtu.getDatetime('01012010'))
    queue_image_last_update_userinfo = ndb.StringProperty()

    def getPropertyUtfMarkdown(self, property, escapeMarkdown=True):
        if property == None:
            return None
        result = convertToUtfIfNeeded(property)
        if escapeMarkdown:
            result = utility.escapeMarkdown(result)
        return result

    def getName(self):
        return self.getPropertyUtfMarkdown(self.key.id())

    def getAddress(self):
        return self.getPropertyUtfMarkdown(self.address)

    def getOpeningTimeLunch(self):
        return self.getPropertyUtfMarkdown(self.opening_time_lunch)

    def getOpeningTimeDinner(self):
        return self.getPropertyUtfMarkdown(self.opening_time_dinner)

    def getInfo(self):
        name = self.getName()
        address = self.getAddress()
        capacity = self.capacity
        orario_lunch = self.getOpeningTimeLunch()
        orario_dinner = self.getOpeningTimeDinner()
        return "*Nome*: {}\n" \
               "*Indirizzo*: {}\n" \
               "*Capacità*: {}\n" \
               "*Orario Pranzo:* {}\n" \
               "*Orario Cena:* {}".format(name, address, capacity, orario_lunch, orario_dinner)

def getMensaByName(name):
    return Mensa.get_by_id(name)

def getInfoMensa(name):
    mensa = getMensaByName(name)
    if mensa:
        return mensa.getInfo()
    return None

def getMensaNames():
    mense = Mensa.query().fetch()
    names = [m.getName() for m in mense]
    return names

def getMenuImageId(name):
    m = getMensaByName(name)
    return m.menu_image_id

def getMenuImageLastUpdateDateTime(name):
    m = getMensaByName(name)
    return dtu.formatDateTime(m.menu_image_last_update_datetime)

def setMenuImageId(name, id, userinfo):
    m = getMensaByName(name)
    m.menu_image_id = id
    m.menu_image_last_update_datetime = dtu.nowCET()
    m.menu_image_last_update_userinfo = userinfo
    m.put()
    #import random
    #return random.choice([True, False])

def getMenuInfo(name):
    return 'This is the menu...'

def addMensa(name, lat, lon, address, capacity, opening_time_lunch, opening_time_dinner, put=True):
    p = Mensa(
        id=name,
        location = ndb.GeoPt(lat, lon),
        address=address,
        capacity=capacity,
        opening_time_lunch=opening_time_lunch,
        opening_time_dinner=opening_time_dinner,
    )
    p.update_location()
    if put:
        p.put()
    return p

def deleteMense():
    more, cursor = True, None
    while more:
        to_delete = []
        keys, cursor, more = Mensa.query().fetch_page(1000, start_cursor=cursor, keys_only=True)
        for k in keys:
            to_delete.append(k)
        if to_delete:
            create_futures = ndb.delete_multi_async(to_delete)
            ndb.Future.wait_all(create_futures)

BASE_MAP_IMG_URL = "http://maps.googleapis.com/maps/api/staticmap?" + \
                   "&size=400x400" + "&maptype=roadmap" + \
                   "&key=" + key.GOOGLE_API_KEY


MAX_THRESHOLD_RATIO = 2

def getMenseNearPosition(lat, lon, radius):
    import geoUtils
    import params
    nearby_fermate_dict = {}
    centralPoint = (lat, lon)
    min_distance = None
    mense = Mensa.query().fetch()
    for m in mense:
        refPoint = (m.latitude, m.longitude)
        d = geoUtils.distance(refPoint, centralPoint)
        if d < radius:
            if min_distance is None or d < min_distance:
                min_distance = d
            name = m.getName()
            nearby_fermate_dict[name] = {
                'loc': refPoint,
                'dist': d
            }
    min_distance = max(min_distance, 1) # if it's less than 1 km use 1 km as a min distance
    nearby_fermate_dict = {k:v for k,v in nearby_fermate_dict.items() if v['dist'] <= MAX_THRESHOLD_RATIO*min_distance}
    max_results = params.MAX_FERMATE_NEAR_LOCATION
    nearby_mense_sorted_dict = sorted(nearby_fermate_dict.items(), key=lambda k: k[1]['dist'])[:max_results]
    return nearby_mense_sorted_dict


def getMenseNearPositionImgUrl(nearby_mense_sorted_dict, lat, lon):
    return BASE_MAP_IMG_URL + \
              "&markers=color:red|{},{}".format(lat, lon) + \
              ''.join(["&markers=color:blue|label:{}|{},{}".format(num, v['loc'][0], v['loc'][1])
                       for num, (f, v) in enumerate(nearby_mense_sorted_dict, 1)])

def getMenseNearPositionText(nearby_mense_sorted_dict):
    from utility import format_distance
    fermate_number = len(nearby_mense_sorted_dict)
    text = 'Ho trovato *1 mensa* ' if fermate_number == 1 else 'Ho trovato *{} mense* '.format(
        fermate_number)
    text += "in prossimità dalla posizione inserita:\n"
    text += '\n'.join(
        '{}. {}: {}'.format(num, f, format_distance(v['dist']))
        for num, (f, v) in enumerate(nearby_mense_sorted_dict, 1))
    return text

'''
mensa_info = jsonUtil.json_load_byteified(open("data/cafeterias.json"))
mensa_names = [x['info']['name'] for x in mensa_info]
mensa_name_loc = {x['info']['name']: x['info']['coordinates'] for x in mensa_info}

def populateMense():
    mense = []
    for name in mensa_names:
        match = [x for x in mensa_info if x['info']['name'] == name][0]
        lat_lon = match['info']['coordinates']
        lat = lat_lon['latitude']
        lon = lat_lon['longitude']
        address = match['info']['address']
        capacity = match['capacity']
        opening_time_lunch = match['info']['launch']["start"] + ' - ' + match['info']['launch']["end"]
        opening_time_dinner = match['info']['dinner']["start"] + ' - ' + match['info']['dinner']["end"]
        m = addMensa(name, lat, lon, address, capacity, opening_time_lunch, opening_time_dinner, put=False)
        mense.append(m)
    create_futures = ndb.put_multi_async(mense)
    ndb.Future.wait_all(create_futures)
'''

'''
import requests
base_url = 'https://00b501df.ngrok.io/RestfulService_war_exploded/restresources'
mensa_info_url = base_url + '/cafeterias'
menu_info_url = base_url + '/cafeteria/{}/menu'
r = requests.get(mensa_info_url)
mensa_info = jsonUtil.json_loads_byteified(r.text)
'''


'''
def getInfoMensa(name):
    match = [x for x in mensa_info if x['info']['name']==name]
    if match:
        entry = match[0]
        address = entry['info']['address']
        capacity = entry['capacity']
        takenSeats = entry['takenSeats']
        orario_lunch = entry['info']['launch']["start"] + ' - ' + entry['info']['launch']["end"]
        orario_dinner = entry['info']['dinner']["start"] + ' - ' + entry['info']['dinner']["end"]
        #freeSeats = capacity-takenSeats
        return "*Nome*: {}\n" \
               "*Indirizzo*: {}\n" \
               "*Capacità*: {}\n" \
               "*Orario Pranzo:* {}\n" \
               "*Orario Cena:* {}".format(name, address, capacity, orario_lunch, orario_dinner)
    return None
'''

'''
def getMenu(name):
    assert name in mensa_names
    index = mensa_names.index(name)
    #url = menu_info_url.format(index)
    #r = requests.get(url)
    #menu = jsonUtil.json_loads_byteified(r.text)
    menu = jsonUtil.json_load_byteified(open("data/menu_{}.json".format(index)))
    return menu
'''

'''
def getMenuInfo(name):
    assert name in mensa_names
    menu = getMenu(name)
    primi = menu['first_plate']
    primi_piatti = [str_plate(x) for x in primi]
    secondi = menu['second_plate']
    secondi_piatti = [str_plate(x) for x in secondi]
    return '\n'.join(["1️⃣ *PRIMI*:\n---------", '\n'.join(primi_piatti), "\n\n2️⃣ *SECONDI*:\n---------", '\n'.join(secondi_piatti)])
'''

'''
def str_plate(dict):
    return '\n'.join([
        '*{}*'.format(dict['name']),
        "  Gluten-Free: {}".format(checkbox(dict['glutenFree'])),
        "  Piatto Unico: {}".format(checkbox(dict['piatto_unico'])),
    ])
'''

'''
def checkbox(boolean):
    return '✅' if boolean else '❌'
'''

