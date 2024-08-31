from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import moviepy.editor as mp
import logging

def optimize_seo(video_path, title, description, tags):
    try:
        vectorizer = TfidfVectorizer(max_features=100)
        model = LogisticRegression()
        X_train = vectorizer.fit_transform([title, description])
        y_train = tags
        model.fit(X_train, y_train)

        X_new = vectorizer.transform([title, description])
        predicted_tags = model.predict(X_new)

        logging.info(f"Optimized SEO for {video_path}: Predicted tags - {predicted_tags}")
    except Exception as e:
        logging.error(f"Error optimizing SEO: {e}", exc_info=True)

def generate_teasers(input_video_path, teaser_output_path, platforms=["twitter", "instagram"]):
    try:
        video = mp.VideoFileClip(input_video_path)
        teaser = video.subclip(0, 10)

        for platform in platforms:
            teaser_path = f"{teaser_output_path}_{platform}.mp4"
            teaser.write_videofile(teaser_path, codec="libx264")
            logging.info(f"Generated teaser for {platform}: {teaser_path}")

            generate_social_media_post(platform, teaser_path)
    except Exception as e:
        logging.error(f"Error generating teasers: {e}", exc_info=True)

def generate_social_media_post(platform, video_path):
    try:
        logging.info(f"Posting {video_path} to {platform}...")
        # Example: call Twitter API to post the video
    except Exception as e:
        logging.error(f"Error posting to social media: {e}", exc_info=True)
