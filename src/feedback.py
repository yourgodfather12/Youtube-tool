import json
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import logging

def log_feedback(user_feedback):
    try:
        sentiment = TextBlob(user_feedback).sentiment
        feedback_entry = {
            "feedback": user_feedback,
            "sentiment": {
                "polarity": sentiment.polarity,
                "subjectivity": sentiment.subjectivity
            }
        }
        categorize_feedback(user_feedback)
        with open("feedback_log.txt", "a") as log_file:
            log_file.write(json.dumps(feedback_entry) + "\n")
        logging.info("Feedback logged with sentiment analysis.")
    except Exception as e:
        logging.error(f"Error logging feedback: {e}", exc_info=True)

def categorize_feedback(feedback):
    try:
        vectorizer = TfidfVectorizer(max_features=100)
        X = vectorizer.fit_transform([feedback])
        kmeans = KMeans(n_clusters=3)
        kmeans.fit(X)
        category = kmeans.predict(X)
        logging.info(f"Feedback categorized into cluster: {category[0]}")
    except Exception as e:
        logging.error(f"Error categorizing feedback: {e}", exc_info=True)
