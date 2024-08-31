import sys
import threading
import hashlib
import logging
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QStackedWidget,
    QHBoxLayout, QSlider, QLabel, QPushButton, QLineEdit, QTextEdit,
    QProgressBar, QSplitter, QSystemTrayIcon, QFileDialog, QStatusBar,
    QTabWidget, QMessageBox, QCheckBox, QComboBox
)
from PyQt6.QtCore import Qt, QUrl, QTimer, QSize, QSettings, pyqtSignal, QObject, QThread, pyqtSlot
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, vfx
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

# Setting up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class WorkerSignals(QObject):
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)

class DownloadWorker(QThread):
    signals = WorkerSignals()

    def __init__(self, url, download_path, quality):
        super().__init__()
        self.url = url
        self.download_path = download_path
        self.quality = quality
        self.file_path = ""

    def run(self):
        try:
            from pytube import YouTube  # Import here to avoid blocking the UI at the start
            yt = YouTube(self.url, on_progress_callback=self.progress_callback)
            stream = yt.streams.filter(res=self.quality, progressive=True, file_extension='mp4').first()
            self.file_path = stream.download(output_path=self.download_path)
            self.signals.finished.emit(True, "Download complete!")
        except Exception as e:
            logging.error(f"Error during download: {e}")
            self.signals.finished.emit(False, str(e))

    def progress_callback(self, stream, chunk, bytes_remaining):
        percent = int((stream.filesize - bytes_remaining) / stream.filesize * 100)
        self.signals.progress.emit(percent)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Advanced YouTube Video Tool")
        self.setGeometry(100, 100, 1200, 800)
        self.setWindowIcon(QIcon("gui/assets/icon.png"))

        self.settings = QSettings("MyCompany", "YouTubeVideoTool")
        self.init_ui()

    def init_ui(self):
        # Set up central widget and layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Responsive Splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        # Sidebar with modern icons
        sidebar = QWidget()
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        splitter.addWidget(sidebar)

        # Modern Navigation
        self.tab_widget = QTabWidget()
        splitter.addWidget(self.tab_widget)
        splitter.setStretchFactor(1, 5)

        # Initialize Pages
        self.download_page = self.create_download_page()
        self.play_page = self.create_play_page()
        self.process_page = self.create_process_page()
        self.analyze_page = self.create_analyze_page()
        self.generate_page = self.create_generate_page()
        self.settings_page = self.create_settings_page()

        # Add pages to tab widget
        self.tab_widget.addTab(self.download_page, QIcon("gui/assets/download.png"), "Download")
        self.tab_widget.addTab(self.play_page, QIcon("gui/assets/play.png"), "Play")
        self.tab_widget.addTab(self.process_page, QIcon("gui/assets/process.png"), "Process")
        self.tab_widget.addTab(self.analyze_page, QIcon("gui/assets/analyze.png"), "Analyze")
        self.tab_widget.addTab(self.generate_page, QIcon("gui/assets/generate.png"), "Generate")
        self.tab_widget.addTab(self.settings_page, QIcon("gui/assets/settings.png"), "Settings")

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Load saved theme
        self.load_style()

        # System tray icon
        self.init_tray_icon()

        # Media player
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        self.video_widget = QVideoWidget()
        self.media_player.setVideoOutput(self.video_widget)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_video_position)

    # Pages creation methods
    def create_download_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(QLabel("Enter Video URL:"))

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste the YouTube video URL here...")
        layout.addWidget(self.url_input)

        self.quality_select = QComboBox()
        self.quality_select.addItems(["720p", "1080p", "1440p", "2160p"])
        layout.addWidget(self.quality_select)

        download_button = QPushButton("Download Video")
        download_button.clicked.connect(self.download_video)
        layout.addWidget(download_button)

        self.download_status = QLabel("")
        layout.addWidget(self.download_status)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.watermark_input = QLineEdit()
        self.watermark_input.setPlaceholderText("Enter watermark text (optional)...")
        layout.addWidget(self.watermark_input)

        self.add_watermark_checkbox = QCheckBox("Add watermark to video")
        layout.addWidget(self.add_watermark_checkbox)

        layout.addStretch()
        return page

    def create_play_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(self.video_widget)

        control_layout = QHBoxLayout()

        play_button = QPushButton("Play")
        play_button.setToolTip("Play the selected video")
        play_button.clicked.connect(self.play_video)
        control_layout.addWidget(play_button)

        pause_button = QPushButton("Pause")
        pause_button.setToolTip("Pause the video")
        pause_button.clicked.connect(self.pause_video)
        control_layout.addWidget(pause_button)

        stop_button = QPushButton("Stop")
        stop_button.setToolTip("Stop the video")
        stop_button.clicked.connect(self.stop_video)
        control_layout.addWidget(stop_button)

        layout.addLayout(control_layout)

        self.video_slider = QSlider(Qt.Orientation.Horizontal)
        self.video_slider.setRange(0, 0)
        self.video_slider.sliderMoved.connect(self.set_video_position)
        layout.addWidget(self.video_slider)

        self.time_label = QLabel("00:00 / 00:00")
        layout.addWidget(self.time_label)

        layout.addStretch()
        return page

    def create_process_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        self.process_tabs = QTabWidget()
        layout.addWidget(self.process_tabs)

        self.trim_tab = self.create_trim_tab()
        self.filter_tab = self.create_filter_tab()
        self.audio_tab = self.create_audio_tab()
        self.subtitles_tab = self.create_subtitles_tab()

        self.process_tabs.addTab(self.trim_tab, "Trim")
        self.process_tabs.addTab(self.filter_tab, "Filter")
        self.process_tabs.addTab(self.audio_tab, "Audio")
        self.process_tabs.addTab(self.subtitles_tab, "Subtitles")

        layout.addStretch()
        return page

    def create_trim_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        layout.addWidget(QLabel("Trim Video"))

        self.trim_start_input = QLineEdit()
        self.trim_start_input.setPlaceholderText("Start time (in seconds)...")
        layout.addWidget(self.trim_start_input)

        self.trim_end_input = QLineEdit()
        self.trim_end_input.setPlaceholderText("End time (in seconds)...")
        layout.addWidget(self.trim_end_input)

        trim_button = QPushButton("Trim Video")
        trim_button.clicked.connect(self.trim_video)
        layout.addWidget(trim_button)

        self.process_text = QTextEdit()
        self.process_text.setPlaceholderText("Processing logs will be displayed here...")
        layout.addWidget(self.process_text)

        return tab

    def create_filter_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        layout.addWidget(QLabel("Apply Filter"))

        self.filter_select = QComboBox()
        self.filter_select.addItems(["Grayscale", "Negative", "Blur"])
        layout.addWidget(self.filter_select)

        filter_button = QPushButton("Apply Filter")
        filter_button.clicked.connect(self.apply_filter)
        layout.addWidget(filter_button)

        return tab

    def create_audio_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        layout.addWidget(QLabel("Adjust Audio"))

        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        layout.addWidget(self.volume_slider)

        mute_button = QPushButton("Mute Audio")
        mute_button.clicked.connect(lambda: self.adjust_audio(0))
        layout.addWidget(mute_button)

        return tab

    def create_subtitles_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        layout.addWidget(QLabel("Add Subtitles"))

        self.subtitle_input = QTextEdit()
        self.subtitle_input.setPlaceholderText("Enter subtitles here...")
        layout.addWidget(self.subtitle_input)

        subtitle_button = QPushButton("Add Subtitles")
        subtitle_button.clicked.connect(self.add_subtitles)
        layout.addWidget(subtitle_button)

        return tab

    def create_analyze_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        layout.addWidget(QLabel("Analyze Channel"))

        self.channel_input = QLineEdit()
        self.channel_input.setPlaceholderText("Enter YouTube Channel URL...")
        layout.addWidget(self.channel_input)

        analyze_button = QPushButton("Analyze")
        analyze_button.setToolTip("Analyze the YouTube channel for patterns")
        analyze_button.clicked.connect(self.analyze_channel)
        layout.addWidget(analyze_button)

        self.analysis_results = QTextEdit()
        self.analysis_results.setPlaceholderText("Results of the analysis will be displayed here...")
        layout.addWidget(self.analysis_results)

        layout.addStretch()
        return page

    def create_generate_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        layout.addWidget(QLabel("Generate Video"))

        self.script_input = QTextEdit()
        self.script_input.setPlaceholderText("Enter the script or content for the video...")
        layout.addWidget(self.script_input)

        generate_button = QPushButton("Generate Video")
        generate_button.setToolTip("Generate a video based on the provided script")
        generate_button.clicked.connect(self.generate_video)
        layout.addWidget(generate_button)

        layout.addStretch()
        return page

    def create_settings_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        layout.addWidget(QLabel("Theme:"))

        self.theme_toggle = QPushButton("Switch to Light Theme")
        self.theme_toggle.clicked.connect(self.toggle_theme)
        layout.addWidget(self.theme_toggle)

        layout.addStretch()
        return page

    # Style and Theme Management
    def load_style(self):
        theme = self.settings.value("theme", "dark")
        if theme == "light":
            self.setStyleSheet(open("gui/styles/light_theme.css").read())
            self.theme_toggle.setText("Switch to Dark Theme")
        else:
            self.setStyleSheet(open("gui/styles/styles.css").read())
            self.theme_toggle.setText("Switch to Light Theme")

    def toggle_theme(self):
        if self.theme_toggle.text() == "Switch to Light Theme":
            self.setStyleSheet(open("gui/styles/light_theme.css").read())
            self.theme_toggle.setText("Switch to Dark Theme")
            self.settings.setValue("theme", "light")
        else:
            self.setStyleSheet(open("gui/styles/styles.css").read())
            self.theme_toggle.setText("Switch to Light Theme")
            self.settings.setValue("theme", "dark")

    # System Tray Icon
    def init_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(QIcon("gui/assets/icon.png"), self)
        self.tray_icon.setToolTip("YouTube Video Tool Running")
        self.tray_icon.show()

    # Video Control Methods
    def set_video_position(self, position):
        self.media_player.setPosition(position)

    def update_video_position(self):
        position = self.media_player.position()
        duration = self.media_player.duration()

        self.video_slider.setRange(0, duration)
        self.video_slider.setValue(position)

        if duration > 0:
            current_time = self.format_time(position)
            total_time = self.format_time(duration)
            self.time_label.setText(f"{current_time} / {total_time}")

    def format_time(self, ms):
        seconds = (ms // 1000) % 60
        minutes = (ms // (1000 * 60)) % 60
        hours = (ms // (1000 * 60 * 60)) % 24
        if hours > 0:
            return f"{hours:02}:{minutes:02}:{seconds:02}"
        else:
            return f"{minutes:02}:{seconds:02}"

    def play_video(self):
        file_dialog = QFileDialog()
        last_dir = self.settings.value("last_video_dir", "")
        file_path, _ = file_dialog.getOpenFileName(self, "Open Video File", last_dir, "Video Files (*.mp4 *.avi *.mkv)")
        if file_path:
            video_url = QUrl.fromLocalFile(file_path)
            self.media_player.setSource(video_url)
            self.media_player.play()
            self.timer.start(1000)
            self.status_bar.showMessage("Playing video...")
            self.settings.setValue("last_video_dir", file_path.rsplit('/', 1)[0])

    def pause_video(self):
        self.media_player.pause()
        self.status_bar.showMessage("Video paused")

    def stop_video(self):
        self.media_player.stop()
        self.timer.stop()
        self.video_slider.setValue(0)
        self.time_label.setText("00:00 / 00:00")
        self.status_bar.showMessage("Video stopped")

    def download_video(self):
        url = self.url_input.text()
        if url:
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.download_status.setText("Downloading video...")
            download_path = QFileDialog.getExistingDirectory(self, "Select Download Directory")
            if download_path:
                self.download_thread = DownloadWorker(url, download_path, self.quality_select.currentText())
                self.download_thread.signals.progress.connect(self.update_progress)
                self.download_thread.signals.finished.connect(self.download_finished)
                self.download_thread.start()
            else:
                self.download_status.setText("Download canceled.")
        else:
            QMessageBox.warning(self, "Invalid URL", "Please enter a valid YouTube URL.")

    @pyqtSlot(int)
    def update_progress(self, percent):
        self.progress_bar.setValue(percent)

    @pyqtSlot(bool, str)
    def download_finished(self, success, message):
        self.download_status.setText(message)
        if success:
            self.progress_bar.setValue(100)
            if self.add_watermark_checkbox.isChecked():
                self.add_text_overlay(self.download_thread.file_path)
        else:
            QMessageBox.critical(self, "Download Error", message)

    def trim_video(self):
        start_time = int(self.trim_start_input.text())
        end_time = int(self.trim_end_input.text())
        video_path = self.download_thread.file_path
        output_path = os.path.join("processed", "trimmed_video.mp4")
        os.makedirs("processed", exist_ok=True)
        try:
            clip = VideoFileClip(video_path).subclip(start_time, end_time)
            clip.write_videofile(output_path, codec="libx264")
            self.process_text.append("Video trimmed successfully!")
        except Exception as e:
            self.process_text.append(f"Error: {str(e)}")
            logging.error(f"Error trimming video: {e}")

    def apply_filter(self):
        video_path = self.download_thread.file_path
        filter_type = self.filter_select.currentText()
        output_path = os.path.join("processed", f"{filter_type}_video.mp4")
        os.makedirs("processed", exist_ok=True)
        try:
            clip = VideoFileClip(video_path)
            if filter_type == "Grayscale":
                clip = clip.fx(vfx.blackwhite)
            elif filter_type == "Negative":
                clip = clip.fx(vfx.invert_colors)
            elif filter_type == "Blur":
                clip = clip.fx(vfx.blur, 2)
            clip.write_videofile(output_path, codec="libx264")
            self.process_text.append(f"{filter_type} filter applied successfully!")
        except Exception as e:
            self.process_text.append(f"Error: {str(e)}")
            logging.error(f"Error applying filter: {e}")

    def adjust_audio(self, volume_level):
        video_path = self.download_thread.file_path
        output_path = os.path.join("processed", "adjusted_audio_video.mp4")
        os.makedirs("processed", exist_ok=True)
        try:
            clip = VideoFileClip(video_path)
            clip = clip.volumex(volume_level / 100.0)
            clip.write_videofile(output_path, codec="libx264")
            self.process_text.append("Audio adjusted successfully!")
        except Exception as e:
            self.process_text.append(f"Error: {str(e)}")
            logging.error(f"Error adjusting audio: {e}")

    def add_subtitles(self):
        video_path = self.download_thread.file_path
        output_path = os.path.join("processed", "subtitled_video.mp4")
        os.makedirs("processed", exist_ok=True)
        subtitles = self.subtitle_input.toPlainText()
        try:
            clip = VideoFileClip(video_path)
            subtitle_clip = TextClip(subtitles, fontsize=24, color='white')
            subtitle_clip = subtitle_clip.set_position(('bottom')).set_duration(clip.duration)
            video = CompositeVideoClip([clip, subtitle_clip])
            video.write_videofile(output_path, codec="libx264")
            self.process_text.append("Subtitles added successfully!")
        except Exception as e:
            self.process_text.append(f"Error: {str(e)}")
            logging.error(f"Error adding subtitles: {e}")

    def analyze_channel(self):
        channel_url = self.channel_input.text()
        if channel_url:
            self.analysis_results.setText("Analyzing channel...")
            # Placeholder for actual analysis code
            # For simplicity, the analysis might use a tool like YouTube API to fetch and analyze channel data.
            self.analysis_results.append("Channel analysis complete!")
        else:
            QMessageBox.warning(self, "Invalid URL", "Please enter a valid YouTube channel URL.")

    def generate_video(self):
        script_content = self.script_input.toPlainText()
        output_path = os.path.join("generated", "generated_video.mp4")
        os.makedirs("generated", exist_ok=True)
        try:
            # Example: Simple text video generation
            clip = TextClip(script_content, fontsize=24, color='white', size=(1280, 720), bg_color='black', duration=10)
            clip.write_videofile(output_path, codec="libx264")
            self.status_bar.showMessage("Video generated successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Generation Error", f"Error: {str(e)}")
            logging.error(f"Error generating video: {e}")

    def add_text_overlay(self, video_path):
        output_path = os.path.join("processed", "watermarked_video.mp4")
        os.makedirs("processed", exist_ok=True)
        watermark_text = self.watermark_input.text()
        try:
            clip = VideoFileClip(video_path)
            txt_clip = TextClip(watermark_text, fontsize=70, color='white')
            txt_clip = txt_clip.set_position('center').set_duration(10)
            video = CompositeVideoClip([clip, txt_clip])
            video.write_videofile(output_path, codec="libx264")
            self.process_text.append("Watermark added successfully!")
        except Exception as e:
            self.process_text.append(f"Error: {str(e)}")
            logging.error(f"Error adding watermark: {e}")

    def encrypt_file(self, file_path, password):
        key = hashlib.sha256(password.encode()).digest()
        with open(file_path, 'rb') as f:
            data = f.read()
        cipher = Cipher(algorithms.AES(key), modes.EAX(), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(data) + encryptor.finalize()

        with open(f"{file_path}.enc", 'wb') as f:
            f.write(ciphertext)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
