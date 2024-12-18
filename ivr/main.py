#!ivr/venv/bin/python3

import asyncio
import logging
import os
import re

from yate.protocol import MessageRequest
from yate.ivr import YateIVR

LOG_FILE = "/tmp/call.log"

SOUNDS_PATH = "./ivr/audio/"

async def play_error(ivr: YateIVR, error_code: int):
    error_code = str(error_code).zfill(4)
    error_file = os.path.join(SOUNDS_PATH, "errors", error_code + ".sln")
    await ivr.play_soundfile(error_file, complete=True)

async def main(ivr: YateIVR):
    caller_id = ivr.call_params.get("caller", "")
    caller_id = re.sub("[^\\d]", "", caller_id)
    caller_id = re.sub("^\\+", "00", caller_id)

    # Welcome to the rust hotline, for german press 1, for english press 2
    await ivr.play_soundfile(os.path.join(SOUNDS_PATH, "messages/intro.sln"))

    lang = "de"
    
    plz = await ivr.read_dtmf_symbols(1)

    print("input", plz)
    # while len(plz) == 0:
    #     plz = await ivr.read_dtmf_symbols(1)

    if plz == "1":
        lang = "de"
    elif plz == "2":
        lang = "en"

    # For general questions 1, compiler errors 2, rewrite in rust 3, unsafe rust 4
    await ivr.play_soundfile(os.path.join(SOUNDS_PATH, "messages/main_menu_{}.sln".format(lang)))


    plz = await ivr.read_dtmf_symbols(1)

    if plz == "1":
        return
    elif plz == "2":
        await ivr.play_soundfile(os.path.join(SOUNDS_PATH, "messages/enter_code_{}.sln".format(lang)))
        plz = await ivr.read_dtmf_symbols(4)
        await play_error(ivr, int(plz))
        await asyncio.sleep(1)
        await play_error(ivr, int(plz))
        await ivr.play_soundfile(os.path.join(SOUNDS_PATH, "messages/error_code_agent_{}.sln".format(lang)), complete=True)



    # await ivr.play_soundfile(os.path.join(SOUNDS_PATH, "ansage_1_intro_plz.slin"))
    # plz = await ivr.read_dtmf_symbols(5)
    # if len(plz) != 5:
    #     plz = "00000"
    # await ivr.play_soundfile(os.path.join(SOUNDS_PATH, "ansage_2_intro_hilfe.slin"), complete=True)

    # for _ in range(3):
    #     await ivr.play_soundfile(os.path.join(SOUNDS_PATH, "ansage_3_auswahl_der_hilfe.slin"))
    #     help_id = await ivr.read_dtmf_symbols(1, 34)
    #     if help_id in ["1", "2", "3", "4", "5"]:
    #         break
    # if help_id == "":
    #     help_id = "5"

    # if help_id == "5":
    #     call_msg = MessageRequest("chan.masquerade", {
    #         "message": "call.execute",
    #         "id": ivr.call_id,
    #         "callto": FORWARD_PHONE_ADDRESS,
    #         "line": LINE,
    #         "oconnection_id": "external_udp",
    #         "osip_From": SIP_FROM_HEADER,
    #     })
    #     result = await ivr.send_message_async(call_msg)
    #     if not result.processed:
    #         await ivr.play_soundfile(os.path.join(SOUNDS_PATH, "ansage_sibernetz_fail.slin"), complete=True)
    # else:
    #     query = {
    #         "token": API_TOKEN,
    #         "phone": caller_id,
    #         "zip": plz,
    #         "request": help_id,
    #     }
    #     success = True
    #     error_message = ""
    #     try:
    #         api_result = requests.get(URL, query)
    #     except requests.exceptions.RequestException as e:
    #         success = False
    #         error_message = str(e)

    #     if success and api_result.status_code != 200:
    #         success = False
    #         error_message = "HTTP error: " + str(api_result.status_code)

    #     if not success:
    #         fallback_filename = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-") + uuid.uuid4().hex + "response.sbj"
    #         fallback_file = os.path.join(FALLBACK_FILES_DIR, fallback_filename)
    #         with open(fallback_file, "w") as f:
    #             f.write(error_message + "\n")
    #             f.write(repr(query))
    #     else:
    #         await ivr.play_soundfile(os.path.join(SOUNDS_PATH, "ansage_4_vielen_dank.slin"), complete=True)
    #         await asyncio.sleep(0.5)


logging.basicConfig(filename=LOG_FILE, filemode="a+")
app = YateIVR()
app.run(main)