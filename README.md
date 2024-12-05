# Hotel Review Sentiment Analyzer
This is a final project that processes text files from the data directory, turning them into csv's which would then be inserted into an Oracle SQL Database for storage while the reviews will be calculated on the frontend and displayed via a gui created from Tkinter.

## Table of Contents
1. [Installation & Preparation](#installation--preparation)
2. [Usage](#usage)
3. [Contributing](#contributing)
4. [License](#license)
5. [Project Documentation](#project-documentation)


Since the database is on an Oracle Environment, the sql file is best opened in a program like Oracle SQL Developer, creating a new database in there and setting the environment variables in a .env file to your user and password.


## Installation & Preparation
- For CX_ORACLE: https://www.youtube.com/watch?v=C9op6I-4WM0
- import cx_Oracle requires the oracle instant client (light) to function https://www.oracle.com/database/technologies/instant-client/downloads.html

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install packages.

```bash
pip install nltk transformers scipy pandas cx_oracle
```
.ENV Variables Needed: 
- DATABASE_USER = username 
- DATABASE_PASSWORD = password 
- SERVICE_NAME = service name 
- CX_ORACLE_LOCATION = cx_Oracle client location
- ANALYZER_LOCATION = Sentiment_Analyzer location
- MAKE SURE TO INCLUE THE PATH OF DOWNLOAD TO THE ENVIRONMENT VARIABLES ON PC (System Properties > Advanced > Environment Variables)

## Usage

0.1. (In IDE Terminal) python process_all_files.py to process every data txt file from the data folder to the processed_data folder
1. (In Oracle SQL Developer) create a connection and input connection information into .ENV
2. (In IDE Terminal) python database_connection.py to connect to the database
3. (In IDE Terminal) python gui.py
   - Type in file name of hotel from data folder (i.e. usa_illinois_chicago_abbott_hotel)

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)

## Project Documentation
Side Note:

The main function to process the files is process_file(filename) while the other two functions, display_stopwords_and_lemmatize(filename) and analyze_document_sentiment(filename) are used purely to display answers for CIT 44400/CIT 58100 Homework 6, they do not contribute to the processed file at all.

The provided txt files are used for testing, with hotel_testing.txt being a smaller scale version than uk_england_london_britannia_international_hotel.txt
(OUTDATED) There is already a processed file in the repository called hotel_processed.csv (which can be overwritten) that displays an end product of processing hotel_texting.txt
### Main.py

#### Overview
This script implements a ReviewAnalyzer class that performs sentiment analysis and categorization of hotel reviews. It uses natural language processing techniques and machine learning models to analyze text data.

#### Main Components
- Natural Language Processing libraries (NLTK, WordNet)
- Machine Learning libraries (transformers, scipy)
- File handling libraries (os, csv, pandas)
- Random selection library (random)
- ReviewAnalyzer Class:
  - Initializes with pre-trained RoBERTa model for sentiment analysis
  - Provides methods for:
    - Removing stopwords and lemmatizing text
    - Analyzing sentiment using RoBERTa
    - Categorizing reviews based on predefined keywords
    - Processing hotel review files
    - Searching for processed hotel files
    - Filtering hotels based on user-specified criteria
    - Analyzing document-level sentiment and average ratings
- Main Function:
  - Prompts user input for hotel name
  - Calls methods to analyze reviews and display results

#### Key Features
- Sentiment Analysis: Uses RoBERTa model for sentiment scoring
- Category Categorization: Identifies categories like breakfast, cleanliness, price, service, location
- Document-Level Analysis: Calculates overall sentiment and average ratings per category
- File Processing: Processes raw hotel review files and saves processed data
- Data Visualization: Displays results including positive/negative reviews count and average ratings
- Hotel Filtering: Allows users to filter hotels based on specific criteria


#### Usage
1. User inputs a hotel name
2. Script searches for existing processed data or processes new data if needed
3. Analyzes sentiment and categorizes reviews
4. Filters hotels based on user-specified criteria
5. Displays document-level sentiment analysis and average ratings

### Process_All_Files.py

#### Overview
This script, process_all_files.py, is designed to process hotel review files stored in a directory structure and generate a comprehensive analysis of the reviews. It builds upon the functionality of the ReviewAnalyzer class from the main.py file.

#### Main Components
- Standard library modules (os, shutil, csv)
- Custom ReviewAnalyzer class from main.py
- Warning and logging modules for better error handling and debugging
- Main Functions:
  - process_all_files(): The primary function that processes all hotel review files
  - scan_files_for_names(): Creates a CSV file listing all hotel names

#### Key Features
- Batch Processing: Files are processed in batches to manage memory usage efficiently
- Directory Traversal: Walks through hotel directories to find and process relevant files
- Progress Logging: Logs progress regularly to track processing status
- Error Handling: Implements try-except blocks for robust error management
- CSV Generation: Creates a Hotels.csv file listing hotel details
#### Usage:
1. python process_all_files.py

### GUI.py

#### Overview
This script, gui.py, creates a graphical user interface (GUI) for the Hotel Review Analyzer application. It utilizes the Tkinter library to build a user-friendly interface for interacting with the ReviewAnalyzer functionality.

#### Main Components
- Tkinter library for GUI creation
- Custom ReviewAnalyzer class from main.py
- OS module for file path operations
- HotelGUI Class:
  - Manages the entire GUI application
  - Handles user interactions and displays results

#### Key Features
- User Interface:
  - Dropdown menu for selecting cities
  - Advanced filtering functionality
  - Listbox for displaying available hotels
  - Buttons for searching and selecting hotels
  - Result display area showing sentiment analysis and ratings
- Functionality:
  - Searches for existing processed hotel files
  - Processes new hotel files if not found
  - Performs document-level sentiment analysis
  - Displays results including positive/negative reviews and average ratings
#### Usage:
The GUI allows users to interact with the Hotel Review Analyzer in the following ways:
- Select a city from the dropdown menu
- Filter desirable attributes for hotels
- View a list of available hotels for the selected city
- Select a hotel from the list to view its analysis

### database_connection.py

#### Overview
This script, database_connection.py, establishes a connection to an Oracle database and provides functions for interacting with it. It includes functionality for creating tables, inserting data, and performing queries.

#### Main Components
- cx_Oracle: For connecting to Oracle databases
- contextmanager: For automatic connection closure
- os: For environment variable handling
- dotenv: For loading environment variables from a .env file
- pandas: For reading CSV files
- csv: For general CSV operations
- Database Connection Functions:
  - connect_to_db: Establishes a connection to the database
  - execute_query: Executes SQL queries on the connected database
  - create_table: Creates a new table if it doesn't exist
  - insert_query: Inserts data into a specified table
  - select_query: Selects data from a table (used for demonstration)

#### Key Features
- Environment Variable Handling: Uses .env file for sensitive information storage
- Table Management: Automatically creates tables if they don't exist
- Batch Processing: Implements batch processing for efficient data insertion
- Error Handling: Includes try-except blocks for robust error management
- CSV File Processing: Reads and prepares data from CSV files for insertion
#### Usage:
The script can be run as part of a larger application. It sets up the database connection and provides functions for various database operations.
1. python database_connection.py

