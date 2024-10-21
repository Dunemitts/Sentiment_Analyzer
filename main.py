import os #file navigation
import shutil #moving output to processed_data folder
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

from transformers import AutoTokenizer, AutoModelForSequenceClassification #transformers is used for ROBERTA
from scipy.special import softmax
import random

import csv #for document analysis
import pandas as pd

import random #for picking random sentences to show off display 

nltk.download(['punkt','punkt_tab','averaged_perceptron_tagger','maxent_ne_chunker','words','stopwords','wordnet','vader_lexicon']) #required corpora found online

stop_words = set(stopwords.words('english')) #you can actually print this to see the entire list
lemmatizer = WordNetLemmatizer()

class ReviewAnalyzer:
    def __init__(self):
        self.index = 1 #index counter for lines
        self.model_name = "cardiffnlp/twitter-roberta-base-sentiment" #uses pretrained ROBERTA model instead of VADER
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)

        self.total_positive = 0 #for document sentiment review
        self.total_negative = 0
        self.total_reviews = 0

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

    def categorize_review(self, review):
        categories = { #list of words that would be targettted to find the context around
            "breakfast": ["breakfast", "brunch", "lunch", "dining room"],
            "cleanliness": ["clean", "dirty", "filthy", "unclean", "spotless", "hygiene", "tidiness"],
            "price": ["cheap", "expensive", "affordable", "overpriced", "value", "cost", "bill"],
            "service": ["staff", "helpful", "rude", "friendly", "unfriendly", "attentive", "inattentive"],
            "location": ["near", "far", "central", "remote", "proximity"]
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
        return {
            "index": self.index,
            "categories": categorized_words,
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
                    writer.writerow(["index", "categories", "overall_sentiment", "review", "sentiment_annotations"]) #lists the titles in csv
                    
                    for line in file_in: #for each line, process and write in csv according to the titles above
                        processed_line = self.remove_stopwords_and_lemmatize(line) #not used in analysis since I want to test context and removing stopwords eliminates context
                        analysis = self.categorize_review(line)
                        
                        formatted_categories = []
                        for category, values in analysis['categories'].items():
                            star_count = sum(values)#combines all the 1's and -1's in the categorized_words list from categorize_review to sum up and find a number between 0-5, putting that amount of stars on the category
                            if star_count > 5:
                                star_count = 5
                            elif star_count < 0:
                                star_count = 0
                            formatted_categories.append(f"{category}:{star_count}★")#flowering up 1 and -1 by converting them into stars, representing the star count for hotels
                        
                        review_text_no_commas = analysis['review_text'].replace(',', '') #strips commas from the final text to maintain csv integrity
                        row = [
                            analysis['index'],
                            ' '.join(formatted_categories), #since this is a csv file, don't join with commas(, )
                            analysis['sentiment_paragraph'],
                            review_text_no_commas,
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

    def search_processed_hotel(self, filename):
        try:
            parts = filename.lower().split('_')
            country = parts[0] #extract name information from the filename to find respective directory
            city = parts[1].lower().replace(' ', '-')
            
            if country in ["usa", "uk"]: #check for countries with states so they can skip over states and only grab city
                city = parts[2].lower().replace(' ', '-')

            processed_file_path = os.path.join("processed_data", city, f"{filename}_processed.csv") #construct full path for simplicity
            if os.path.exists(processed_file_path) == False: #check if exists, runs processing if it doesn't exist
                    analyzer.process_file(filename) #processes and lists information in a csv file
            else:
                print(f'Processed file found in {processed_file_path}')

        except Exception as e:
            print(f"An error occurred while searching for processed hotel: {str(e)}")

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

    def analyze_document_sentiment(self, filename): #takes in the csv file as input
        try:
            parts = filename.lower().split('_')
            country = parts[0] #extract name information from the filename to find respective directory
            city = parts[1].lower().replace(' ', '-')
            
            if country in ["usa", "uk"]: #check for countries with states so they can skip over states and only grab city
                city = parts[2].lower().replace(' ', '-')

            processed_file_path = os.path.join("processed_data", city, f"{filename}_processed.csv") #construct full path for simplicity

            with open(processed_file_path, 'r', encoding='utf-8') as file_in: #finds the processed file in it's respective city folder (i.e. "processed_data\beijing\china_beijing_aloft_beijing_haidian_processed.csv")
                df = pd.read_csv(file_in, usecols=['overall_sentiment'])#access 'sentiment' column from csv using pandas
                if df.columns[0] == 'Unnamed: 0': #skip header
                    df = df.iloc[1:]
                
                total_positive = df[df['overall_sentiment'] >= 1].shape[0] #count positive and negative by counting how many is present in a column with that value
                total_neutral = df[df['overall_sentiment'] == 0].shape[0]
                total_negative = abs(df[df['overall_sentiment'] <= -1].shape[0])
                total_reviews = df.shape[0]
            
            positive_ratio = total_positive / total_reviews#calculate overall sentiment
            negative_ratio = total_negative / total_reviews
            if positive_ratio > negative_ratio: #overall sentiment of the document ('positive', 'negative', or 'neutral').
                document_sentiment =  "positive"
            elif negative_ratio > positive_ratio:
                document_sentiment =  "negative"
            else:
                document_sentiment =  "neutral"
            
            print(f"\nThe overall sentiment of the document is {document_sentiment}.")#print statement that contains all the information needed to display at the end
            print(f"Positive reviews: {total_positive}")
            print(f"Neutral reviews: {total_neutral}")
            print(f"Negative reviews: {total_negative}")
            print(f"Total reviews analyzed: {total_reviews}")

        except Exception as e:
            print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    analyzer = ReviewAnalyzer()
    hotel_name = input("Enter the hotel name (e.g., china_beijing_aloft_beijing_haidian): ") #take in input
    analyzer.search_processed_hotel(hotel_name) #searches if file exists as processed data. if it does not, processes and lists information in a csv file
    analyzer.analyze_document_sentiment(hotel_name) #prints document sentiment
    
    #DEPRECATED: analyzer.display_stopwords_and_lemmatize(os.path.join("data", hotel_name.lower().replace(' ', '_'), f"{hotel_name.lower().replace(' ', '_')}.txt")) #uses same logic as remove_stopwords_and_lemmatize to display results on small scale
