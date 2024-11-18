import os #file navigation
import shutil #moving output to processed_data folder
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

from transformers import AutoTokenizer, AutoModelForSequenceClassification #transformers is used for ROBERTA
from scipy.special import softmax

import csv #for document analysis
import pandas as pd
import random #for picking random sentences to show off display 

#nltk.download(['punkt','punkt_tab','averaged_perceptron_tagger','maxent_ne_chunker','words','stopwords','wordnet','vader_lexicon']) #required corpora found online

stop_words = set(stopwords.words('english')) #you can actually print this to see the entire list
lemmatizer = WordNetLemmatizer()

class ReviewAnalyzer:
    def __init__(self):
        self.index = 1 #index counter for lines
        self.model_name = "cardiffnlp/twitter-roberta-base-sentiment" #uses pretrained ROBERTA model instead of VADER
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
        self.file_processed = False #universal variable for gui processed file checking

    def remove_stopwords_and_lemmatize(self, input_text): #removes stop words and turns the individual words into a list with each words as its own string item
        tokens = word_tokenize(input_text.lower())
        filtered_tokens = [token for token in tokens if token not in stop_words] #stop words gone
        lemmatized_tokens = [lemmatizer.lemmatize(token) for token in filtered_tokens] #lemmatize
        return ' '.join(lemmatized_tokens)

    def analyze_sentiment_roberta(self, text):#returns a number depending on positivity
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        outputs = self.model(**inputs)#get the model outputs
        scores = outputs.logits.detach().numpy()[0]
        scores = softmax(scores)
        neg_tenth = int(scores[0] * 10) #grabs the 10th place value from negative and positive
        pos_tenth = int(scores[2] * 10) #the positive value in scores array is the 3rd value (position: 2)
        if neg_tenth >= 1 or pos_tenth >= 1: #if neither the negative value or positive value is high enough, they're considered over neutral (as neutral will always be dominant)
            if neg_tenth > pos_tenth:
                return '-1'
            else:
                return '1'
        else:
            return '0'

    def categorize_review(self, review): #gives scoring to set categories depending on sentiment and keywords
        categories = {#list of words that would be targettted to find the context around
            "breakfast": ["breakfast", "brunch", "lunch", "dining room", "morning meal", "continental breakfast", "full English breakfast", "cereal", "eggs", "pancakes", "waffles", "oatmeal", "toast", "baked goods", "fruit", "juice", "coffee", "tea", "breakie", "brekkie"],
            "cleanliness": ["clean", "dirty", "filthy", "unclean", "spotless", "hygiene", "tidiness", "neatness", "orderly", "organized", "spotless", "sterile", "sanitary", "hygienic", "dust-free", "clutter-free", "messy", "disheveled", "untidy", "chaotic"],
            "price": ["cheap", "expensive", "affordable", "overpriced", "value", "cost", "bill", "rate", "fee", "charge", "tariff", "expense", "budget-friendly", "steep", "reasonable", "worthwhile", "rip-off", "outrageous", "exorbitant", "astronomical", "sky-high", "eye-watering", "wallet-busting"],
            "service": ["staff", "helpful", "rude", "friendly", "unfriendly", "attentive", "inattentive", "efficient", "inefficient", "courteous", "impolite", "professional", "unprofessional", "welcoming", "aloof", "accommodating", "unaccommodating", "responsive", "irresponsive", "supportive", "unsupportive", "assisting", "neglecting"],
            "location": ["near", "far", "central", "remote", "proximity", "accessibility", "convenience", "location", "situation", "position", "placement", "setting", "ambience", "atmosphere", "environment", "surroundings", "vicinity", "locale", "spot", "place", "site"]
        }

        words = review.split()
        categorized_words = {}
        roberta_sentiments = []
        
        for i, word in enumerate(words):
            lower_word = word.lower()
            for category, keywords in categories.items():
                if any(lower_word in single_keyword for single_keyword in keywords):
                    context = ' '.join(words[max(0, i-3):min(i+3, len(words))]) #finds the previous 3 words and the next 3 words to put together in a sentence to find the sentiment of (using context)
                    sentiment = self.analyze_sentiment_roberta(context)
                    roberta_sentiments.append(sentiment)
                    
                    if sentiment >= '1':
                        categorized_words.setdefault(category, []).append(1)#signifies positive review for this category, will be combined later for a 0-5 star rating
                    elif sentiment <= '-1':
                        categorized_words.setdefault(category, []).append(-1)#signifies negative review for this category, will be combined later for a 0-5 star rating
        
        total_score = sum(map(int, roberta_sentiments))#calculate overall sentiment score (convert the sentiments from strings to integers before summing them)
        
        category_scores = {}
        for category in categories.keys():
            score = sum(categorized_words.get(category, []))
            if score > 5:
                score = 5
            elif score < 0:
                score = 0
            category_scores[category] = score

        return {
            "index": self.index,
            "categories": category_scores,
            "sentiment_paragraph": total_score,
            "review_text": review,
        }

    def process_file(self, filename): #processes the file
        try:
            parts = filename.lower().split('_')
            country = parts[0] #extract name information from the filename to find respective directory
            city = parts[1].lower().replace(' ', '-') #lowercases it, replaces spaces with dashes(-)
            hotel_name = parts[2].lower().replace(' ', '-')
            
            if country in ["usa", "uk"]: #check for countries with states so they can skip over states and only grab city
                if city not in ["new-york-city", "san-francisco"]:
                    city = parts[2].lower().replace(' ', '-') 
            
            hotel_dir = os.path.join("data", city) #find the directory with the hotel files
            if not os.path.exists(hotel_dir): #check if directory exists
                print(f"Error: Hotel directory '{hotel_dir}' not found.")
                return
            
            input_file = filename #find the input file
            if not input_file: #check if file exists
                print(f"Error: No .txt file found in '{hotel_dir}'.")
                return
            
            output_file = f"{filename}_processed.csv" #create output file name

            with open(os.path.join(hotel_dir, input_file), 'r') as file_in:
                with open(output_file, 'w', encoding='utf-8') as file_out:
                    writer = csv.writer(file_out)
                    writer.writerow(["index", "breakfast", "cleanliness", "price", "service", "location", "overall_sentiment", "review"]) #lists the titles in csv
                    
                    for line in file_in: #for each line, process and write in csv according to the titles above
                        processed_line = self.remove_stopwords_and_lemmatize(line) #not used in analysis since I want to test context and removing stopwords eliminates context
                        analysis = self.categorize_review(line)
    
                        row = [
                            analysis['index'],
                            f"breakfast:{(analysis['categories']).get('breakfast', '')}★",#combines all the 1's and -1's in the categorized_words list from categorize_review to sum up and find a number between 0-5, putting that amount of stars on the category
                            f"cleanliness:{(analysis['categories']).get('cleanliness', '')}★",#flowering up 1 and -1 by converting them into stars, representing the star count for hotels
                            f"price:{(analysis['categories']).get('price', '')}★",
                            f"service:{(analysis['categories']).get('service', '')}★",
                            f"location:{(analysis['categories']).get('location', '')}★",
                            analysis['sentiment_paragraph'],
                            analysis['review_text'].replace(',', '')#strips commas from the final text to maintain csv integrity
                        ]
                        writer.writerow(row)
                        self.index += 1
            
            processed_dir = os.path.join(os.getcwd(), "processed_data") #creates a 'processed_data' directory in case it doesn't exist
            os.makedirs(processed_dir, exist_ok=True)
            new_output_file = os.path.join(processed_dir, city, output_file)
            shutil.move(output_file, new_output_file) #moveds output to 'processed_data' folder
            
            print(f"Processing completed successfully for {hotel_name}")
        except Exception as e: #error catching
            print(f"An error occurred: {str(e)}")
        self.index = 1

    def search_processed_hotel(self, filename): #finds existing processed files
        try:
            if filename.endswith('_processed.csv'): #targetting something like this: _processed.csv
                filename = filename.replace("_processed.csv", "")

            parts = filename.lower().split('_')
            country = parts[0] #extract name information from the filename to find respective directory
            city = parts[1].lower().replace(' ', '-')
            
            if country in ["usa", "uk"]: #check for countries with states so they can skip over states and only grab city
                if city not in ["new-york-city", "san-francisco"]:
                    city = parts[2].lower().replace(' ', '-') #check for countries with states so they can skip over states and only grab city

            processed_file_path = os.path.join("processed_data", city, f"{filename}_processed.csv") #construct full path for simplicity
            if os.path.exists(processed_file_path): #check if exists, runs processing if it doesn't exist
                print(f'Processed file found in {processed_file_path}')
                self.file_processed = True #sets this to true so gui can check for this
            else:
                print(f"No processed file found for {filename}. Processing...")
                self.process_file(filename) #processes file if doesn't exist
                self.file_processed = False #sets this to false so gui can check for this

        except Exception as e:
            print(f"An error occurred while searching for processed hotel: {str(e)}")
            self.file_processed = False

    def display_stopwords_and_lemmatize(self, filename): #DEPRECATED: displays stopwords and lemmatization for assignment
        with open(filename, 'r') as file:
            text = file.read()

        sentences = nltk.sent_tokenize(text) #tokenizes text into sentences
        random_sentence = random.choice(sentences)#select a random sentence to display functionality on small scale

        filtered_tokens = [word.lower() for word in nltk.word_tokenize(random_sentence) if word.lower() not in stop_words]
        lemmatized_tokens = [lemmatizer.lemmatize(word) for word in filtered_tokens]

        print(f"\nOriginal Review:\n{random_sentence}")

        print("\nStopwords Removed:")
        print(" ".join(filtered_tokens))

        print("\nLemmatized Words:")
        print(" ".join(lemmatized_tokens))

    def analyze_document_sentiment(analyzer, filename): #finds the total amount of reviews and average ratings for each hotel and displays them as an overall sentiment per hotel
        try:
            total_positive = 0 #for document sentiment review
            total_negative = 0
            total_reviews = 0

            if filename.endswith('_processed.csv'): #targetting something like this: _processed.csv
                filename = filename.replace("_processed.csv", "")

            parts = filename.lower().split('_')
            country = parts[0] #extract name information from the filename to find respective directory
            city = parts[1].lower().replace(' ', '-')
            
            if country in ["usa", "uk"]: #check for countries with states so they can skip over states and only grab city
                if city not in ["new-york-city", "san-francisco"]:
                    city = parts[2].lower().replace(' ', '-') #check for countries with states so they can skip over states and only grab city

            processed_file_path = os.path.join("processed_data", city, f"{filename}_processed.csv") #construct full path for simplicity
            if os.path.exists(processed_file_path):  #check if exists, runs processing if it doesn't exist
                print(f'Processed file found in {processed_file_path}')
                analyzer.file_processed = True #sets this to true so gui can check for this
            else:
                print(f"No processed file found for {filename}. Processing...")
                analyzer.process_file(filename) #processes file if doesn't exist
                analyzer.file_processed = False #sets this to false so gui can check for this

            with open(processed_file_path, 'r', encoding='utf-8') as file_in: #finds the processed file in it's respective city folder (i.e. "processed_data\beijing\china_beijing_aloft_beijing_haidian_processed.csv")
                df = pd.read_csv(file_in)#access columns from csv using pandas
                if df.columns[0] == 'Unnamed: 0': #skip header
                    df = df.iloc[1:]

                total_reviews = df.shape[0]
                total_positive = df[df['overall_sentiment'] >= 1].shape[0] #count positive and negative by counting how many is present in a column with that value
                total_neutral = df[df['overall_sentiment'] == 0].shape[0]
                total_negative = abs(df[df['overall_sentiment'] <= -1].shape[0])
            
                if total_positive > total_negative: #overall sentiment of the document ('positive', 'negative', or 'neutral').
                    document_sentiment =  "positive"
                elif total_negative > total_positive:
                    document_sentiment =  "negative"
                else:
                    document_sentiment =  "neutral"

                categories = ["breakfast", "cleanliness", "price", "service", "location"] #lists the categories for counting
                average_ratings = {}

                for category in categories: #counts for the total stars of every category and averages them for a document level analysis
                    ratings = df[category].str.replace(f'{category}:', '') #remove string to just have number
                    ratings = ratings.str.replace('★', '').astype(int)
                    
                    total_positive_star_ratings = ratings.sum()
                    
                    if total_reviews > 0:
                        avg_rating = round(total_positive_star_ratings / total_reviews) #finds the average (rounded up) of all ratings per category
                        average_ratings[category] = f"{avg_rating}★"
                    else:
                        average_ratings[category] = "0★"


            print(f"\nThe overall sentiment of the document is {document_sentiment}.")#print statement that contains all the information needed to display at the end
            print(f"Positive reviews: {total_positive}")
            print(f"Neutral reviews: {total_neutral}")
            print(f"Negative reviews: {total_negative}")
            print(f"Total reviews analyzed: {total_reviews}")
            print(average_ratings)

            return {
                "positive_reviews": total_positive,
                "negative_reviews": total_negative,
                "total_reviews": total_reviews,
                "average_ratings": average_ratings
            }

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            analyzer.file_processed = False
            return None

if __name__ == "__main__": #this is strictly backend stuff without gui
    analyzer = ReviewAnalyzer()
    hotel_name = input("Enter the hotel name (e.g., china_beijing_aloft_beijing_haidian): ") #take in input
    #analyzer.search_processed_hotel(hotel_name) #searches if file exists as processed data. if it does not, processes and lists information in a csv file
    #analyzer.analyze_document_sentiment(hotel_name) #prints document sentiment
    
    #DEPRECATED: analyzer.display_stopwords_and_lemmatize(os.path.join("data", hotel_name.lower().replace(' ', '_'), f"{hotel_name.lower().replace(' ', '_')}.txt")) #uses same logic as remove_stopwords_and_lemmatize to display results on small scale

__all__ = ['ReviewAnalyzer'] #uncomment this line to turn main.py into a module