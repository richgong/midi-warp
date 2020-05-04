from pynput import keyboard
import threading
from flask import Flask, render_template, jsonify, request
import requests


### OBS hooks

def script_description():
    return "<b>Gong OBS plugin</b>" + \
           "<hr>" + \
           "Script to receive web commands at http://localhost:28000/" + \
           "<br/><br/>" + \
           "© 2020 Richard Gong"


def script_update(settings):
    print("GONG) Test input:", obs.obs_data_get_string(settings, "test_input"))


def script_properties():
    props = obs.obs_properties_create()
    obs.obs_properties_add_text(props, "test_input", "Test input", obs.OBS_TEXT_DEFAULT)
    return props


def script_load(settings):
    print("GONG) loaded")


def script_unload():
    requests.get(f'http://localhost:{PORT}/kill')


### App

app = Flask(__name__)
IS_DEV = __name__ == '__main__'
PORT = 8080 if IS_DEV else 28000

print(f"GONG) Hi. Running as {__name__}. IS_DEV={IS_DEV}")


@app.route("/")
def home_view():
    return render_template('home.html')


@app.route("/record-start")
def record_start_view():
    obs.obs_frontend_recording_start()
    return render_template('record_start.html')


@app.route("/record-stop")
def record_stop_view():
    obs.obs_frontend_recording_stop()
    return render_template('record_stop.html')


@app.route("/kill")
def kill_view():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return render_template('kill.html')


def on_hotkey():
    print("GONG) Hotkey detected")
    obs.obs_frontend_recording_start()


def run_server(debug=False):
    app.run(host='0.0.0.0', port=PORT, debug=debug)


if IS_DEV:
    # run_server(debug=True)
    threading.Thread(target=run_server, kwargs=dict(debug=False)).start()
else:
    threading.Thread(target=run_server, kwargs=dict(debug=False)).start()
    import obspython as obs
