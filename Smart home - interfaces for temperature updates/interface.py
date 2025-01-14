from tkinter import *
import sqlite3
import threading
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation

M1 = 12
M2 = 31
N1 = 21.1
N2 = 23.7
temperature={
    'room1':1,
    'room2':1
}

temperatures = {
    'room1': [],
    'room2': []
}

def get_temperature():
    conn = sqlite3.connect('E:/Документы/Умный дом/база данных/smart_house.db')
    cur = conn.cursor()
    cur.execute("SELECT room, temperature FROM temperature WHERE room = 'room1' ORDER BY strftime('%Y-%m-%d %H:%M:%S', timestamp) DESC LIMIT 1")
    room1_temperature = cur.fetchone()

    cur.execute("SELECT room, temperature FROM temperature WHERE room = 'room2' ORDER BY strftime('%Y-%m-%d %H:%M:%S', timestamp) DESC LIMIT 1")
    room2_temperature = cur.fetchone()

    conn.close()
    return {'room1': room1_temperature[1] if room1_temperature else None,
            'room2': room2_temperature[1] if room2_temperature else None}


def get_new_temperatures():
    global start_time
    conn = sqlite3.connect('E:/Документы/Умный дом/база данных/smart_house.db')
    cur = conn.cursor()
    new_temperatures = {'room1': [], 'room2': []}
    cur.execute("SELECT room, timestamp, temperature FROM temperature WHERE strftime('%Y-%m-%d %H:%M:%S', timestamp) > ?", (start_time,))
    new_records = cur.fetchall()

    for record in new_records:
        room, timestamp, temp = record
        new_temperatures[room].append((timestamp, temp))

    return new_temperatures

def get_thresholds():
    global N2, N1
    conn = sqlite3.connect('E:/Документы/Умный дом/база данных/smart_house.db')
    cur = conn.cursor()
    cur.execute("SELECT upper_value from thresholds")
    upper_value = cur.fetchone()
    N2 = float(upper_value[0]) if upper_value else N2
    cur.execute("SELECT low_value from thresholds")
    low_value = cur.fetchone()
    N1 = float(low_value[0]) if low_value else N1
    conn.close()

def heating_system():
    for room, temp in temperature.items():
        if room =='room1':
            if temp <= N1:
                heating_room1_label.config(text="Heating system: On")
            elif temp >= N2:
                heating_room1_label.config(text="Heating system: Off")
        else:
            if temp <= N1:
                heating_room2_label.config(text="Heating system: On")
            elif temp >= N2:
                heating_room2_label.config(text="Heating system: Off")


def update_gra(frame):
    plt.clf()
    room1_data = temperatures['room1']
    room2_data = temperatures['room2']

    room1_times, room1_temps = zip(*room1_data)
    room2_times, room2_temps = zip(*room2_data)

    plt.plot(room1_times, room1_temps, label='Bedroom 2')
    plt.plot(room2_times, room2_temps, label='Bedroom 3')

    plt.title('Temperature Change Over Time')
    plt.xlabel('Time')
    plt.ylabel('Temperature')
    plt.legend()
    return plt.gca()

def update_values():
    global N1, N2
    conn = sqlite3.connect('E:/Документы/Умный дом/база данных/smart_house.db')
    cur = conn.cursor()
    if upper_input.get().replace(',', '.').replace('.', '', upper_input.get().count(
            '.') - 1).isdigit() and lower_input.get().replace(',', '.').replace('.', '', lower_input.get().count(
            '.') - 1).isdigit():
        N1 = float(lower_input.get().replace(',', '.'))
        N2 = float(upper_input.get().replace(',', '.'))

        cur.execute("SELECT * FROM thresholds")
        existing_threshold = cur.fetchone()
        if existing_threshold:
            cur.execute("UPDATE thresholds SET upper_value=?, low_value=?", (N2, N1))
        else:
            cur.execute("INSERT INTO thresholds (upper_value, low_value) VALUES (?, ?)", (N2, N1))
        conn.commit()

        lower_label.config(text="Lower threshold: " + str(N1))
        upper_label.config(text="Upper threshold: " + str(N2))

def update_graph(frame):
    ax.clear()
    room1_data = temperatures['room1']
    room2_data = temperatures['room2']

    room1_times, room1_temps = zip(*room1_data)
    room2_times, room2_temps = zip(*room2_data)

    ax.plot(room1_times, room1_temps, label='Bedroom 2')
    ax.plot(room2_times, room2_temps, label='Bedroom 3')

    ax.axhline(y=N1, color='r', linestyle='--')
    ax.axhline(y=N2, color='g', linestyle='--')

    ax.set_title('Temperature Change Over Time')
    ax.set_xlabel('Time')
    ax.set_ylabel('Temperature')
    ax.legend()

    if len(room1_times) > 5 or len(room2_times) > 5:
        ax.set_xticks(ax.get_xticks()[::len(ax.get_xticks())//5])
        ax.tick_params(axis='x', rotation=45)
    ax.tick_params(axis='x', labelsize=8)

    return ax

window = Tk()
window.title('Пиріг Н. Я.')
window.geometry('890x690')

lower_label= Label(window, text='Lower threshold:  '+str(N1), font=("Times New Roman", 14))
upper_label=Label(window, text="Upper threshold: "+str(N2), font=("Times New Roman", 14))
room1_label=Label(window, text="Bedroom 2", font=("Times New Roman", 16))
room2_label=Label(window, text="Bedroom 3", font=("Times New Roman", 16))
temp_room1_label=Label(window, text='Temperature:  ', font=("Times New Roman", 14))
temp_room2_label=Label(window, text='Temperature:  ', font=("Times New Roman", 14))
heating_room1_label=Label(window, text='Heating system:  ', font=("Times New Roman", 14))
heating_room2_label=Label(window, text='Heating system:  ', font=("Times New Roman", 14))

upper_input = Entry(window, width=30, font=("Times New Roman", 12))
lower_input = Entry(window, width=30, font=("Times New Roman", 12))
button_thresholds = Button(window, text="Update thresholds", command=update_values)

lower_label.place(x=50, y=20)
upper_label.place(x=50, y=70)
room1_label.place(x=200, y=120)
room2_label.place(x=600, y=120)
temp_room1_label.place(x=170, y=170)
temp_room2_label.place(x=570, y=170)
heating_room1_label.place(x=170, y=200)
heating_room2_label.place(x=570, y=200)
lower_input.place(x=400, y=20)
upper_input.place(x=400, y=70)
button_thresholds.place(x=650, y=42)

canvas = Canvas(window, width=800, height=600)
canvas.place(x=50, y=250)
fig = plt.figure(figsize=(8, 4))

ax = fig.add_subplot(1, 1, 1)
graph = FigureCanvasTkAgg(fig, master=window)
canvas.create_window(0, 0, anchor='nw', window=graph.get_tk_widget())
ani = FuncAnimation(fig, update_graph, frames=None, blit=False, interval=3700)

def update_temperat():
    global temperature, temperatures
    while True:
        latest_temperatures = get_temperature()
        temperature['room1'] = latest_temperatures['room1']
        temperature['room2'] = latest_temperatures['room2']

        temp_room1_label.config(text='Temperature:  ' + str(temperature['room1']))
        temp_room2_label.config(text='Temperature:  ' + str(temperature['room2']))
        heating_system()
        current_time = time.strftime('%Y-%m-%d %H:%M:%S')
        temperatures['room1'].append((current_time, temperature['room1']))
        temperatures['room2'].append((current_time, temperature['room2']))
        time.sleep(3.7)
def update_temperatures():
    global temperature, temperatures
    while True:
        latest_temperatures = get_temperature()
        temperature['room1'] = latest_temperatures['room1']
        temperature['room2'] = latest_temperatures['room2']

        temp_room1_label.after(0, temp_room1_label.config, {'text': 'Temperature:  ' + str(temperature['room1'])})
        temp_room2_label.after(0, temp_room2_label.config, {'text': 'Temperature:  ' + str(temperature['room2'])})
        heating_system()
        current_time = time.strftime('%Y-%m-%d %H:%M:%S')
        temperatures['room1'].append((current_time, temperature['room1']))
        temperatures['room2'].append((current_time, temperature['room2']))
        time.sleep(3.7)

temperature_thread = threading.Thread(target=update_temperatures)
temperature_thread.start()

def update_thresholds():
    global N1, N2
    while True:
        get_thresholds()
        lower_label.config(text="Lower threshold: " + str(N1))
        upper_label.config(text="Upper threshold: " + str(N2))

        time.sleep(5)

thresholds_thread = threading.Thread(target=update_thresholds)
thresholds_thread.start()

window.mainloop()