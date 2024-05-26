#! /usr/bin/env python
import serial
import argparse
import os

temperatureValues: list[int| None] = [None] * 15 

import time

start_time = time.time()

def millis_since_start():
    current_time = time.time()
    millis = (current_time - start_time) * 1000
    return str(int(millis))


def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')


def print_temperature_values(temperature_values: list[int | None]):
    clear_console()
    print("Temperature Values:")
    for i, temperature in enumerate(temperature_values):
        print(f"Sensor {i + 1}: {temperature}°C")
    print()

def handle_data_packet(packet: str, temperature_values: list[int | None]):
    data = packet.split(';')[1:]
    #print(f"Data: {data}")
    packet_id = int(data[0])
    packet_temperatures = []
    for d in data[1:]:
        if not d.isnumeric():
            break
        packet_temperatures.append(int(d) - 127)
    #print(f"Cleaned Data: {packet_temperatures}")
    match packet_id:
        case 4: 
            for i in range(7):
                temperature_values[i] = packet_temperatures[i]
            print_temperature_values(temperature_values)
        case 5: 
            for i in range(7, 14):
                temperature_values[i] = packet_temperatures[i - 7]
            print_temperature_values(temperature_values)
        case 6: 
            temperature_values[14] = packet_temperatures[0]
            print_temperature_values(temperature_values)
        case _: pass
        

def handle_serial_packet(packet: str, output):
    global temperatureValues
    with open(output, 'a+') as outfile:
        handle_data_packet(packet, temperatureValues)
        outfile.write(f"{millis_since_start()+ ";" + packet.strip()}\n")
        
def receive_serial_packets(port, output, on_receive_packet):
    ser = serial.Serial(
        port=port,
        baudrate=115200,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=None
    )

    try:
        data_str = ""
        while True:
            if ser.in_waiting > 0:
                data = ser.read(ser.in_waiting)
                data_str += data.decode('utf-8')
                while data_str.count("#") >= 2:
                    packet = data_str.split("#")[1]
                    data_str = "".join(data_str.split("#", 1)[2:])
                    #print("Packet: " + packet)  # Print the data
                    on_receive_packet(packet)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        ser.close()


def main():
    parser = argparse.ArgumentParser(description="Serial port reader script.")
    parser.add_argument('port', type=str, help="The serial port to use (e.g., /dev/cu.usbmodem111301)")
    parser.add_argument('output', type=str, help="The file to write the output to")
    args = parser.parse_args()
    receive_serial_packets(
        args.port, 
        args.output, 
        lambda packet: handle_serial_packet(packet, args.output)
    )



if __name__ == "__main__":
    main()
