import sqlite3
import os
import argparse

# Define the database connection and cursor
def initialize_db(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create tables if they do not exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS packets (
        id INTEGER PRIMARY KEY,
        packet_id INTEGER NOT NULL,
        temperature1 INTEGER,
        temperature2 INTEGER,
        temperature3 INTEGER,
        temperature4 INTEGER,
        temperature5 INTEGER,
        temperature6 INTEGER,
        temperature7 INTEGER,
        temperature8 INTEGER,
        temperature9 INTEGER,
        temperature10 INTEGER,
        temperature11 INTEGER,
        temperature12 INTEGER,
        temperature13 INTEGER,
        temperature14 INTEGER,
        sentReceived STRING NOT NULL
    );''')
    
    return conn, cursor

def handle_data_packet(packet: str, cursor):
    data = packet.split(';')[1:]
    packet_id = int(data[0])
    packet_temperatures = []
    
    for d in data[1:]:
        if not d.isnumeric():
            break
        packet_temperatures.append(int(d) - 127)

    temperature_values = [None] * 14
    if packet_id == 4:
        temperature_values[:7] = packet_temperatures[:7]
    elif packet_id == 5:
        temperature_values[7:] = packet_temperatures[:7]
    elif packet_id == 6:
        temperature_values[14-1] = packet_temperatures[0]
    
    cursor.execute('''
    INSERT INTO packets (packet_id, temperature1, temperature2, temperature3, temperature4, temperature5, temperature6, temperature7, temperature8, temperature9, temperature10, temperature11, temperature12, temperature13, temperature14, sentReceived)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    ''', (packet_id, *temperature_values, 'received'))
    cursor.connection.commit()

def read_file_and_write_to_db(file_path, cursor):
    with open(file_path, 'r') as file:
        for line in file:
            line_data = line.strip()
            if line_data:  # Ensure the line is not empty
                handle_data_packet(line_data, cursor)

def main():
    parser = argparse.ArgumentParser(description="Read a file and write its contents into a database.")
    parser.add_argument('db_path', type=str, help="The path to the database file")
    parser.add_argument('file_path', type=str, help="The path to the file to be read")
    args = parser.parse_args()

    if os.path.exists(args.file_path):
        conn, cursor = initialize_db(args.db_path)
        read_file_and_write_to_db(args.file_path, cursor)
        conn.close()
    else:
        print(f"The file {args.file_path} does not exist.")

if __name__ == "__main__":
    main()
