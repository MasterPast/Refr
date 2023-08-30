import tkinter as tk
import serial.tools.list_ports
import serial


t_last_err = 0
g_current_com_port_id = -1

ds_err_ok = 0
ds_err_port = -10
ds_err_no_sensor = -11
ds_err_io = -12
ds_err_baud_rate = -13

class ds_data_byte:
    def __init__(self):
        self.l_temo = 0
        self.h_temo = 0
        self.h_user = 0
        self.l_user = 0
        self.config = 0
        self.x1 = 0
        self.x2 = 0
        self.x3 = 0
        self.crc = 0

port_only = -10

def get_last_err():
    return t_last_err

def get_last_err_string(err=-1):
    if err == -1:
        err = t_last_err
    if err == ds_err_ok:
        return "No errors"
    elif err == ds_err_port:
        return "Failed to open port"
    elif err == ds_err_no_sensor:
        return "Temperature sensor not found"
    elif err == ds_err_io:
        return "Error communicating with the sensor"
    elif err == ds_err_baud_rate:
        return "Error changing baud rate"

def close_port(port=port_only):
    global g_current_com_port_id, t_last_err
    test_port_id(port)
    if isinstance(port, str):
        port_id = serial_port_id(port)
    else:
        port_id = port
    if is_serial_port(port):
        set_serial_port_status(port, pb_serial_port_dtr, 0)
        set_serial_port_status(port, pb_serial_port_rts, 0)
        close_serial_port(port)
        t_last_err = ds_err_ok
        return True
    else:
        t_last_err = ds_err_port
        return False

def open_port(com_port, port=port_only):
    global g_current_com_port_id, t_last_err
    if port >= 0:
        close_port(port)
        port_id = port
    else:
        port_id = pb_any
    id = open_serial_port(port_id, com_port, 115200, pb_serial_port_no_parity, 8, 1, pb_serial_port_rts_handshake, 24, 24)
    if id:
        if port == port_only:
            g_current_com_port_id = id
        elif port >= 0:
            id = port
        set_serial_port_status(id, pb_serial_port_dtr, 1)
        set_serial_port_status(id, pb_serial_port_rts, 1)
        t_last_err = ds_err_ok
        return id
    else:
        t_last_err = ds_err_port
        return False

def reset_ds(port=port_only):
    global t_last_err
    test_port_id(port)
    t_last_err = ds_err_ok
    if is_serial_port(port):
        if set_baud_rate(port, 9600):
            clear_in_buf(port)
            x = 0xF0
            write_serial_port_data(port, x)
            x = elapsed_milliseconds() + 100
            while available_serial_port_input(port) == 0 and elapsed_milliseconds() < x:
                delay(2)
            if available_serial_port_input(port) == 1:
                x = 0
                if read_serial_port_data(port, x) == 1:
                    if x != 0xF0:
                        t_last_err = ds_err_no_sensor
                        return False
                else:
                    t_last_err = ds_err_no_sensor
                    return False
            else:
                t_last_err = ds_err_no_sensor
                return False
            set_baud_rate(port, 115200)
            return True
    else:
        t_last_err = ds_err_port
        return False

def byte_rw(byte=0xFF, port=port_only):
    global t_last_err
    test_port_id(port)
    t_last_err = ds_err_ok
    result = 0xFF
    if is_serial_port(port):
        clear_in_buf(port)
        time = elapsed_milliseconds() + 100
        for i in range(8):
            x = odd(byte) * 0xFF
            write_serial_port_data(port, x)
            byte >>= 1
            while available_serial_port_input(port) == 0 and elapsed_milliseconds() < time:
                pass
            if available_serial_port_input(port) == 1:
                x = 0
                if read_serial_port_data(port, x) == 1:
                    result >>= 1
                    if odd(x):
                        result |= 0x80
                else:
                    result = 0xFF
                    t_last_err = ds_err_io
                    break
            else:
                result = 0xFF
                t_last_err = ds_err_io
                break
    else:
        t_last_err = ds_err_port
    return result

def get_crc(buff, count):
    global t_last_err
    count -= 1
    crc = 0
    for i in range(count + 1):
        byte = buff[i].byte
        for x in range(8):
            if (byte ^ crc) & 1:
                crc = ((crc >> 1) | 0x80) & 0xFF
            else:
                crc >>= 1
            byte >>= 1
    return crc

def get_thermo(info, port=port_only):
    global t_last_err
    t_last_err = ds_err_ok
    test_port_id(port)
    if is_serial_port(port):
        clear_in_buf(port)
        if reset_ds(port):
            byte_rw(0xCC, port)
            byte_rw(0x44, port)
            delay(800)
            if reset_ds(port):
                byte_rw(0xCC, port)
                byte_rw(0xBE, port)
                for i in range(9):
                    info.byte[i] = byte_rw(0xFF, port)
                return True
    else:
        t_last_err = ds_err_port
    return False
