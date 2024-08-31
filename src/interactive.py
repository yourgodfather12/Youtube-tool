import moviepy.editor as mp
import os
import logging

def add_interactive_elements(input_video_path, output_video_path):
    try:
        video = mp.VideoFileClip(input_video_path)
        html_overlay_path = "interactive_overlay.html"
        generate_html_overlay(html_overlay_path)

        overlay = mp.ImageClip(html_overlay_path).set_duration(video.duration)
        final_video = mp.CompositeVideoClip([video, overlay])

        final_video.write_videofile(output_video_path, codec="libx264")
        logging.info("Interactive elements added successfully.")
    except Exception as e:
        logging.error(f"Error adding interactive elements: {e}", exc_info=True)

def generate_html_overlay(file_path):
    try:
        with open(file_path, 'w') as file:
            file.write("""
            <html>
            <body>
                <div style="position: absolute; top: 10%; left: 10%;">
                    <button onclick="alert('Clicked!')">Click Me!</button>
                    <form>
                        <label for="name">Name:</label><br>
                        <input type="text" id="name" name="name"><br>
                        <input type="submit" value="Submit">
                    </form>
                </div>
            </body>
            </html>
            """)
        logging.info(f"HTML overlay generated at {file_path}.")
    except Exception as e:
        logging.error(f"Error generating HTML overlay: {e}", exc_info=True)
