from flask import Flask, render_template, jsonify, request
import logging
import os
import requests
import threading
from os.path import normpath, realpath, dirname


### OBS hooks

def script_description():
    return "<b>Gong OBS plugin</b>" + \
           "<hr>" + \
           "Script to receive web commands at http://localhost:28000/" + \
           "<br/><br/>" + \
           "© 2020 Richard Gong"


def script_update(settings):
    test_input = obs.obs_data_get_string(settings, 'test_input')
    logging.info(f"GONG) Test input: {test_input}")


def script_properties():
    props = obs.obs_properties_create()
    obs.obs_properties_add_text(props, "test_input", "Test input", obs.OBS_TEXT_DEFAULT)
    return props


def script_load(settings):
    logging.info("GONG) loaded")


def script_unload():
    requests.get(f'http://localhost:{PORT}/kill')


### Setup

PROJECT_PATH = dirname(realpath(__file__))

app = Flask(__name__)
IS_DEV = __name__ == '__main__'
PORT = 8080 if IS_DEV else 28000

log_level = logging.INFO
logging.getLogger('werkzeug').setLevel(logging.WARNING)
logger = logging.getLogger()
logger.setLevel(log_level)
log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(module)s:%(lineno)d %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(log_formatter)
logger.handlers.clear()
logger.addHandler(stream_handler)

### Helpers

def get_absolute_path(relative_path):
    return normpath(os.path.join(PROJECT_PATH, relative_path))

SPEAK_VBS_PATH = get_absolute_path('speak.vbs')

def get_debug_info():
    debug_info = f"GONG) os.name={os.name} __name__={__name__}. IS_DEV={IS_DEV} PORT={PORT} CWD={os.getcwd()} __file__={__file__} PROJECT_PATH={PROJECT_PATH} SPEAK_VBS_PATH={SPEAK_VBS_PATH}"
    logging.info(debug_info)
    return debug_info


get_debug_info()


def say(s):
    if os.name == 'nt':
        cmd = f'cscript {SPEAK_VBS_PATH} "{s}"'
    else:
        cmd = f"say '[[volm 0.50]] {s}'"
    logging.info(f"Saying: {cmd}")
    os.system(cmd)
    return s

### Routes

@app.route("/")
def home_view():
    info = get_debug_info()
    return render_template('home.html', info=info)


@app.route("/record-toggle")
def record_toggle_view():
    recording = not obs.obs_frontend_recording_active()
    if recording:
        obs.obs_frontend_recording_start()
    else:
        obs.obs_frontend_recording_stop()
    return jsonify(msg="Recording started" if recording else "Recording stopped", on=recording)


@app.route("/pause-toggle")
def pause_toggle_view():
    recording = obs.obs_frontend_recording_active()
    msg = None
    if not recording:
        msg = say('Go')
        obs.obs_frontend_recording_start()
        paused = False
    else:
        paused = not obs.obs_frontend_recording_paused()
        if not paused:
            msg = say('Going')
        obs.obs_frontend_recording_pause(paused)
        if paused:
            msg = say('Stop')
    return jsonify(msg=msg, on=not paused)


@app.route("/stop")
def stop_view():
    recording = obs.obs_frontend_recording_active()
    if not recording:
        return jsonify(msg="Already not recording.", on=False)
    if obs.obs_frontend_recording_paused():
        return jsonify(msg="Already paused.", on=False)
    obs.obs_frontend_recording_pause(True)
    return jsonify(msg=say("Stop"), on=False)


@app.route("/start")
def start_view():
    logging.info("Request: start_view...")
    recording = obs.obs_frontend_recording_active()
    if not recording:
        logging.info("...Start recording!")
        msg = say('Start')
        obs.obs_frontend_recording_start()
        return jsonify(msg=msg, on=True)
    if obs.obs_frontend_recording_paused():
        logging.info("...Continue recording!")
        msg = say('Go')
        obs.obs_frontend_recording_pause(False)
        return jsonify(msg=msg, on=True)
    logging.info("...Already recording!")
    return jsonify(msg="Already recording", on=True)


@app.route("/kill")
def kill_view():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return render_template('msg.html', msg='Server killed.')


### This doesn't really work here. use volume_listen.py
# from pynput import keyboard
# def on_hotkey():
#     logging.info("GONG) Hotkey detected")
#     obs.obs_frontend_recording_start()


### Start server

def run_server(debug=False):
    app.run(host='0.0.0.0', port=PORT, debug=debug)


if IS_DEV:
    # run_server(debug=True)
    threading.Thread(target=run_server, kwargs=dict(debug=False)).start()
else:
    threading.Thread(target=run_server, kwargs=dict(debug=False)).start()
    import obspython as obs

