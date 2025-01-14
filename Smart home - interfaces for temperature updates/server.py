from flask import Flask, render_template, request, jsonify
import random
import threading
import time
import os
import configparser
import sqlite3

app = Flask(__name__)
M1 = 12
M2 = 31
N1 = 22.9
N2 = 32.7

heating_states = {
    'room1':False,
    'room2': False
}

light_states = {
    'room1': False,
    'room2': False
}
temperature = {
    'room1': [],
    'room2': []
}
brightness = 0

def load_config():
    config_file_path = "config.conf"
    default_N1 = 22.9
    default_N2 = 32.7

    if not os.path.exists(config_file_path):
        config = configparser.ConfigParser()
        config["Thresholds"] = {
            "N1": str(default_N1),
            "N2": str(default_N2)
        }
        with open(config_file_path, 'w') as configfile:
            config.write(configfile)

    config = configparser.ConfigParser()
    config.read(config_file_path)
    N1 = float(config["Thresholds"]["N1"])
    N2 = float(config["Thresholds"]["N2"])

    return N1, N2

def update_temperature():
    global temperature
    conn = sqlite3.connect("E:/Документы/Умный дом/база данных/smart_house.db")
    cur = conn.cursor()

    while True:
        room1_temp = round(random.uniform(M1, M2), 2)
        room2_temp = round(random.uniform(M1, M2), 2)
        current_time = time.strftime('%Y-%m-%d %H:%M:%S')
        temperature['room1'].append({'time': current_time, 'temperature': room1_temp})
        temperature['room2'].append({'time': current_time, 'temperature': room2_temp})

        for room, temp in temperature.items():
            cur.execute("INSERT INTO temperature (room, timestamp, temperature) VALUES (?, ?, ?)", (room, temp[-1]['time'], temp[-1]['temperature']))
            conn.commit()
            if temp[-1]['temperature'] < N1:
                heating_states[room] = True
            elif temp[-1]['temperature'] > N2:
                heating_states[room] = False
            else:
                pass

        print("Temperature:", temperature)
        print("Heating system states: ", heating_states)
        time.sleep(3.7)

sensor_thread = threading.Thread(target=update_temperature)
sensor_thread.daemon = True
sensor_thread.start()

def update_thresholds_from_database():
    global N1, N2
    conn = sqlite3.connect("E:/Документы/Умный дом/база данных/smart_house.db")
    cur = conn.cursor()

    while True:
        cur.execute("SELECT upper_value, low_value FROM thresholds")
        thresholds = cur.fetchone()

        if thresholds:
            N2, N1 = map(float, thresholds)
            print("Thresholds updated from database: N1 =", N1, ", N2 =", N2)

        time.sleep(5)

thresholds_thread = threading.Thread(target=update_thresholds_from_database)
thresholds_thread.daemon = True
thresholds_thread.start()

@app.route('/')
def index():
    templateData = {
        'light_states': light_states,
        'brightness': brightness,
        'temperature': temperature,
        'heating_states': heating_states,
        'N1': N1,
        'N2': N2
    }
    return render_template('index.html', **templateData)

@app.route('/light/<room>')
def toggle_light(room):
    global light_states
    light_states[room] = not light_states[room]
    print("Light state changed:", light_states)
    templateData = {
        'light_states': light_states,
        'brightness': brightness,
        'temperature': temperature,
        'heating_states': heating_states,
        'N1': N1,
        'N2': N2
    }
    return render_template('index.html', **templateData)

@app.route('/brightness', methods=['GET','POST'])
def change_brightness():
    global brightness
    if request.method == 'POST':
        if request.form.get('brightness'):
            brightness=request.form.get('brightness')
            print("Brightness changed: ", brightness)
    templateData = {
        'light_states': light_states,
        'brightness': brightness,
        'temperature': temperature,
        'heating_states': heating_states,
        'N1': N1,
        'N2': N2
    }
    return render_template('index.html', **templateData)

@app.route('/update_thresholds', methods=['GET', 'POST'])
def change_threshold():
    global N1, N2
    conn = sqlite3.connect("E:/Документы/Умный дом/база данных/smart_house.db")
    cur = conn.cursor()

    if request.method == 'POST':
        new_N1 = request.form.get('N1')
        new_N2 = request.form.get('N2')

        if new_N1 and new_N2:
            N1 = float(new_N1)
            N2 = float(new_N2)
            print("Thresholds changed: N1 =", N1, ", N2 =", N2)
            config = configparser.ConfigParser()
            config["Thresholds"] = {
                "N1": str(N1),
                "N2": str(N2)
            }
            with open("config.conf", 'w') as configfile:
                config.write(configfile)
            cur.execute("SELECT * FROM thresholds")
            existing_threshold = cur.fetchone()

            if existing_threshold:
                cur.execute("UPDATE thresholds SET upper_value=?, low_value=?", (N2, N1))
            else:
                cur.execute("INSERT INTO thresholds (upper_value, low_value) VALUES (?, ?)", (N2, N1))

            conn.commit()

    templateData = {
        'light_states': light_states,
        'brightness': brightness,
        'temperature': temperature,
        'heating_states': heating_states,
        'N1': N1,
        'N2': N2
    }
    return render_template('index.html', **templateData)

@app.route('/temperature')
def get_temperature():
    global temperature
    return jsonify(temperature)

@app.route('/heating')
def get_heating():
    global heating_states
    return jsonify(heating_states)

@app.route('/get_thresholds')
def get_thresholds():
    global N1, N2
    return jsonify({'N1': N1, 'N2': N2})

if __name__ == '__main__':
    N1, N2 = load_config()
    app.run(host='0.0.0.0', port=80)