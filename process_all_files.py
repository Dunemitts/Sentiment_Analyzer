import os
import shutil 
import csv
from main import ReviewAnalyzer

import warnings
warnings.filterwarnings('ignore', category=UserWarning, message='TypedStorage is deprecated')

import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def process_all_files(data_dir="data"):
    analyzer = ReviewAnalyzer()
    
    hotel_directories = []
    for root, dirs, files in os.walk(data_dir):
        if 'processed_data' in root:
            continue
        hotel_directories.append(root)
    print(f"Hotel Directories: {hotel_directories}")
    
    total_processed = 0
    
    batch_size = 50 #process files in batches
    for i in range(0, len(hotel_directories), batch_size):
        batch = hotel_directories[i:i+batch_size]
        print(f"Batch: {batch}")
        
        for city_dir in batch:
            print(f"Processing city directory: {city_dir}")
            try:
                for filename in os.listdir(city_dir):
                    try:
                        analyzer.search_processed_hotel(filename)
                        total_processed += 1
                        
                        if total_processed % 50 == 0:#log progress every 50 files
                            print(f"Processed {total_processed} hotels")
                    except Exception as e:
                        logging.error(f"Error processing {filename}: {str(e)}")
            except Exception as e:
                logging.error(f"Error accessing directory {city_dir}: {str(e)}")
    
    print(f"Total hotels processed: {total_processed}")

def scan_files_for_names(data_dir="data"): #makes a new csv for the names of the hotels
    hotel_directories = []
    for root, dirs, files in os.walk(data_dir):
        if 'processed_data' in root:
            continue
        hotel_directories.append(root)
    
    with open('Hotels.csv', 'w', newline='') as csvfile:
        hotel_writer = csv.writer(csvfile)
        hotel_writer.writerow(['HOTELID', 'NAME', 'CITY', 'COUNTRY'])
        
        total_hotels = 1
        
        batch_size = 50
        for i in range(0, len(hotel_directories), batch_size):
            batch = hotel_directories[i:i+batch_size]
            print(f"Processing batch: {batch}")
            
            for city_dir in batch:
                print(f"Processing city directory: {city_dir}")
                try:
                    for filename in os.listdir(city_dir):
                        try:#only works for a filename with COUNTRY, CITY, NAME 
                            

                            parts = filename.lower().split('_')
                            country = parts[0] #extract name information from the filename to find respective directory
                            
                            if country == "usa":#handle USA cities (including Chicago) differently
                                if os.path.basename(city_dir) not in ["new-york-city", "san-francisco"]:#check for countries with states so they can skip over states and only grab city
                                    hotel_name = '-'.join(parts[3:])#include the state names
                            elif country in ["uk"]:  #handle UK cities (including London) differently
                                hotel_name = '-'.join(parts[3:])
                            else:
                                hotel_name = '-'.join(parts[2:])

                            hotel_data = (total_hotels, hotel_name, os.path.basename(city_dir), country)
                            hotel_writer.writerow(hotel_data)
                            total_hotels += 1
                        except Exception as e:
                            logging.error(f"Error processing {filename}: {str(e)}")
                except Exception as e:
                    logging.error(f"Error accessing directory {city_dir}: {str(e)}")
    
    print(f"Total hotels processed: {total_hotels}")

if __name__ == "__main__":
    #scan_files_for_names() #creates a new csv called Hotels to put names of hotels into database
    try:
        process_all_files()
    except KeyboardInterrupt:
        print("Process interrupted by user.")
    except Exception as e:
        logging.exception("An unexpected error occurred:")

#python -W ignore::UserWarning: process_all_files.py