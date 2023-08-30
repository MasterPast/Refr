import threading
import tkinter as tk
import serial
import DS18B20_Module

def read_sensor(x):
    global open_port_flag
    while True:
        if DS18B20_Module.GetThermo(x):
            if DS18B20_Module.GetCRC(x, 8) == x.CRC:
                text_status.set("Порт відкритий")
                temp = (x.H_Termo << 8) | x.L_Termo
                string_thermo.set("{:.1f} °C".format(temp / 16))
            else:
                text_status.set("Помилка CRC")
        else:
            error_code = DS18B20_Module.GetLastErr()
            if error_code != DS18B20_Module.DS_Err_OK:
                text_status.set(DS18B20_Module.getLastErr_String(error_code))
                string_thermo.set("")
        threading.Event().wait(0.2)

def select_port():
    global open_port_flag
    port = combo_ports.get()

    DS18B20_Module.close_port()
    open_port_flag = False

    if port:
        try:
            ser = serial.Serial(port, 9600)
            ser.close()
            open_port_flag = True
            text_status.set("Порт відкритий")
        except serial.SerialException:
            text_status.set("Помилка: порт недоступний")

def enum_ports():
    ports = []
    for i in range(11):
        try:
            with serial.Serial("COM" + str(i), 9600):
                ports.append("COM" + str(i))
        except serial.SerialException:
            pass
    return ports

def save_settings():
    with open("Setting.ini", "w") as file:
        file.write(combo_ports.get())

def load_settings():
    try:
        with open("Setting.ini", "r") as file:
            port = file.readline().strip()
            if port:
                combo_ports.set(port)
    except FileNotFoundError:
        pass

open_port_flag = False

root = tk.Tk()
root.title("DS18B20 Reader")

frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

text_status = tk.StringVar()
label_status = tk.Label(frame, textvariable=text_status)
label_status.pack()

string_thermo = tk.StringVar()
label_thermo = tk.Label(frame, textvariable=string_thermo)
label_thermo.pack()

combo_ports = tk.StringVar()
combo_ports.set("Виберіть порт")
combo = tk.OptionMenu(frame, combo_ports, *enum_ports())
combo.pack()

button_select = tk.Button(frame, text="Вибрати порт", command=select_port)
button_select.pack()

load_settings()
select_port()

thread = threading.Thread(target=read_sensor, args=([DS18B20_Module.Info] * 1,))
thread.start()

root.protocol("WM_DELETE_WINDOW", save_settings)
root.mainloop()
