Note:

The provided txt files are used for testing, with hotel_testing.txt being a smaller scale version than uk_england_london_britannia_international_hotel.txt

The main function to process the files is process_file(filename) while the other two functions, display_stopwords_and_lemmatize(filename) and analyze_document_sentiment(filename) are used purely to display answers for CIT 44400/CIT 58100 Homework 6, they do not contribute to the processed file at all.

(OUTDATED) There is already a processed file in the repository called hotel_processed.csv (which can be overwritten) that displays an end product of processing hotel_texting.txt

Since the database is on an Oracle Environment, the sql file is best opened in a program like Oracle SQL Developer, creating a new database in there and setting the environment variables in a .env file to your user and password.

.ENV Variables Needed:
DATABASE_USER = username
DATABASE_PASSWORD = password
SERVICE_NAME = service name
CX_ORACLE_LOCATION = cx_Oracle client location

Pip Installs:
pip install nltk transformers scipy pandas cx_oracle

FOR CX_ORACLE:
https://www.youtube.com/watch?v=C9op6I-4WM0

HOW TO USE:
1. (In Oracle SQL Developer) create a connection and input connection information into .ENV
1. (In IDE Terminal) python database_connection.py to connect to the database
2. (In IDE Terminal) python gui.py
3. Type in file name of hotel from data folder (i.e. usa_illinois_chicago_abbott_hotel)

import cx_Oracle requires the oracle instant client (light) to function https://www.oracle.com/database/technologies/instant-client/downloads.html
- MAKE SURE TO INCLUE THE PATH OF DOWNLOAD TO THE ENVIRONMENT VARIABLES ON PC (System Properties > Advanced > Environment Variables)