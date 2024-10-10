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
        pos_tenth = int(scores[2] * 10)
        if neg_tenth >= 1 or pos_tenth >= 1: #if either the negative value or positive value is high enough, they're considered over neutral (as neutral will always be dominant)
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
        roberta_sentiment = self.analyze_sentiment_roberta(' '.join(words))
        
        for i, word in enumerate(words):
            lower_word = word.lower()
            for category, keywords in categories.items():
                if any(lower_word in single_keyword for single_keyword in keywords):
                    context = ' '.join(words[max(0, i-3):min(i+3, len(words))])
                    sentiment = self.analyze_sentiment_roberta(context)
                    if sentiment == '1':
                        categorized_words.setdefault(category, []).append(1)#signifies positive review for this category, will be combined later for a 0-5 star rating
                    elif sentiment == '-1':
                        categorized_words.setdefault(category, []).append(-1)#signifies negative review for this category, will be combined later for a 0-5 star rating
        return {
            "index": self.index,
            "categories": categorized_words,
            "sentiment_roberta": roberta_sentiment,
            "review_text": review
        }
    
    def process_file(self, filename): #processes the file
        try:
            with open(filename, 'r') as file_in:
                with open('hotel_processed.csv', 'w', encoding='utf-8') as file_out:
                    writer = csv.writer(file_out)
                    writer.writerow(["index", "categories", "sentiment", "review"]) #lists the titles in csv
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
                        
                        review_text_no_commas = processed_line.replace(',', '') #strips commas from the final text to maintain csv integrity
                        row = [
                            analysis['index'],
                            ' '.join(formatted_categories), #since this is a csv file, don't join with commas(, )
                            analysis['sentiment_roberta'],
                            review_text_no_commas
                        ]
                        writer.writerow(row)
                        self.index += 1
        except Exception as e: #error catching
            print(f"An error occurred: {str(e)}")


    def display_stopwords_and_lemmatize(self, filename): #displays stopwords and lemmatization for assignment
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
            with open(filename, 'r') as file_in:
                df = pd.read_csv(file_in, usecols=['sentiment'])#access 'sentiment' column from csv using pandas
                if df.columns[0] == 'Unnamed: 0': #skip header
                    df = df.iloc[1:]
                
                total_positive = df[df['sentiment'] == 1].shape[0] #count positive and negative by counting how many is present in a column with that value
                total_negative = abs(df[df['sentiment'] == -1].shape[0])
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
            print(f"Negative reviews: {total_negative}")
            print(f"Total reviews analyzed: {total_reviews}")

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return None

if __name__ == "__main__":
    analyzer = ReviewAnalyzer()
    analyzer.process_file("hotel_testing.txt") #processes and lists information in a csv file
    analyzer.display_stopwords_and_lemmatize("uk_england_london_britannia_international_hotel.txt") #uses same logic as remove_stopwords_and_lemmatize to display results on small scale
    analyzer.analyze_document_sentiment("hotel_processed.csv") #prints document sentiment