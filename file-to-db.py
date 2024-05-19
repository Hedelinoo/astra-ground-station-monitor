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
        byte1 INTEGER,
        byte2 INTEGER,
        byte3 INTEGER,
        byte4 INTEGER,
        byte5 INTEGER,
        byte6 INTEGER,
        byte7 INTEGER,
        sentReceived STRING NOT NULL
    );''')
    
    return conn, cursor

def handle_data_packet(packet: str, cursor):
    data = packet.split(';')[1:]
    packet_id = int(data[0])
    data_bytes = []

    for d in data[1:]:
        if not d.isnumeric():
            break
        data_bytes.append(int(d))

    # Ensure the list has exactly 7 elements
    while len(data_bytes) < 7:
        data_bytes.append(None)
    
    cursor.execute('''
    INSERT INTO packets (packet_id, byte1, byte2, byte3, byte4, byte5, byte6, byte7, sentReceived)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    ''', (packet_id, *data_bytes, 'received'))
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
