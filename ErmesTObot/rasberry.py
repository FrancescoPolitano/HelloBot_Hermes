
from main_exception import SafeRequestHandler
import jsonUtil
import logging

class PiPeople(SafeRequestHandler):

    def post(self):
        import key
        import person
        from main import send_message
        body = jsonUtil.json_loads_byteified(self.request.body)
        people_count = body['people']
        logging.debug("body: {}".format(body))
        katja = person.getPersonById(key.KATJA_T_ID)
        send_message(katja, "People count: {} ".format(people_count))