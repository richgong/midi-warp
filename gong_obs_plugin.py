from pynput import keyboard
import threading
import os
from flask import Flask, render_template, jsonify, request
import requests
import logging


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


### App

app = Flask(__name__)
IS_DEV = __name__ == '__main__'
PORT = 8080 if IS_DEV else 28000

log_level = logging.DEBUG if IS_DEV else logging.WARNING
logging.getLogger('werkzeug').setLevel(log_level)
logger = logging.getLogger()
logger.setLevel(log_level)
log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(module)s:%(lineno)d %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(log_formatter)
logger.addHandler(stream_handler)

logging.info(f"GONG) Hi. Running as {__name__}. IS_DEV={IS_DEV}")


def say(s):
    os.system(f"say '[[volm 0.50]] {s}'")
    return s


@app.route("/")
def home_view():
    return render_template('home.html')


@app.route("/record-toggle")
def record_toggle_view():
    recording = not obs.obs_frontend_recording_active()
    if recording:
        obs.obs_frontend_recording_start()
    else:
        obs.obs_frontend_recording_stop()
    return jsonify(msg="Recoding started" if recording else "Recording stopped", on=recording)


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


@app.route("/pause")
def pause_view():
    recording = obs.obs_frontend_recording_active()
    if not recording:
        return jsonify(msg="Already not recording.", on=False)
    if obs.obs_frontend_recording_paused():
        return jsonify(msg="Already paused.", on=False)
    obs.obs_frontend_recording_pause(True)
    return jsonify(msg=say("Stop"), on=False)


@app.route("/continue")
def continue_view():
    recording = obs.obs_frontend_recording_active()
    if not recording:
        msg = say('Start')
        obs.obs_frontend_recording_start()
        return jsonify(msg=msg, on=True)
    if obs.obs_frontend_recording_paused():
        msg = say('Go')
        obs.obs_frontend_recording_pause(False)
        return jsonify(msg=msg, on=True)
    return jsonify(msg="Already recording", on=True)


@app.route("/kill")
def kill_view():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return render_template('msg.html', msg='Server killed.')


def on_hotkey():
    logging.info("GONG) Hotkey detected")
    obs.obs_frontend_recording_start()


def run_server(debug=False):
    app.run(host='0.0.0.0', port=PORT, debug=debug)


if IS_DEV:
    # run_server(debug=True)
    threading.Thread(target=run_server, kwargs=dict(debug=False)).start()
else:
    threading.Thread(target=run_server, kwargs=dict(debug=False)).start()
    import obspython as obs
