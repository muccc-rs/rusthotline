#!ivr/venv/bin/python3

import asyncio
import logging
import os
import re
import json

from yate.ivr import YateIVR

import datetime
import pickledb
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename='./call.log', encoding='utf-8', level=logging.DEBUG)

LOG_FILE = "/tmp/call.log"

SOUNDS_PATH = "./ivr/audio/"

def log_call(ivr: YateIVR, event: str):
    with open("calllog.csv", "a") as call_log:
        time_str = datetime.datetime.now().strftime("%d-%m-%Y_%H:%M:%S")
        call_log.write("{},{}, {}\n".format(ivr.call_params.get("caller"), time_str, event))

async def handle_error_code(ivr: YateIVR, lang: str):
    await ivr.play_soundfile(os.path.join(SOUNDS_PATH, "messages/enter_code_{}.sln".format(lang)))
    plz = await ivr.read_dtmf_symbols(4)
    error_code = str(plz).zfill(4)
    callername = "e" + error_code + "/" + ivr.call_params.get("called") + "/" + ivr.call_params.get("callername")
    error_file = os.path.join(SOUNDS_PATH, "errors", error_code + ".sln")
    log_call(ivr, "Error code: " + error_code)
    if not os.path.isfile(error_file):
        await ivr.play_soundfile(os.path.join(SOUNDS_PATH, "messages/error_code_does_not_exist_{}.sln".format(lang)), complete=True)
    else:
        await ivr.play_soundfile(error_file, complete=True)
        await asyncio.sleep(1)
        await ivr.play_soundfile(error_file, complete=True)
        await ivr.play_soundfile(os.path.join(SOUNDS_PATH, "messages/error_code_agent_{}.sln".format(lang)), complete=True)  
    await call_operators(ivr, callername)

async def main(ivr: YateIVR):
    caller_id = ivr.call_params.get("caller", "")
    caller_id = re.sub("[^\\d]", "", caller_id)
    caller_id = re.sub("^\\+", "00", caller_id)

    if (ivr.call_params.get("called") == "8787"):
        await hotline(ivr)
    elif (ivr.call_params.get("called") == "7372"):
         await admin_setup(ivr)

async def admin_setup(ivr: YateIVR):
    await ivr.play_soundfile(os.path.join(SOUNDS_PATH, "messages/admin_please_enter_password.sln"))
    password_input = await ivr.read_dtmf_symbols(5)
    if password_input != "23646":
        return
    
    # Play enter sound
    await ivr.play_soundfile(os.path.join(SOUNDS_PATH, "messages/admin_hello.sln"))
    # Set state
    state_input = await ivr.read_dtmf_symbols(1)

    db = pickledb.load('./rustations.db', False)
    data = db.get('admins')
    if data == None or not data:
        db.set('admins', json.dumps([]))
        data = db.get('admins')
    admins = json.loads(db.get('admins'))

    sip_uri = ivr.call_params.get("sip_from")
    if state_input == "1":
        # Check if caller id is in operator list else add it
        if admins == None or len(admins) == 0:
            admins = [sip_uri]
        elif sip_uri not in admins:
            admins.append(sip_uri)
        db.set('admins', json.dumps(admins))
        db.dump()
        await ivr.play_soundfile(os.path.join(SOUNDS_PATH, "messages/admin_sign_in.sln"), complete=True)
    elif state_input == "2":
        # Remove caller id from operator list
        if admins != None and sip_uri in admins:
            admins.remove(sip_uri)
            db.set('admins', json.dumps(admins))
        db.dump()
        await ivr.play_soundfile(os.path.join(SOUNDS_PATH, "messages/admin_sign_out.sln"), complete=True)
    elif state_input == "3":
        await ivr.ring_extension("sip:8631@voip.eventphone.de")
        # await ivr.fork_call(["sip:8631@voip.eventphone.de"], "admin")

async def call_operators(ivr: YateIVR, callername: str):
    log_call(ivr, "Call operators")
    db = pickledb.load('./rustations.db', False)
    data = db.get('admins')
    if data == None or not data:
        return
    admins = json.loads(data)
    if len(admins) == 0:
        await ivr.play_soundfile(os.path.join(SOUNDS_PATH, "messages/not_staffed_one_hour.sln"), complete=True)
        return
    await ivr.play_soundfile(os.path.join(SOUNDS_PATH, "messages/waiting_announcement_1_en.sln"), complete=True)
    await ivr.fork_call(admins, callername)

async def hotline(ivr:YateIVR):
    # Welcome to the rust hotline, for german press 1, for english press 2
    await ivr.play_soundfile(os.path.join(SOUNDS_PATH, "messages/intro.sln"))
    log_call(ivr, "Call enter")

    lang = "de"
    
    # ToDo: use wait_channel_event !
    plz = await ivr.read_dtmf_symbols(1, 12)

    if plz == "1":
        lang = "de"
    elif plz == "2":
        lang = "en"
    elif plz == "":
        callername = "unknown"
        caller_id = ivr.call_params.get("caller")
        caller_name = ivr.call_params.get("callername")
        if caller_id and caller_name:
            callername = caller_id + "/" + caller_name
        await call_operators(ivr, callername)
    # For general questions 1, compiler errors 2, rewrite in rust 3, unsafe rust 4
    await ivr.play_soundfile(os.path.join(SOUNDS_PATH, "messages/main_menu_{}.sln".format(lang)))

    # ToDo: use wait_channel_event !
    plz = await ivr.read_dtmf_symbols(1, 23)

    if plz == "" or plz == "1" or plz == "3" or plz == "4":
        caller_id = ivr.call_params.get("caller")
        caller_name = ivr.call_params.get("callername")
        callername = lang
        if caller_id and caller_name:
            callername = lang + "/"+ caller_id + "/" + caller_name
        await call_operators(ivr, callername)
    elif plz == "2":
        await handle_error_code(ivr, lang)

app = YateIVR()
app.run(main)