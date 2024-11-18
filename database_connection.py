import cx_Oracle #requires the oracle instant client (light) to function https://www.oracle.com/database/technologies/instant-client/downloads.html

from contextlib import contextmanager #automatically close the connection when done

import os #importing os module for environment variables
from dotenv import load_dotenv, dotenv_values #importing necessary functions from dotenv library
import pandas as pd #used to iterate through csv files and folders
import csv

load_dotenv() #loading variables from .env file
cx_Oracle.init_oracle_client(lib_dir=os.getenv("CX_ORACLE_LOCATION")) #path of instantclient should look something like "C:\Users\Lance\Documents\SchoolVSCode\cit44400\instantclient_23_6"

def read_csv_file(file_path): #read csv
    df = pd.read_csv(file_path)
    return df

@contextmanager
def connect_to_db(username, password, ip, port, service_name): #connects to db
    conn = cx_Oracle.connect(f'{username}/{password}@{ip}:{port}/{service_name}') #f'{username}/{password}@{ip}:{port}/{service_name}'
    print(conn)
    try:
        yield conn
        print("database connected!")
    finally:
        print("closing connection")
        conn.close()

def execute_query(conn, query, params=None): #used to execute sql queries
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
        clear_table = f"""
        TRUNCATE TABLE {table_name}
        """
        execute_query(conn, clear_table)
        print(f"Table {table_name} cleared.")
    else:
        print(f"Creating new table {table_name}...")
        create_table_query = f"""
        CREATE TABLE {table_name} (
            HOTELID NUMBER(38, 0) PRIMARY KEY,
            NAME VARCHAR2(100) NOT NULL,
            CITY VARCHAR2(100),
            COUNTRY VARCHAR2(100)
        )
        """
        execute_query(conn, create_table_query)
        print(f"Table {table_name} created successfully.")
    
    return table_name

def prepare_data_for_insertion(df): #returns a list 
    prepared_data = []

    hotel_id = 1  #start with 1 since HOTELID is NUMBER(38, 0)

    for _, row in df.iterrows():
        hotel_id += 1
        
        hoteld_id = int(hotel_id)#makes HOTELID is an integer
        
        name = str(row['NAME']) if pd.notna(row['NAME']) else 'Unknown'#handle NaN values
        city = str(row['CITY']) if pd.notna(row['CITY']) else 'Unknown'
        country = str(row['COUNTRY']) if pd.notna(row['COUNTRY']) else 'Unknown'

        prepared_data.append({
            'HOTELID': hoteld_id,
            'NAME': name,
            'CITY': city,
            'COUNTRY': country
        })

    return prepared_data

def insert_query(conn, table_name, data): #inserts data into table
    insert_query = f"""
    INSERT INTO {table_name} (HOTELID, NAME, CITY, COUNTRY)
    VALUES (:0, :1, :2, :3)
    """

    print(f"Starting insertion for table {table_name}")
    print(f"Number of rows to insert: {len(data)}")
    with conn.cursor() as cursor:
        try:
            for item in data:
                print(f"Inserting row: {item}")
                
                formatted_item = (#ensure all values are strings
                    str(item['HOTELID']),
                    item['NAME'],
                    item['CITY'],
                    item['COUNTRY']
                )
                
                cursor.execute(insert_query, formatted_item)
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


def create_rated_table(conn, table_name, table_name_foreign): #takes in 2 table names and uses the second as a foreign key, returns both names
    table_name = table_name.upper()
    check_table_query = f"""
    SELECT COUNT(*) FROM user_tables WHERE table_name = '{table_name}'
    """
    result = execute_query(conn, check_table_query)
    count = result.fetchone()[0] #gathers a count of other tables with the same name
    
    if count > 0: #checks if table already exists with the same name
        print(f"Table {table_name} already exists.")
        clear_table = f"""
        TRUNCATE TABLE {table_name}
        """
        execute_query(conn, clear_table)
        print(f"Table {table_name} cleared.")
    else:
        print(f"Creating new table {table_name}...")
        create_table_query = f"""
        CREATE TABLE {table_name} (
            RATINGID INT PRIMARY KEY,
            HOTELID INT,
            BREAKFASTSCORE INT,
            CLEANSCORE INT,
            PRICESCORE INT,
            SERVICESCORE INT,
            LOCALSCORE INT,
            FOREIGN KEY (HOTELID) REFERENCES {table_name_foreign}(HOTELID)
        )
        """
        execute_query(conn, create_table_query)
        print(f"Table {table_name} created successfully.")
    
    return table_name, table_name_foreign

def insert_average_ratings(conn, table_name, table_name_foreign, data_dir): #inserts average hotel ratings into database
    hotel_directories = []
    for root, dirs, files in os.walk(data_dir):
        hotel_directories.append(root)

    total_hotels = len(hotel_directories)
    print(f"Looking at {total_hotels}")
    batch_size = 10
    ratings_id = 1
    for i in range(0, total_hotels, batch_size):
        batch = hotel_directories[i:i+batch_size]
        print(f"Processing batch: {batch}")
        
        for city_dir in batch:#get all city folders from processed_data folder
            print(f"Processing city directory: {city_dir}")
            try:
                for filename in os.listdir(city_dir):
                    try:
                        parts = filename.lower().split('_') #name finding logic
                        country = parts[0] #extract name information from the filename to find respective directory
                        
                            
                        if country == "usa":#handle USA cities (including Chicago) differently
                            if os.path.basename(city_dir) not in ["new-york-city", "san-francisco"]:#check for countries with states so they can skip over states and only grab city
                                city = parts[2]
                                hotel_name = '-'.join(parts[3:])#include the state names
                        elif country in ["uk"]:  #handle UK cities (including London) differently
                            city = parts[2]
                            hotel_name = '-'.join(parts[3:])
                        else:
                            city = parts[1]
                            hotel_name = '-'.join(parts[2:])
                        
                        df = pd.read_csv(os.path.join(city_dir, filename))#read the CSV file
                        
                        df['breakfast'] = df['breakfast'].astype(str).str.replace('breakfast:', '').replace('★', '')
                        df['breakfast'] = df['breakfast'].str.replace('★', '')
                        df['cleanliness'] = df['cleanliness'].astype(str).str.replace('cleanliness:', '').replace('★', '')
                        df['cleanliness'] = df['cleanliness'].str.replace('★', '')
                        df['price'] = df['price'].astype(str).str.replace('price:', '').replace('★', '')
                        df['price'] = df['price'].str.replace('★', '')
                        df['service'] = df['service'].astype(str).str.replace('service:', '').replace('★', '')
                        df['service'] = df['service'].str.replace('★', '')
                        df['location'] = df['location'].astype(str).str.replace('location:', '').replace('★', '')
                        df['location'] = df['location'].str.replace('★', '')
                        
                        avg_ratings = { #calculate average ratings
                            'breakfast': round(df['breakfast'].astype(float).mean()),
                            'cleanliness': round(df['cleanliness'].astype(float).mean()),
                            'price': round(df['price'].astype(float).mean()),
                            'service': round(df['service'].astype(float).mean()),
                            'location': round(df['location'].astype(float).mean())
                        }

                        print(f"Processing hotel: {hotel_name.replace('-processed.csv', '')}")

                        try:
                            #finds matching hotel in hotels table
                            select_query = f"""
                            SELECT HOTELID FROM {table_name_foreign} WHERE NAME LIKE :name AND CITY LIKE :city
                            """
                            result = execute_query(conn, select_query, params={'name': hotel_name.replace('-processed.csv', ''), 'city': city})
                            hotel_id = result.fetchone()[0]

                            #insert ratings into table
                            insert_query = f"""
                            INSERT INTO {table_name} (RATINGID, HOTELID, BREAKFASTSCORE, CLEANSCORE, PRICESCORE, SERVICESCORE, LOCALSCORE)
                            VALUES (:ratings_id, :hotel_id, :breakfast, :cleanliness, :price, :service, :location)
                            """
                            
                            execute_query(conn, insert_query, params={
                                'ratings_id': ratings_id,
                                'hotel_id': hotel_id,
                                'breakfast': avg_ratings['breakfast'],
                                'cleanliness': avg_ratings['cleanliness'],
                                'price': avg_ratings['price'],
                                'service': avg_ratings['service'],
                                'location': avg_ratings['location']
                            })
                            ratings_id += 1
                        except cx_Oracle.Error as e:
                            print(f"Error processing hotel {hotel_name}: {str(e)}")
                    except Exception as e:
                        print(f"Error processing {filename}: {str(e)}")
            except Exception as e:
                print(f"Error accessing directory {city_dir}: {str(e)}")
                
        conn.commit()
        print("Average ratings inserted successfully.")

def main(conn): #currently used for inserting Hotel.csv rows to hotels table
    processed_data_folder = r"C:\Users\13178\Documents\GitHub\Sentiment_Analyzer"
    hotel_file = os.path.join(processed_data_folder, 'Hotels.csv')

    hotels_table = create_table(conn, "hotels")
    
    df = read_csv_file(hotel_file)
    prepared_data = prepare_data_for_insertion(df)

    print(f"Prepared data types:")
    for col in ['HOTELID', 'NAME', 'CITY', 'COUNTRY']:
        print(f"{col}: {prepared_data[0][col]} ({type(prepared_data[0][col])})")

    print(f"\nFirst few items:")
    for item in prepared_data[:5]:
        print(item)

    insert_query(conn, hotels_table, prepared_data)
    print(f"Inserted {len(prepared_data)} rows from Hotels.csv")
    
    select_query(conn, hotels_table)

        
if __name__ == "__main__":
    username = os.getenv("DATABASE_USER")
    password = os.getenv("DATABASE_PASSWORD")
    ip = "localhost"
    port = 1521  #default Oracle port
    service_name = os.getenv("SERVICE_NAME")
    with connect_to_db(username, password, ip, port, service_name) as conn:
        #main(conn)
        ratings, hotels = create_rated_table(conn, "ratings", "hotels")
        insert_average_ratings(conn, ratings, hotels, r"processed_data") #input parent directory to search from