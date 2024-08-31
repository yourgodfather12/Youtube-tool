import logging
import os
from .analysis import extract_video_metadata, analyze_structural_elements, detect_scene_changes, generate_formula
from .generation import generate_script, smart_clip_video, auto_generate_video, dynamic_music_generation
from .postproduction import apply_color_correction, apply_audio_enhancement, add_transitions_to_video
from .cloud import upload_to_s3
from .interactive import add_interactive_elements
from .optimization import optimize_seo, generate_teasers
from .reuse import manage_asset_library
from .auth import authenticate_user
from .utils import load_yaml

# Configure logging with more detailed logging levels and output to file
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler("tool_log.log"), logging.StreamHandler()])

# Load configuration settings
config = load_yaml('config/config.yaml')

def main():
    try:
        # User Authentication
        if not authenticate_user(config['user_credentials']):
            logging.error("Authentication failed. Exiting.")
            return

        video_path = "sample_video.mp4"
        logging.info("Starting video metadata extraction.")
        metadata = extract_video_metadata(video_path)
        logging.info(f"Metadata extracted: {metadata}")

        logging.info("Starting structural element analysis.")
        frames = analyze_structural_elements(video_path)
        logging.debug(f"Number of frames analyzed: {len(frames)}")

        logging.info("Detecting scene changes.")
        scenes = detect_scene_changes(video_path)
        logging.debug(f"Number of scene changes detected: {len(scenes)}")

        logging.info("Generating channel formula.")
        formula = generate_formula("My YouTube Channel")
        logging.debug(f"Generated formula: {formula}")

        logging.info("Generating script.")
        script = generate_script("Introduction to AI in video editing", include_sources=True)
        logging.debug(f"Generated script: {script}")

        logging.info("Creating smart clip.")
        smart_clip_video(video_path, 10, 20, "clipped_video.mp4", format="mp4")
        logging.info("Smart clip created.")

        logging.info("Applying color correction.")
        apply_color_correction("clipped_video.mp4", "final_video.mp4")
        logging.info("Color correction applied.")

        logging.info("Enhancing audio.")
        apply_audio_enhancement("final_video.mp4", "enhanced_audio_video.mp4")
        logging.info("Audio enhancement applied.")

        logging.info("Adding transitions.")
        add_transitions_to_video(["final_video.mp4"], "transitions_applied.mp4", transition_type="crossfade", duration=1.0)
        logging.info("Transitions applied.")

        logging.info("Auto-generating video.")
        auto_generate_video("Introduction to AI", ["Introduction", "AI Basics", "Advanced AI Techniques"], "auto_generated_video.mp4", background_music_path="background_music.mp3")
        logging.info("Auto-generated video created.")

        logging.info("Generating dynamic music track.")
        dynamic_music_generation("auto_generated_video.mp4", "music_track.mp3")
        logging.info("Dynamic music track generated.")

        logging.info("Adding interactive elements.")
        add_interactive_elements("auto_generated_video.mp4", "interactive_video.mp4")
        logging.info("Interactive elements added.")

        logging.info("Uploading video to S3.")
        upload_to_s3("interactive_video.mp4", "my-video-bucket", "interactive_video.mp4", region_name=config['aws_region'])
        logging.info("Uploaded video to S3.")

        logging.info("Optimizing SEO for video.")
        optimize_seo("interactive_video.mp4", "Optimized Title", "Description", ["tag1", "tag2"])
        logging.info("SEO optimized.")

        logging.info("Generating social media teaser.")
        generate_teasers("interactive_video.mp4", "teaser_video.mp4")
        logging.info("Social media teaser generated.")

        logging.info("Managing asset library.")
        manage_asset_library("assets/")
        logging.info("Asset library managed.")

    except Exception as e:
        logging.error(f"An error occurred: {e}", exc_info=True)

if __name__ == "__main__":
    main()
