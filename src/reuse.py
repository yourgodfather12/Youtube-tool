import os
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import logging


def manage_asset_library(asset_dir):
    try:
        if not os.path.exists(asset_dir):
            os.makedirs(asset_dir)

        assets = [f for f in os.listdir(asset_dir) if os.path.isfile(os.path.join(asset_dir, f))]
        for asset in assets:
            asset_metadata = {
                "file_name": asset,
                "tags": generate_tags_for_asset(asset),
                "used_in": []
            }
            with open(os.path.join(asset_dir, f"{os.path.splitext(asset)[0]}_metadata.json"), 'w') as metadata_file:
                json.dump(asset_metadata, metadata_file)
        logging.info(f"Asset library in {asset_dir} managed successfully.")
    except Exception as e:
        logging.error(f"Error managing asset library: {e}", exc_info=True)


def generate_tags_for_asset(asset):
    try:
        vectorizer = TfidfVectorizer(max_features=5)
        X = vectorizer.fit_transform([asset])
        kmeans = KMeans(n_clusters=1)
        kmeans.fit(X)
        tags = vectorizer.get_feature_names_out()
        return tags
    except Exception as e:
        logging.error(f"Error generating tags for asset: {e}", exc_info=True)
        return []
