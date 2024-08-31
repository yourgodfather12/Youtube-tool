from transformers import GPT2LMHeadModel, AutoModel, AutoTokenizer
import logging
import os
import hashlib
from concurrent.futures import ThreadPoolExecutor
from mlflow import log_model, set_tracking_uri, register_model

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def calculate_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def validate_model(model_name, expected_hash):
    model_path = f"./models/{model_name}/pytorch_model.bin"
    if not os.path.exists(model_path):
        logging.error(f"Model {model_name} not found at {model_path}.")
        return False

    model_hash = calculate_md5(model_path)
    if model_hash != expected_hash:
        logging.error(f"Model hash mismatch: expected {expected_hash}, got {model_hash}.")
        return False

    logging.info(f"Model {model_name} validated successfully.")
    return True


def download_model(model_name="gpt2"):
    try:
        logging.info(f"Downloading {model_name} model...")

        if model_name == "gpt2":
            model = GPT2LMHeadModel.from_pretrained("gpt2")
        else:
            model = AutoModel.from_pretrained(model_name)
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            tokenizer.save_pretrained(f"./models/{model_name}/")

        model.save_pretrained(f"./models/{model_name}/")
        logging.info(f"Model {model_name} downloaded and saved.")

        # Validate the downloaded model
        expected_hash = "expected_md5_hash_here"  # Replace with actual hash
        validate_model(model_name, expected_hash)

        # Log and register the model with MLflow
        log_model(model, model_name, registered_model_name=model_name)
        logging.info(f"Model {model_name} registered with MLflow.")
    except Exception as e:
        logging.error(f"Failed to download model {model_name}: {e}", exc_info=True)


def download_multiple_models(model_names):
    with ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(download_model, model_names)


def deploy_model_as_api(model_name):
    try:
        logging.info(f"Deploying {model_name} model as REST API...")
        # Example using TensorFlow Serving or TorchServe
        subprocess.run(["torchserve", "--start", "--ncs", "--model-store", f"./models/{model_name}/"])
        logging.info(f"Model {model_name} deployed as REST API.")
    except Exception as e:
        logging.error(f"Failed to deploy model {model_name} as API: {e}", exc_info=True)


if __name__ == "__main__":
    set_tracking_uri("http://localhost:5000")  # Example MLflow server URI
    download_multiple_models(["gpt2", "bert-base-uncased"])
    deploy_model_as_api("gpt2")
