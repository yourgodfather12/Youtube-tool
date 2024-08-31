import os
import cv2
import threading
import logging
import yaml
import torch
from pyspark.sql import SparkSession
from dask import dataframe as dd

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def load_preprocessing_config(config_path="config/preprocessing.yaml"):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)


def preprocess_video(input_path, output_path, config):
    try:
        video = cv2.VideoCapture(input_path)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(output_path, fourcc, config['fps'], (config['width'], config['height']))

        while video.isOpened():
            ret, frame = video.read()
            if not ret:
                break

            if config['use_gpu']:
                frame = torch.tensor(frame).cuda()

            stabilized_frame = stabilize_frame(frame, config)
            noise_reduced_frame = reduce_noise(stabilized_frame, config)
            augmented_frame = augment_frame(noise_reduced_frame, config)
            resized_frame = cv2.resize(augmented_frame, (config['width'], config['height']))

            out.write(resized_frame)

        video.release()
        out.release()
        logging.info(f"Preprocessed {input_path} and saved to {output_path}")
    except Exception as e:
        logging.error(f"Error preprocessing video {input_path}: {e}", exc_info=True)


def stabilize_frame(frame, config):
    # AI-based stabilization (using a pre-trained model, if configured)
    if config['stabilize']:
        # Placeholder for stabilization logic
        pass
    return frame


def reduce_noise(frame, config):
    # AI-based noise reduction
    if config['reduce_noise']:
        # Placeholder for noise reduction logic
        pass
    return frame


def augment_frame(frame, config):
    # Apply data augmentation techniques
    if config['augment']:
        # Example: flipping, rotating, adding noise, etc.
        if config['flip']:
            frame = cv2.flip(frame, 1)
        if config['rotate']:
            frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        # Placeholder for additional augmentation logic
    return frame


def preprocess_data(input_dir, output_dir, config):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    threads = []
    for file_name in os.listdir(input_dir):
        if file_name.endswith('.mp4'):
            input_path = os.path.join(input_dir, file_name)
            output_path = os.path.join(output_dir, f"preprocessed_{file_name}")
            thread = threading.Thread(target=preprocess_video, args=(input_path, output_path, config))
            threads.append(thread)
            thread.start()

    for thread in threads:
        thread.join()


def distributed_preprocessing(input_dir, output_dir, config):
    spark = SparkSession.builder.appName("VideoPreprocessing").getOrCreate()
    video_files = os.listdir(input_dir)
    video_df = spark.createDataFrame(video_files, StringType())
    video_df = video_df.repartition(4)  # Distribute across 4 nodes

    def process_video_file(file_name):
        input_path = os.path.join(input_dir, file_name)
        output_path = os.path.join(output_dir, f"preprocessed_{file_name}")
        preprocess_video(input_path, output_path, config)

    video_df.foreach(process_video_file)
    spark.stop()


if __name__ == "__main__":
    config = load_preprocessing_config()
    distributed_preprocessing("input_videos", "output_videos", config)
