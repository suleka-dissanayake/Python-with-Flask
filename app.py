from nltk.sentiment import SentimentIntensityAnalyzer
import nltk

nltk.download('vader_lexicon')

text = """that was really bad news!!!"""

sia = SentimentIntensityAnalyzer()

sentiment_scores = sia.polarity_scores(text)

compound_score = sentiment_scores['compound']

if compound_score >= 0.05:
    sentiment = 'Positive'
elif compound_score <= -0.05:
    sentiment = 'Negative'
else:
    sentiment = 'Neutral'


print(sentiment)