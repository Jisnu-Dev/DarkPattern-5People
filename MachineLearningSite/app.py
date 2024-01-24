import numpy as np
import pandas as pd
from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import requests
import joblib
import nltk
from nltk.corpus import stopwords
import string

nltk.download('wordnet')

# Scraper
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OPR/106.0.0.0'
}

def clean_review_text(review_text):
    return review_text.replace('READ MORE', '')

def get_flipkart_reviews(product_link):
    try:
        all_reviews = []

        page = 1

        while True:
            # Construct the URL for the current page
            page_url = f"{product_link}&page={page}"

            # Get reviews from the current page
            res = requests.get(page_url, headers=headers)
            soup = BeautifulSoup(res.text, 'html.parser')

            review_elements = soup.find_all("div", class_='t-ZTKy')
            for review_element in review_elements:
                review_text = review_element.text.strip()
                cleaned_review = clean_review_text(review_text)
                all_reviews.append(cleaned_review)

            # Check for the presence of the "Next" button
            next_button = soup.find("a", class_='_1LKTO3')

            if not next_button:
                # No more pages, exit the loop
                break

            # Move to the next page
            page += 1

        return all_reviews

    except Exception as e:
        print(f"Error: {e}")
        print("Failed to fetch reviews.")
        return None

# Model loading

# Moved text_process to the global level
def text_process(review):
    nopunc = [char for char in review if char not in string.punctuation]
    nopunc = ''.join(nopunc)
    return [word for word in nopunc.split() if word.lower() not in stopwords.words('english')]

svm_model = joblib.load('D:/FakeReviews/Py/svm_model.joblib')

def predict_review_type(review, model):
    cleaned_review = ' '.join(text_process(review))
    prediction = model.predict([cleaned_review])
    return 'CG' if prediction[0] == 'CG' else 'OR'

# Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    if request.method == 'POST':
        product_link = request.form['product_link']
        flipkart_reviews = get_flipkart_reviews(product_link)

        if flipkart_reviews:
            # Create additional columns
            numbers = list(range(len(flipkart_reviews)))
            categories = ['Electronics_5'] * len(flipkart_reviews)

            # Extract ratings from the reviews
            ratings = []
            for review in flipkart_reviews:
                soup = BeautifulSoup(review, 'html.parser')
                rating_element = soup.find("div", class_='_3LWZlK _1BLPMq')
                rating = rating_element.text.strip() if rating_element else '5'
                ratings.append(rating)

            # Fill other columns
            labels = ['OR'] * len(flipkart_reviews)
            text_column = flipkart_reviews

            # Create DataFrame
            df = pd.DataFrame({
                '': numbers,
                'category': categories,
                'rating': ratings,
                'labels': labels,
                'text_': text_column
            })

            new_df = df.copy()
            new_df['Predicted_Label'] = new_df['text_'].apply(lambda x: predict_review_type(x, svm_model))

            result = new_df[['text_', 'Predicted_Label']].to_html(classes='table table-striped')

            return render_template('result.html', result=result)
        else:
            return render_template('no_reviews.html')

if __name__ == '__main__':
    app.run(port=4000)  # You can change the port as needed

