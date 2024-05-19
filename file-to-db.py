import sqlite3
import os
import argparse

# Define the database connection and cursor
def initialize_db(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS raw_serial_data (
                        id INTEGER PRIMARY KEY,
                        packet STRING NOT NULL,
                        sentRecieved STRING NOT NULL);''')
    
    return conn, cursor

def read_file_and_write_to_db(file_path, cursor):
    with open(file_path, 'r') as file:
        for line in file:
            line_data = line.strip()
            if line_data:  # Ensure the line is not empty
                cursor.execute("INSERT INTO raw_serial_data (packet, sentRecieved) VALUES (?, ?);",
                               (line_data, 'received'))
                cursor.connection.commit()

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
