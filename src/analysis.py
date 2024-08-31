import cv2
import mediapipe as mp
import numpy as np
from deepface import DeepFace
import logging

def extract_video_metadata(video_path):
    try:
        video = cv2.VideoCapture(video_path)
        metadata = {
            "frame_count": int(video.get(cv2.CAP_PROP_FRAME_COUNT)),
            "frame_rate": video.get(cv2.CAP_PROP_FPS),
            "duration": int(video.get(cv2.CAP_PROP_FRAME_COUNT)) / video.get(cv2.CAP_PROP_FPS),
            "resolution": (int(video.get(cv2.CAP_PROP_FRAME_WIDTH)), int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))),
            "bitrate": int(video.get(cv2.CAP_PROP_BITRATE)) if video.get(cv2.CAP_PROP_BITRATE) != 0 else None,
            "codec": video.get(cv2.CAP_PROP_FOURCC)
        }
        video.release()
        return metadata
    except Exception as e:
        logging.error(f"Error extracting video metadata: {e}", exc_info=True)
        return {}

def analyze_structural_elements(video_path):
    try:
        video = cv2.VideoCapture(video_path)
        mp_face_detection = mp.solutions.face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5)
        mp_objectron = mp.solutions.objectron.Objectron(static_image_mode=False, max_num_objects=5, min_detection_confidence=0.5, model_name='Cup')
        frames = []
        while video.isOpened():
            ret, frame = video.read()
            if not ret:
                break
            results = mp_face_detection.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            object_results = mp_objectron.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            frames.append({
                "frame": frame,
                "face_detections": results.detections if results.detections else [],
                "object_detections": object_results.detected_objects if object_results.detected_objects else [],
                "frame_id": video.get(cv2.CAP_PROP_POS_FRAMES)
            })
        video.release()
        return frames
    except Exception as e:
        logging.error(f"Error analyzing structural elements: {e}", exc_info=True)
        return []

def detect_scene_changes(video_path):
    try:
        video = cv2.VideoCapture(video_path)
        previous_frame = None
        scene_changes = []
        frame_id = 0
        optical_flow = cv2.DISOpticalFlow_create(cv2.OPTFLOW_FARNEBACK_GAUSSIAN)

        while video.isOpened():
            ret, frame = video.read()
            if not ret:
                break
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if previous_frame is not None:
                flow = optical_flow.calc(previous_frame, gray_frame, None)
                mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1])
                if np.mean(mag) > 0.5:
                    scene_changes.append(frame_id)
            previous_frame = gray_frame
            frame_id += 1

        video.release()
        return scene_changes
    except Exception as e:
        logging.error(f"Error detecting scene changes: {e}", exc_info=True)
        return []

def perform_face_recognition(video_path):
    try:
        video = cv2.VideoCapture(video_path)
        faces = []
        while video.isOpened():
            ret, frame = video.read()
            if not ret:
                break
            face_analysis = DeepFace.analyze(frame, actions=['age', 'gender', 'emotion'])
            faces.append(face_analysis)
        video.release()
        return faces
    except Exception as e:
        logging.error(f"Error performing face recognition: {e}", exc_info=True)
        return []

def generate_formula(channel_name):
    try:
        formula = {
            "channel_name": channel_name,
            "video_style": {
                "pacing": "medium",
                "transitions": ["fade", "cut"],
                "color_scheme": "bright and vibrant",
                "narrative_style": "story-driven with B-roll"
            },
            "common_elements": ["intro logo", "outro card", "background music"],
            "detected_faces": perform_face_recognition("sample_video.mp4")
        }
        return formula
    except Exception as e:
        logging.error(f"Error generating formula: {e}", exc_info=True)
        return {}
