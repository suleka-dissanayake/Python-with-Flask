from flask import Flask, render_template, request, redirect, url_for
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
import requests
from bs4 import BeautifulSoup

# Ensure VADER lexicon is downloaded
nltk.download('vader_lexicon')

# Initialize VADER Sentiment Analyzer
sia = SentimentIntensityAnalyzer()

# Initialize Flask app
app = Flask(__name__)

# Function to classify sentiment based on VADER compound score
def classify_sentiment(review):
    score = sia.polarity_scores(review)
    compound_score = score['compound']
    if compound_score >= 0.2:
        return 'Positive'
    elif compound_score <= -0.2:
        return 'Negative'
    else:
        return 'Neutral'

# Function to extract eBay reviews
def extract_ebay_reviews(item_url):
    try:
        response = requests.get(item_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        review_sections = soup.find_all('div', class_='ebay-review-section')
        extracted_reviews = []

        for review in review_sections:
            title = review.find('h3', itemprop='name').get_text(strip=True) if review.find('h3', itemprop='name') else 'No title'
            body = review.find('p', itemprop='reviewBody').get_text(strip=True) if review.find('p', itemprop='reviewBody') else 'No content'
            extracted_reviews.append({
                'title': title,
                'body': body
            })

        return extracted_reviews

    except requests.exceptions.RequestException as e:
        print(f"Error fetching reviews: {e}")
        return []

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        review = request.form['review']
        sentiment = classify_sentiment(review)

        if sentiment == 'Positive':
            image = 'Positive.png'
        elif sentiment == 'Negative':
            image = 'Negative.png'
        else:
            image = 'Neutral.png'

        return render_template('index.html', review=review, sentiment=sentiment, image=image)

    return render_template('index.html', review=None, sentiment=None, image=None)

@app.route('/bulk', methods=['GET', 'POST'])
def bulk():
    if request.method == 'POST':
        item_url = request.form['url']
        reviews = extract_ebay_reviews(item_url)
        review_sentiments = []

        for review in reviews:
            sentiment = classify_sentiment(review['body'])
            review_sentiments.append({
                'title': review['title'],
                'body': review['body'],
                'sentiment': sentiment
            })

        # Calculate the average sentiment
        positive_count = sum(1 for r in review_sentiments if r['sentiment'] == 'Positive')
        negative_count = sum(1 for r in review_sentiments if r['sentiment'] == 'Negative')
        neutral_count = sum(1 for r in review_sentiments if r['sentiment'] == 'Neutral')
        total = len(review_sentiments)

        avg_sentiment = {
            'Positive': positive_count / total if total > 0 else 0,
            'Negative': negative_count / total if total > 0 else 0,
            'Neutral': neutral_count / total if total > 0 else 0
        }

        return render_template('bulk.html', reviews=review_sentiments, avg_sentiment=avg_sentiment)

    return render_template('bulk.html', reviews=None)

if __name__ == '__main__':
    app.run(debug=True)
