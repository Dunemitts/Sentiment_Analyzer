import cx_Oracle
from contextlib import contextmanager
import os
from dotenv import load_dotenv, dotenv_values
import pandas as pd
import csv

load_dotenv()
cx_Oracle.init_oracle_client(lib_dir=os.getenv("CX_ORACLE_LOCATION"))

def read_csv_file(file_path):
    df = pd.read_csv(file_path)
    return df

@contextmanager
def connect_to_db(username, password, ip, port, service_name):
    conn = cx_Oracle.connect(f'{username}/{password}@{ip}:{port}/{service_name}')
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

def create_table(conn, table_name):
    table_name = table_name.upper()
    check_table_query = f"""
    SELECT COUNT(*) FROM user_tables WHERE table_name = '{table_name}'
    """
    result = execute_query(conn, check_table_query)
    count = result.fetchone()[0]
    
    if count > 0:
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

def prepare_data_for_insertion(df):
    prepared_data = []
    hotel_id = 1

    for _, row in df.iterrows():
        hotel_id += 1
        hoteld_id = int(hotel_id)
        name = str(row['NAME']) if pd.notna(row['NAME']) else 'Unknown'
        city = str(row['CITY']) if pd.notna(row['CITY']) else 'Unknown'
        country = str(row['COUNTRY']) if pd.notna(row['COUNTRY']) else 'Unknown'

        prepared_data.append({
            'HOTELID': hoteld_id,
            'NAME': name,
            'CITY': city,
            'COUNTRY': country
        })
        
    return prepared_data

def insert_query(conn, table_name, data):
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
                formatted_item = (
                    str(item['HOTELID']-1),
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

def select_query(conn, table_name):
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

def insert_reviews_from_csv(conn, table_name, table_name_foreign, df, data_dir):
    review_table = table_name
    hotels_table = table_name_foreign
    
    # Check if the review table exists
    check_review_table = f"SELECT COUNT(*) FROM user_tables WHERE table_name = '{review_table}'"
    result = execute_query(conn, check_review_table)
    if result.fetchone()[0] == 0:
        print(f"No {review_table} table found.")
        return

    review_count = 0
    review_id = 1
    batch_size = 100

    try:
        # Iterate over each hotel in the Hotels.csv file
        for _, row in df.iterrows():
            hotel_id = row['HOTELID']
            hotel_name = row['NAME'].replace(" ", "-")
            city = row['CITY']

            # Construct the path to the review file
            review_file_path = os.path.join(data_dir, "processed_data", city.lower(), f"{hotel_name}_processed.csv")

            # Read the review file
            try:
                reviews_df = pd.read_csv(review_file_path, header=0)
            except FileNotFoundError:
                print(f"File not found: {review_file_path}")
                continue

            # Process the reviews
            for i in range(0, len(reviews_df), batch_size):
                batch = reviews_df.iloc[i:i+batch_size]
                for index, review_row in batch.iterrows():
                    review_count += 1

                    breakfast = review_row.get('breakfast', '0').split(':')[1].strip().replace('★', '') if 'breakfast' in review_row else '0'
                    cleanliness = review_row.get('cleanliness', '0').split(':')[1].strip().replace('★', '') if 'cleanliness' in review_row else '0'
                    price = review_row.get('price', '0').split(':')[1].strip().replace('★', '') if 'price' in review_row else '0'
                    service = review_row.get('service', '0').split(':')[1].strip().replace('★', '') if 'service' in review_row else '0'
                    location = review_row.get('location', '0').split(':')[1].strip().replace('★', '') if 'location' in review_row else '0'

                    # Insert the review
                    insert_query = f"""
                    INSERT INTO {review_table} (REVIEWID, HOTELID, BREAKFASTSCORE, CLEANSCORE, PRICESCORE, SERVICESCORE, LOCALSCORE)
                    VALUES (:id, :hotel_id, :breakfast, :cleanliness, :price, :service, :location)
                    """
                    execute_query(
                        conn,
                        insert_query,
                        {
                            'id': review_id,
                            'hotel_id': hotel_id,
                            'breakfast': breakfast,
                            'cleanliness': cleanliness,
                            'price': price,
                            'service': service,
                            'location': location
                        }
                    )
                    review_id += 1

                conn.commit()
                print(f"Batch inserted for {hotel_name}. Total reviews inserted: {review_count}")

        print(f"All reviews processed. Total reviews inserted: {review_count}")
    except Exception as e:
        print(f"Error processing reviews: {str(e)}")
        conn.rollback()
    finally:
        conn.commit()

def main(conn):
    processed_data_folder = os.getenv("ANALYZER_LOCATION")
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

    insert_reviews_from_csv(conn, "REVIEW", "HOTELS", df, processed_data_folder)

if __name__ == "__main__":
    username = os.getenv("DATABASE_USER")
    password = os.getenv("DATABASE_PASSWORD")
    ip = "localhost"
    port = 1521
    service_name = os.getenv("SERVICE_NAME")
    with connect_to_db(username, password, ip, port, service_name) as conn:
        main(conn)
