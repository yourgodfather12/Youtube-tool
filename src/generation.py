from transformers import GPT2LMHeadModel, GPT2Tokenizer
import cv2
import moviepy.editor as mp
import os
from newspaper import Article
import logging

def generate_script(prompt, include_sources=False):
    try:
        model_name = "gpt2"
        model = GPT2LMHeadModel.from_pretrained(model_name)
        tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        inputs = tokenizer.encode(prompt, return_tensors="pt")
        outputs = model.generate(inputs, max_length=1000, num_return_sequences=1, temperature=0.7)
        script = tokenizer.decode(outputs[0], skip_special_tokens=True)

        if include_sources:
            sources = fetch_relevant_articles(prompt)
            script += f"\n\nSources:\n{sources}"

        return script
    except Exception as e:
        logging.error(f"Error generating script: {e}", exc_info=True)
        return ""

def fetch_relevant_articles(topic):
    try:
        article = Article(f'https://www.google.com/search?q={topic.replace(" ", "+")}&tbm=nws')
        article.download()
        article.parse()
        return f"- {article.title}: {article.url}"
    except Exception as e:
        logging.error(f"Error fetching articles: {e}", exc_info=True)
        return "No sources available."

def smart_clip_video(video_path, start_time, end_time, output_path, format="mp4"):
    try:
        video = cv2.VideoCapture(video_path)
        fps = video.get(cv2.CAP_PROP_FPS)
        start_frame = int(start_time * fps)
        end_frame = int(end_time * fps)

        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        if format == "mp4":
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (int(video.get(3)), int(video.get(4))))

        current_frame = 0
        while video.isOpened():
            ret, frame = video.read()
            if not ret or current_frame > end_frame:
                break
            if start_frame <= current_frame <= end_frame:
                out.write(frame)
            current_frame += 1

        video.release()
        out.release()
    except Exception as e:
        logging.error(f"Error clipping video: {e}", exc_info=True)

def auto_generate_video(title, sections, output_path, background_music_path=None):
    try:
        clips = []
        for section in sections:
            script = generate_script(f"{section} for a video titled {title}", include_sources=True)
            logging.info(f"Generated Script for {section}: {script}")

            clip = mp.TextClip(script, fontsize=70, color='white', size=(1920, 1080))
            clip = clip.set_duration(5)
            clips.append(clip)

        final_clip = mp.concatenate_videoclips(clips)

        if background_music_path:
            music = mp.AudioFileClip(background_music_path)
            final_clip = final_clip.set_audio(music)

        final_clip.write_videofile(output_path, codec="libx264")
    except Exception as e:
        logging.error(f"Error generating video: {e}", exc_info=True)

def dynamic_music_generation(video_path, music_output_path):
    try:
        logging.info(f"Generating dynamic music for {video_path}...")
        os.system(f"cp example_music.mp3 {music_output_path}")
    except Exception as e:
        logging.error(f"Error generating dynamic music: {e}", exc_info=True)
