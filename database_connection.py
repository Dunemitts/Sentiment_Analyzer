import cx_Oracle #requires the oracle instant client (light) to function https://www.oracle.com/database/technologies/instant-client/downloads.html
cx_Oracle.init_oracle_client(lib_dir=r"C:\Users\13178\Documents\GitHub\Sentiment_Analyzer\instantclient-basiclite-windows.x64-23.5.0.24.07\instantclient_23_5") #path of instantclient

from contextlib import contextmanager #automatically close the connection when done

import os #importing os module for environment variables
from dotenv import load_dotenv, dotenv_values #importing necessary functions from dotenv library
load_dotenv() #loading variables from .env file


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

def execute_query(conn, query):
    try:
        cur = conn.cursor()
        cur.execute(query)
        return cur
    except Exception as e:
        print(f"Error executing query: {e}")
        raise


def main():
    print(os.getenv("DATABASE_USER")) #accessing and printing value

    username = os.getenv("DATABASE_USER")
    password = os.getenv("DATABASE_PASSWORD")
    ip = "localhost"
    port = 1521  # Default Oracle port
    service_name = "orcl"
    
    with connect_to_db(username, password, ip, port, service_name) as conn:
        # Example query
        query = "SELECT * FROM hotel_reviews"
        cursor = execute_query(conn, query)
        
        # Process results
        try:
            print("trying query")
            for row in cursor:
                print(row)
        finally:
            print("closing cursor")
            cursor.close()

if __name__ == "__main__":
    main()