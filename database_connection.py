import cx_Oracle #requires the oracle instant client (light) to function https://www.oracle.com/database/technologies/instant-client/downloads.html
cx_Oracle.init_oracle_client(lib_dir=r"C:\Users\13178\Documents\GitHub\Sentiment_Analyzer\instantclient-basiclite-windows.x64-23.5.0.24.07\instantclient_23_5") #path of instantclient

from contextlib import contextmanager #automatically close the connection when done

import os #importing os module for environment variables
from dotenv import load_dotenv, dotenv_values #importing necessary functions from dotenv library
import pandas as pd #used to iterate through csv files and folders
import csv

load_dotenv() #loading variables from .env file

def read_csv_file(file_path): #read csv
    df = pd.read_csv(file_path)
    return df

def prepare_data_for_insertion(df, csv_file, city_folder_path, universal_id, hotel_id):
    prepared_data = []

    for _, row in df.iterrows():
        review_text = row['review']
        overall_sentiment = str(row['overall_sentiment']).zfill(4)
        
        id = str(universal_id).zfill(3) #always increments no matter what
        idHotel = str(hotel_id).zfill(3) #only increments when a new file is being imported
        idReview = str(row['index']).zfill(3) #takes on the 'index' column from the csv

        print(f'id = {id}')
        print(f'idHotel = {idHotel}')
        print(f'idReview = {idReview}')
        
        prepared_data.append({
            'id': id,
            'idHotel': idHotel,
            'idReview': idReview,
            'overall_sentiment': overall_sentiment,
            'review': review_text
        })

        universal_id += 1 #should always increment no matter what

    return prepared_data

@contextmanager
def connect_to_db(username, password, ip, port, service_name):
    conn = cx_Oracle.connect(f'{username}/{password}@{ip}:{port}/{service_name}') #f'{username}/{password}@{ip}:{port}/{service_name}'
    print(conn)
    try:
        yield conn
        print("database connected!")
    finally:
        print("closing connection")
        conn.close()

def execute_query(conn, query, params=None):
    try:
        cur = conn.cursor()
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)
        return cur
    except Exception as e:
        print(f"Error executing query: {e}")
        raise

def create_table(conn, table_name): #checks for table, and creates one if not there. it returns the table NAME (JUST THE NAME)
    table_name = table_name.upper()
    check_table_query = f"""
    SELECT COUNT(*) FROM user_tables WHERE table_name = '{table_name}'
    """
    result = execute_query(conn, check_table_query)
    count = result.fetchone()[0] #gathers a count of other tables with the same name
    
    if count > 0: #checks if table already exists with the same name
        print(f"Table {table_name} already exists.")
    else:
        print(f"Creating new table {table_name}...")
        create_table_query = f"""
        CREATE TABLE {table_name} (
            id CHAR(3) PRIMARY KEY,
            idHotel CHAR(3),
            idReview CHAR(3),
            overall_sentiment CHAR(4),
            review VARCHAR2(4000)
        )
        """
        execute_query(conn, create_table_query)
        print(f"Table {table_name} created successfully.")
    
    return table_name

def insert_query(conn, table_name, data): #inserts data into table
    insert_query = f"""
    INSERT INTO {table_name} (
        id,
        idHotel,
        idReview,
        overall_sentiment,
        review
    ) VALUES (
        :id,
        :idHotel,
        :idReview,
        :overall_sentiment,
        :review
    )
    """
    with conn.cursor() as cursor:
        try:
            cursor.executemany(insert_query, data)
            conn.commit()
            print(f"{len(data)} rows inserted successfully into {table_name}")
        except cx_Oracle.Error as e:
            print(f"Error inserting data: {e}")
            conn.rollback()

def select_query(conn, table_name): #counts rows and selects one random row from data (for demo)
    select_query = f"SELECT * FROM {table_name}"
    result = execute_query(conn, select_query)
    row = result.fetchone()
    if row:
        print(f"Data inserted into {table_name} successfully:")
        print(row)
    else:
        print(f"No rows returned in {table_name} after insertion")

    count_query = f"SELECT COUNT(*) FROM {table_name}"
    result = execute_query(conn, count_query)
    count = result.fetchone()[0]
    print(f"Number of rows in {table_name} table: {count}")

def main():
    username = os.getenv("DATABASE_USER")
    password = os.getenv("DATABASE_PASSWORD")
    ip = "localhost"
    port = 1521  #default Oracle port
    service_name = "orcl"

    universal_id = 1 #is a global variable because it's an index tracker
    hotel_id = 1 #also a global variable but increases every file change

    processed_data_folder = r"processed_data" #example path: processed_data\beijing\china_beijing_aloft_beijing_haidian_processed.csv
    city_folders = ["beijing", "chicago", "las-vegas", "london", "montreal", "new-delhi", "new-york-city", "san-francisco", "shanghai"]

    with connect_to_db(username, password, ip, port, service_name) as conn:
        hotel_table = create_table(conn, "hotel_reviews") #takes table name as a second argument (can be an input)
        
        for city in city_folders:
            city_folder_path = os.path.join(processed_data_folder, city)

            csv_files = [os.path.join(city_folder_path, file)
                         for file in os.listdir(city_folder_path)
                         if file.endswith('.csv') and 'processed' in file.lower()]

            if csv_files:
                print(f"Processing {city} files...")

                for csv_file in csv_files:
                    df = read_csv_file(csv_file)
                    prepared_data = prepare_data_for_insertion(df, csv_file, city_folder_path, universal_id, hotel_id)

                    insert_query(conn, hotel_table, prepared_data)
                    print(f"Inserted {len(prepared_data)} rows from {csv_file}")
                    hotel_id += 1 #increments every file change
                    universal_id += len(df)  # Increment universal_id by the number of rows in the current file
                print(f"Finished processing {city} files.\n")
            else:
                print(f"No processed csv files found in {city} folder.\n")

        #select_query(conn, hotel_table) #double checking data insertion

        
if __name__ == "__main__":
    main()