import moviepy.editor as mp
import numpy as np
import logging

def apply_color_correction(input_video_path, output_video_path):
    try:
        video = mp.VideoFileClip(input_video_path)
        corrected_video = video.fx(mp.vfx.colorx, 1.3)
        corrected_video = corrected_video.fx(mp.vfx.lum_contrast, 0, 1.5, 128)
        corrected_video = corrected_video.fx(mp.vfx.gamma_corr, 1.2)
        corrected_video = corrected_video.fx(mp.vfx.blackwhite, 0.5)
        corrected_video.write_videofile(output_video_path, codec="libx264")
    except Exception as e:
        logging.error(f"Error applying color correction: {e}", exc_info=True)

def apply_audio_enhancement(input_video_path, output_video_path):
    try:
        video = mp.VideoFileClip(input_video_path)
        audio = video.audio.fx(mp.audio.fx.all.audio_normalize)
        audio = audio.volumex(1.2)
        audio = audio.fx(mp.audio.fx.all.audio_low_pass_filter, frequency=1000)
        final_video = video.set_audio(audio)
        final_video.write_videofile(output_video_path, codec="libx264")
    except Exception as e:
        logging.error(f"Error enhancing audio: {e}", exc_info=True)

def add_transitions_to_video(video_clips, output_path, transition_type="crossfade", duration=1.0):
    try:
        if transition_type == "crossfade":
            final_clip = mp.concatenate_videoclips(video_clips, method="compose", transition=mp.transitions.crossfadein(duration))
        elif transition_type == "slide":
            final_clip = mp.concatenate_videoclips(video_clips, method="compose", transition=mp.transitions.slide(duration))
        else:
            final_clip = mp.concatenate_videoclips(video_clips)

        final_clip.write_videofile(output_path, codec="libx264")
    except Exception as e:
        logging.error(f"Error adding transitions: {e}", exc_info=True)
