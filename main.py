import tkinter as tk
import serial.tools.list_ports
import serial

selected_port = None
connected_sensors = []

def first_start():
    pass


def update_device_list(device_listbox):
    device_listbox.delete(0, tk.END)
    
    # Отримання списку доступних COM-портів
    ports = list(serial.tools.list_ports.comports())
    for port in ports:
        device_listbox.insert(tk.END, port.device)

def select_port(device_listbox, options_window):
    global selected_port
    selected_port_index = device_listbox.curselection()
    if selected_port_index:
        selected_port = device_listbox.get(selected_port_index[0])
        options_window.destroy()  # Закрити вікно після вибору
        update_connected_sensors()

def cancel_selection(options_window):
    options_window.destroy()  # Закрити вікно при скасуванні

def update_connected_sensors():
    global connected_sensors
    connected_sensors = []  # Очищаємо список підключених датчиків
    try:
        ser = serial.Serial(selected_port, 9600, timeout=1)  # Параметри можуть змінюватися відповідно до налаштувань CP2102
        ser.write(b'GET_SENSORS\n')  # Відправляємо запит на підключені датчики
        response = ser.readline().decode().strip()
        connected_sensors = response.split(',')
        ser.close()
        display_connected_sensors()  # Викликаємо функцію для оновлення відображення
    except serial.SerialException:
        print("Помилка підключення до порту", selected_port)

# Функція для відображення підключених датчиків
def display_connected_sensors():
    connected_sensors_text = ", ".join(connected_sensors)
    connected_sensors_label.config(text="Підключені датчики: " + connected_sensors_text)

# Функція, яка викликається при виборі пункту "Опції"
def open_options():
    global selected_port
    selected_port = None

    options_window = tk.Toplevel(root)
    options_window.title("Опції")
    options_window.geometry("400x350")  # Новий розмір вікна

    device_listbox = tk.Listbox(options_window)
    device_listbox.pack(fill=tk.BOTH, expand=True)  # Розмістити таблицю по всій ширині та висоті

    update_button = tk.Button(options_window, text="Обновити список портів", command=lambda: update_device_list(device_listbox))
    update_button.pack()

    buttons_frame = tk.Frame(options_window)
    buttons_frame.pack(side=tk.RIGHT, padx=10, pady=10)  # Розмістити кнопки праворуч з відступами

    ok_button = tk.Button(buttons_frame, text="Ок", command=lambda: select_port(device_listbox, options_window))
    ok_button.pack(side=tk.RIGHT, padx=5)

    cancel_button = tk.Button(buttons_frame, text="Відміна", command=lambda: cancel_selection(options_window))
    cancel_button.pack(side=tk.RIGHT, padx=5)

# Створення головного вікна
root = tk.Tk()
root.title("Головне вікно")
root.geometry("800x600")  # Новий розмір вікна

# Створення меню
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

options_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Опції", menu=options_menu)  # Змінене назва меню
options_menu.add_command(label="Відобразити порти", command=open_options)

# Створення мітки для відображення підключених датчиків
connected_sensors_label = tk.Label(root, text="Підключені датчики:")
connected_sensors_label.pack()

root.mainloop()
