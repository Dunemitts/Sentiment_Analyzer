import cx_Oracle #requires the oracle instant client (light) to function https://www.oracle.com/database/technologies/instant-client/downloads.html
cx_Oracle.init_oracle_client(lib_dir=r"C:\Users\13178\Documents\GitHub\Sentiment_Analyzer\instantclient-basiclite-windows.x64-23.5.0.24.07\instantclient_23_5") #path of instantclient

from contextlib import contextmanager #automatically close the connection when done

import os #importing os module for environment variables
from dotenv import load_dotenv, dotenv_values #importing necessary functions from dotenv library
load_dotenv() #loading variables from .env file


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

def main():
    print(os.getenv("DATABASE_USER")) #accessing and printing value

    username = os.getenv("DATABASE_USER")
    password = os.getenv("DATABASE_PASSWORD")
    ip = "localhost"
    port = 1521  # Default Oracle port
    service_name = "orcl"
    
    with connect_to_db(username, password, ip, port, service_name) as conn:
        check_table_query = """
        SELECT COUNT(*) FROM user_tables WHERE table_name = 'HOTEL_REVIEWS'
        """
        result = execute_query(conn, check_table_query)
        count = result.fetchone()[0]
        
        if count > 0:
            print("Table hotel_reviews already exists.")
        else:
            print("Creating new table hotel_reviews...")
            create_table_query = """
            CREATE TABLE hotel_reviews (
                id CHAR(3) PRIMARY KEY,
                idHotel CHAR(3),
                idReview CHAR(3),
                overall_sentiment CHAR(4),
                review VARCHAR2(4000)
            )
            """
            execute_query(conn, create_table_query)
            print("Table created successfully.")

        # Example query
        insert_query = """
        INSERT INTO hotel_reviews (
            id,
            idHotel,
            idReview,
            overall_sentiment,
            review
        ) VALUES (
            '1',
            '1',
            '1',
            '64',
            :reviewText
        )
        """

        # Prepare the review text
        review_text = """'Oct 12 2009 	Nice trendy hotel location not too bad.	I stayed in this hotel for one night. As this is a fairly new place some of the taxi drivers did not know where it was and/or did not want to drive there. Once I have eventually arrived at the hotel I was very pleasantly surprised with the decor of the lobby/ground floor area. It was very stylish and modern. I found the reception's staff geeting me with 'Aloha' a bit out of place but I guess they are briefed to say that to keep up the coroporate image.As I have a Starwood Preferred Guest member I was given a small gift upon-check in. It was only a couple of fridge magnets in a gift box but nevertheless a nice gesture.My room was nice and roomy there are tea and coffee facilities in each room and you get two complimentary bottles of water plus some toiletries by 'bliss'.The location is not great. It is at the last metro stop and you then need to take a taxi but if you are not planning on going to see the historic sites in Beijing then you will be ok.I chose to have some breakfast in the hotel which was really tasty and there was a good selection of dishes. There are a couple of computers to use in the communal area as well as a pool table. There is also a small swimming pool and a gym area.I would definitely stay in this hotel again but only if I did not plan to travel to central Beijing as it can take a long time. The location is ok if you plan to do a lot of shopping as there is a big shopping centre just few minutes away from the hotel and there are plenty of eating options around including restaurants that serve dog meat!'"""

        # Execute the query with parameterized values
        execute_query(conn, insert_query, {'reviewText': review_text})

        select_query = "SELECT * FROM hotel_reviews"
        result = execute_query(conn, select_query)
        row = result.fetchone()
        if row:
            print("Data inserted successfully:")
            print(row)
        else:
            print("No rows returned after insertion")

        count_query = "SELECT COUNT(*) FROM hotel_reviews"
        result = execute_query(conn, count_query)
        count = result.fetchone()[0]
        print(f"Number of rows in hotel_reviews table: {count}")

        
if __name__ == "__main__":
    main()