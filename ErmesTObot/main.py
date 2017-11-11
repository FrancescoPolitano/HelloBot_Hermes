# -*- coding: utf-8 -*-

import main_fb
import main_telegram

import logging
from time import sleep
import utility
import geoUtils
import key
import person
from person import Person
import date_time_util as dtu
import webapp2


########################
WORK_IN_PROGRESS = False
########################


# ================================
# ================================
# ================================

STATES = {
    0: 'Initial state',
    9: 'Feedback'
}

RESTART_STATE = 0
SETTINGS_STATE = 3
HELP_STATE = 9


# ================================
# BUTTONS
# ================================

BOTTONE_INDIETRO = "🔙 INDIETRO"
BOTTONE_INIZIO = "🏠 TORNA ALL'INIZIO"
BOTTENE_CERCA_MENSA = "🔍🍽 CERCA MENSA"
BOTTONE_FEEDBACK = "📮 FEEDBACK"


BOTTONE_LOCATION = {
    'text': "INVIA POSIZIONE",
    'request_location': True,
}

# ================================
# TEMPLATE API CALLS
# ================================

def send_message(p, msg, kb=None, markdown=True, inline_keyboard=False, one_time_keyboard=False,
         sleepDelay=False, hide_keyboard=False, force_reply=False, disable_web_page_preview=False):
    if p.isTelegramUser():
        return main_telegram.send_message(p, msg, kb, markdown, inline_keyboard, one_time_keyboard,
                           sleepDelay, hide_keyboard, force_reply, disable_web_page_preview)
    else:
        if kb is None:
            kb = p.getLastKeyboard()
        if kb:
            kb_flat = utility.flatten(kb)[:11] # no more than 11
            return main_fb.sendMessageWithQuickReplies(p, msg, kb_flat)
        else:
            return main_fb.sendMessage(p, msg)
        #main_fb.sendMessageWithButtons(p, msg, kb_flat)

def send_photo_png_data(p, file_data, filename):
    if p.isTelegramUser():
        main_telegram.sendPhotoFromPngImage(p.chat_id, file_data, filename)
    else:
        main_fb.sendPhotoData(p, file_data, filename)
        # send message to show kb
        kb = p.getLastKeyboard()
        if kb:
            msg = 'Opzioni disponibili:'
            kb_flat = utility.flatten(kb)[:11] # no more than 11
            main_fb.sendMessageWithQuickReplies(p, msg, kb_flat)

def send_photo_url(p, url, kb=None):
    if p.isTelegramUser():
        main_telegram.sendPhotoViaUrlOrId(p.chat_id, url, kb)
    else:
        #main_fb.sendPhotoUrl(p.chat_id, url)
        import requests
        file_data = requests.get(url).content
        main_fb.sendPhotoData(p, file_data, 'file.png')
        # send message to show kb
        kb = p.getLastKeyboard()
        if kb:
            msg = 'Opzioni disponibili:'
            kb_flat = utility.flatten(kb)[:11]  # no more than 11
            main_fb.sendMessageWithQuickReplies(p, msg, kb_flat)

def sendDocument(p, file_id):
    if p.isTelegramUser():
        main_telegram.sendDocument(p.chat_id, file_id)
    else:
        pass

def sendExcelDocument(p, sheet_tables, filename='file'):
    if p.isTelegramUser():
        main_telegram.sendExcelDocument(p.chat_id, sheet_tables, filename)
    else:
        pass

def sendWaitingAction(p, action_type='typing', sleep_time=None):
    if p.isTelegramUser():
        main_telegram.sendWaitingAction(p.chat_id, action_type, sleep_time)
    else:
        pass


# ================================
# GENERAL FUNCTIONS
# ================================

# ---------
# BROADCAST
# ---------

BROADCAST_COUNT_REPORT = utility.unindent(
    """
    Messaggio inviato a {} persone
    Ricevuto da: {}
    Non rivevuto da : {} (hanno disattivato il bot)
    """
)

#NOTIFICATION_WARNING_MSG = '🔔 Per modificare le notifiche vai su {} → {}.'.format(
#    BOTTONE_IMPOSTAZIONI, BOTTONE_NOTIFICHE)

def broadcast(sender, msg, qry = None, restart_user=False,
              blackList_sender=False, sendNotification=True,
              notificationWarning = False):

    from google.appengine.ext.db import datastore_errors
    from google.appengine.api.urlfetch_errors import InternalTransientError

    if qry is None:
        qry = Person.query()
    qry = qry.order(Person._key) #_MultiQuery with cursors requires __key__ order

    more = True
    cursor = None
    total, enabledCount = 0, 0

    while more:
        users, cursor, more = qry.fetch_page(100, start_cursor=cursor)
        for p in users:
            try:
                #if p.getId() not in key.TESTERS:
                #    continue
                if not p.enabled:
                    continue
                if blackList_sender and sender and p.getId() == sender.getId():
                    continue
                total += 1
                p_msg = msg
                #+ '\n\n' + NOTIFICATION_WARNING_MSG \
                #    if notificationWarning \
                #    else msg
                if send_message(p, p_msg, sleepDelay=True): #p.enabled
                    enabledCount += 1
                    if restart_user:
                        restart(p)
            except datastore_errors.Timeout:
                msg = '❗ datastore_errors. Timeout in broadcast :('
                tell_admin(msg)
                #deferredSafeHandleException(broadcast, sender, msg, qry, restart_user, curs, enabledCount, total, blackList_ids, sendNotification)
                return
            except InternalTransientError:
                msg = 'Internal Transient Error, waiting for 1 min.'
                tell_admin(msg)
                sleep(60)
                continue

    disabled = total - enabledCount
    msg_debug = BROADCAST_COUNT_REPORT.format(total, enabledCount, disabled)
    logging.debug(msg_debug)
    if sendNotification:
        send_message(sender, msg_debug)
    #return total, enabledCount, disabled

def broadcastUserIdList(sender, msg, userIdList, blackList_sender, markdown):
    for id in userIdList:
        p = person.getPersonById(id)
        if not p.enabled:
            continue
        if blackList_sender and sender and p.getId() == sender.getId():
            continue
        send_message(p, msg, markdown=markdown, sleepDelay=True)



# ---------
# Restart All
# ---------

def restartAll(qry = None):
    from google.appengine.ext.db import datastore_errors
    if qry is None:
        qry = Person.query()
    qry = qry.order(Person._key)  # _MultiQuery with cursors requires __key__ order

    more = True
    cursor = None
    total = 0

    while more:
        users, cursor, more = qry.fetch_page(100, start_cursor=cursor)
        try:
            for p in users:
                if p.enabled:
                    if p.state == RESTART_STATE:
                        continue
                    #logging.debug('Restarting {}'.format(p.chat_id))
                    total += 1
                    restart(p)
                sleep(0.1)
        except datastore_errors.Timeout:
            msg = '❗ datastore_errors. Timeout in broadcast :('
            tell_admin(msg)

    logging.debug('Restarted {} users.'.format(total))

# ================================
# UTILIITY TELL FUNCTIONS
# ================================

def tellMaster(msg, markdown=False, one_time_keyboard=False):
    for id in key.ADMIN_IDS:
        p = person.getPersonById(id)
        main_telegram.send_message(
            p, msg, markdown=markdown,
            one_time_keyboard=one_time_keyboard,
            sleepDelay=True
        )

def tellInputNonValidoUsareBottoni(p, kb=None):
    msg = '⛔️ Input non riconosciuto, usa i bottoni qui sotto 🎛'
    send_message(p, msg, kb)

def tellInputNonValido(p, kb=None):
    msg = '⛔️ Input non riconosciuto.'
    send_message(p, msg, kb)

def tell_admin(msg):
    logging.debug(msg)
    for id in key.ADMIN_IDS:
        p = person.getPersonById(id)
        send_message(p, msg, markdown=False)

def send_message_to_person(id, msg, markdown=False):
    p = Person.get_by_id(id)
    send_message(p, msg, markdown=markdown)
    if p and p.enabled:
        return True
    return False

# ================================
# RESTART
# ================================
def restart(p, msg=None):
    if msg:
        send_message(p, msg)
    p.resetTmpVariable()
    redirectToState(p, RESTART_STATE)


# ================================
# SWITCH TO STATE
# ================================
def redirectToState(p, new_state, **kwargs):
    if p.state != new_state:
        logging.debug("In redirectToState. current_state:{0}, new_state: {1}".format(str(p.state), str(new_state)))
        # p.firstCallCategoryPath()
        p.setState(new_state)
    repeatState(p, **kwargs)


# ================================
# REPEAT STATE
# ================================
def repeatState(p, put=False, **kwargs):
    methodName = "goToState" + str(p.state)
    method = possibles.get(methodName)
    if not method:
        send_message(p, "Si è verificato un problema (" + methodName +
             "). Segnalamelo mandando una messaggio a @kercos" + '\n' +
             "Ora verrai reindirizzato/a nella schermata iniziale.")
        restart(p)
    else:
        if put:
            p.put()
        method(p, **kwargs)

# ================================
# UNIVERSAL COMMANDS
# ================================

def dealWithUniversalCommands(p, input):
    from main_exception import deferredSafeHandleException
    if p.isAdmin():
        if input.startswith('/testText '):
            text = input.split(' ', 1)[1]
            if text:
                msg = '🔔 *Messaggio da ErmesTObot* 🔔\n\n' + text
                logging.debug("Test broadcast " + msg)
                send_message(p, msg)
                return True
        if input.startswith('/broadcast '):
            text = input.split(' ', 1)[1]
            if text:
                msg = '🔔 *Messaggio da ErmesTObot* 🔔\n\n' + text
                logging.debug("Starting to broadcast " + msg)
                deferredSafeHandleException(broadcast, p, msg)
                return True
        elif input.startswith('/restartBroadcast '):
            text = input.split(' ', 1)[1]
            if text:
                msg = '🔔 *Messaggio da ErmesTObot* 🔔\n\n' + text
                logging.debug("Starting to broadcast and restart" + msg)
                deferredSafeHandleException(broadcast, p, msg, restart_user=False)
                return True
        elif input.startswith('/textUser '):
            p_id, text = input.split(' ', 2)[1]
            if text:
                p = Person.get_by_id(p_id)
                if send_message(p, text, kb=p.getLastKeyboard()):
                    msg_admin = 'Message sent successfully to {}'.format(p.getFirstNameLastNameUserName())
                    tell_admin(msg_admin)
                else:
                    msg_admin = 'Problems sending message to {}'.format(p.getFirstNameLastNameUserName())
                    tell_admin(msg_admin)
                return True
        elif input.startswith('/restartUser '):
            p_id = input.split(' ')[1]
            p = Person.get_by_id(p_id)
            restart(p)
            msg_admin = 'User restarted: {}'.format(p.getFirstNameLastNameUserName())
            tell_admin(msg_admin)
            return True
        elif input == '/testlist':
            p_id = key.FEDE_FB_ID
            p = Person.get_by_id(p_id)
            main_fb.sendMessageWithList(p, 'Prova lista template', ['one','twp','three','four'])
            return True
        elif input == '/restartAll':
            deferredSafeHandleException(restartAll)
            return True
        elif input == '/restartAllNotInInitialState':
            deferredSafeHandleException(restartAll)
            return True
        elif input == '/testSpeech':
            redirectToState(p, 8)
            return True
    return False

## +++++ BEGIN OF STATES +++++ ###

# ================================
# GO TO STATE 0: Initial State
# ================================

def goToState0(p, **kwargs):
    input = kwargs['input'] if 'input' in kwargs.keys() else None
    giveInstruction = input is None
    if giveInstruction:
        msg = '🏠 *Inizio*\n\n' \
              'Premi su:\n' \
              '{} per cercare la mensa più vicina.\n' \
              '{} per contattarci o inviarci suggerimenti'.\
            format(BOTTENE_CERCA_MENSA, BOTTONE_FEEDBACK)
        kb = [
            [BOTTENE_CERCA_MENSA],
            [BOTTONE_FEEDBACK]
        ]
        #if p.isAdmin():
        #    kb[-1].append(BOTTONE_ADMIN)
        p.setLastKeyboard(kb)
        send_message(p, msg, kb)
    else:
        kb = p.getLastKeyboard()
        if input in utility.flatten(kb):
            if input == BOTTENE_CERCA_MENSA:
                msg = '⚠️ Work in progress'
                send_message(p, msg, kb)
            elif input == BOTTONE_FEEDBACK:
                redirectToState(p, 9)
            #else:
            #    assert input == BOTTONE_ADMIN
            #    redirectToState(p, 7)
        else:
            tellInputNonValidoUsareBottoni(p, kb)


# ================================
# GO TO STATE 9: Contattaci
# ================================

def goToState9(p, **kwargs):
    input = kwargs['input'] if 'input' in kwargs.keys() else None
    giveInstruction = input is None
    if giveInstruction:
        kb = [[BOTTONE_INDIETRO]]
        msg = '📩 Non esitate a *contattarci*:\n\n' \
              '∙ 📝 Scrivi qua sotto qualsiasi feedback o consiglio\n' \
              '∙ 🗣 Entrare in chat con noi cliccando su @kercos\n'
        p.setLastKeyboard(kb)
        send_message(p, msg, kb)
    else:
        if input == BOTTONE_INDIETRO:
            restart(p)
        else:
            msg_admin = '📩📩📩\nMessaggio di feedback da {}:\n{}'.format(p.getFirstNameLastNameUserName(), input)
            tell_admin(msg_admin)
            msg = 'Grazie per il tuo messaggio, ti contatteremo il prima possibile.'
            send_message(p, msg)
            restart(p)


## +++++ END OF STATES +++++ ###

def dealWithUserInteraction(chat_id, name, last_name, username, application, text,
                            location, contact, photo, document, voice):

    p = person.getPersonByChatIdAndApplication(chat_id, application)
    name_safe = ' {}'.format(name) if name else ''

    if p is None:
        p = person.addPerson(chat_id, name, last_name, username, application)
        msg = " 😀 Ciao{},\nbenvenuto/a In ErmesTObot!\n".format(name_safe)
        send_message(p, msg)
        restart(p)
        tellMaster("New {} user: {}".format(application, p.getFirstNameLastNameUserName()))
    else:
        # known user
        modified, was_disabled = p.updateUserInfo(name, last_name, username)
        if WORK_IN_PROGRESS and p.getId() not in key.TESTER_IDS:
            send_message(p, "🏗 Il sistema è in aggiornamento, ti preghiamo di riprovare più tardi.")
        elif was_disabled or text in ['/start', 'start', 'START', 'INIZIO']:
            msg = " 😀 Ciao{}!\nBentornato/a in ErmesTObot!".format(name_safe)
            send_message(p, msg)
            restart(p)
        elif text == '/state':
            msg = "You are in state {}: {}".format(p.state, STATES.get(p.state, '(unknown)'))
            send_message(p, msg)
        elif text in ['/settings', 'IMPOSTAZIONI']:
            redirectToState(p, SETTINGS_STATE)
        elif text in ['/help', 'HELP', 'AIUTO']:
            redirectToState(p, HELP_STATE)
        elif text in ['/stop', 'STOP']:
            p.setEnabled(False, put=True)
            msg = "🚫 Hai *disabilitato* ErmesTObot.\n" \
                  "In qualsiasi momento puoi riattivarmi scrivendomi qualcosa."
            send_message(p, msg)
        else:
            if not dealWithUniversalCommands(p, input=text):
                logging.debug("Sending {} to state {} with input {}".format(p.getFirstName(), p.state, text))
                repeatState(p, input=text, location=location, contact=contact, photo=photo, document=document,
                            voice=voice)

import rasberry

app = webapp2.WSGIApplication([
    ('/telegram_me', main_telegram.MeHandler),
    ('/telegram_set_webhook', main_telegram.SetWebhookHandler),
    ('/telegram_get_webhook_info', main_telegram.GetWebhookInfo),
    ('/telegram_delete_webhook', main_telegram.DeleteWebhook),
    #(key.FACEBOOK_WEBHOOK_PATH, main_fb.WebhookHandler),
    (key.TELEGRAM_WEBHOOK_PATH, main_telegram.WebhookHandler),
    ('/pi_people', rasberry.PiPeople),
], debug=True)

possibles = globals().copy()
possibles.update(locals())
