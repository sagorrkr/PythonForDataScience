import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import pygame
import os
import time
from mutagen.mp3 import MP3
from mutagen.wave import WAVE
import random
import logging


class MusicPlayer:
    #Constants for GUI styling and audio settings
    WINDOW_SIZE = "600x500"
    BUTTON_STYLE = {"font": ("Helvetica", 12), "width": 5}
    UPDATE_INTERVAL_MS = 1000  
    AUDIO_BUFFER = 4096  
    MAX_FILE_SIZE_MB = 50 
    MAX_BITRATE_KBPS = 192  
    PLAYLIST_FILE = "playlist.txt"


    def __init__(self, root):
        self.root = root
        self.root.title("Group - B Music Player")
        self.root.geometry(self.WINDOW_SIZE)
        self.root.resizable(False, False)


        #Setup logging for debugging
        logging.basicConfig(filename="music_player.log", level=logging.DEBUG,
                           format="%(asctime)s - %(levelname)s - %(message)s")

        #Initialize pygame mixer with optimized settings
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=self.AUDIO_BUFFER)
            pygame.mixer.music.set_volume(0.5)
            logging.info("Pygame mixer initialized successfully")
        except pygame.error as e:
            messagebox.showerror("Error", f"Audio initialization failed: {e}\nEnsure no other audio apps are running.")
            logging.error(f"Audio init failed: {e}")
            self.root.destroy()
            return


        #State variables
        self.tracks = []
        self.current_track_index = -1
        self.is_playing = False
        self.is_paused = False
        self.track_length = 0
        self.current_position = 0
        self.playback_start_time = 0


        #Setup GUI
        self.setup_gui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.update_progress()


    def setup_gui(self):
        """Set up the GUI elements."""
        # Album art
        try:
            self.album_art = tk.PhotoImage(file="/Users/sagor/Desktop/PythonForDataScience/101/Projects/university_art.png")
            self.album_label = tk.Label(self.root, image=self.album_art)
            self.album_label.pack(pady=5)
        except tk.TclError as e:
            messagebox.showwarning("Warning", "Could not load university_art.png. Place it in the same directory.")
            logging.warning(f"Album art load failed: {e}")
            self.album_label = tk.Label(self.root, text="No album art", font=("Helvetica", 10))
            self.album_label.pack(pady=5)


        #Playlist frame
        self.playlist_frame = tk.Frame(self.root)
        self.playlist_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        self.playlist_scroll = tk.Scrollbar(self.playlist_frame)
        self.playlist_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.playlist = tk.Listbox(
            self.playlist_frame, bg="#f0f0f0", fg="black",
            selectbackground="#3498db", selectforeground="white",
            yscrollcommand=self.playlist_scroll.set
        )
        self.playlist.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.playlist_scroll.config(command=self.playlist.yview)
        self.playlist.bind('<<ListboxSelect>>', self.on_track_select)


        #Track info
        self.track_label = tk.Label(self.root, text="No track loaded", wraplength=580, font=("Helvetica", 10))
        self.track_label.pack(pady=5)


        #Progress bar
        self.progress_frame = tk.Frame(self.root)
        self.progress_frame.pack(fill=tk.X, padx=20)
        self.time_label = tk.Label(self.progress_frame, text="00:00 / 00:00", font=("Helvetica", 9))
        self.time_label.pack()
        self.progress = ttk.Scale(self.progress_frame, from_=0, to=100, orient=tk.HORIZONTAL, command=self.on_seek)
        self.progress.pack(fill=tk.X, pady=5)


        #Controls
        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack(pady=20)
        tk.Button(self.control_frame, text="⏮", **self.BUTTON_STYLE, command=self.previous_track).pack(side=tk.LEFT, padx=5)
        self.play_pause_button = tk.Button(self.control_frame, text="▶", **self.BUTTON_STYLE, command=self.play_pause)
        self.play_pause_button.pack(side=tk.LEFT, padx=5)
        tk.Button(self.control_frame, text="⏹", **self.BUTTON_STYLE, command=self.stop).pack(side=tk.LEFT, padx=5)
        tk.Button(self.control_frame, text="⏭", **self.BUTTON_STYLE, command=self.next_track).pack(side=tk.LEFT, padx=5)
        tk.Button(self.control_frame, text="🔀", **self.BUTTON_STYLE, command=self.shuffle_tracks).pack(side=tk.LEFT, padx=5)


        #Playlist management buttons
        tk.Button(self.root, text="Add Tracks", command=self.add_tracks).pack(side=tk.LEFT, padx=10, pady=5)
        tk.Button(self.root, text="Clear Playlist", command=self.clear_playlist).pack(side=tk.LEFT, padx=10, pady=5)
        tk.Button(self.root, text="Save Playlist", command=self.save_playlist).pack(side=tk.LEFT, padx=10, pady=5)
        #tk.Button(self.root, text="Load Playlist", command=self.load_playlist).pack(side=tk.LEFT, padx=10, pady=5)


        #Volume
        self.volume_frame = tk.Frame(self.root)
        self.volume_frame.pack(pady=5, side=tk.RIGHT, padx=20)
        tk.Label(self.volume_frame, text="Volume:").pack(side=tk.LEFT)
        self.volume = ttk.Scale(self.volume_frame, from_=0, to=1, orient=tk.HORIZONTAL, command=self.set_volume)
        self.volume.set(0.5)
        self.volume.pack(side=tk.LEFT, padx=5)


    def add_tracks(self):
        """Add audio files to the playlist."""
        files = filedialog.askopenfilenames(filetypes=[("Audio Files", "*.mp3 *.wav")])
        for file in files:
            if file not in self.tracks and self.is_valid_audio_file(file):
                self.tracks.append(file)
                self.playlist.insert(tk.END, os.path.basename(file))
        if files and self.current_track_index == -1:
            self.current_track_index = 0
            self.playlist.selection_set(0)
            self.load_and_play()


    def is_valid_audio_file(self, file_path):
        """Validate audio file before adding."""
        try:
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            if file_size_mb > self.MAX_FILE_SIZE_MB:
                messagebox.showwarning("Warning", f"File {os.path.basename(file_path)} is too large ({file_size_mb:.1f}MB). May cause buffering.")
                logging.warning(f"Large file detected: {file_path} ({file_size_mb:.1f}MB)")
                return False
            if file_path.lower().endswith('.mp3'):
                audio = MP3(file_path)
                bitrate = audio.info.bitrate // 1000
                if bitrate > self.MAX_BITRATE_KBPS:
                    messagebox.showwarning("Warning", f"File {os.path.basename(file_path)} has high bitrate ({bitrate}kbps). May cause playback issues.")
                    logging.warning(f"High bitrate detected: {file_path} ({bitrate}kbps)")
            elif file_path.lower().endswith('.wav'):
                audio = WAVE(file_path)
            else:
                return False
            if audio.info.length > 600:
                messagebox.showwarning("Warning", f"File {os.path.basename(file_path)} is long ({audio.info.length/60:.1f}min). May cause buffering.")
                logging.warning(f"Long track detected: {file_path} ({audio.info.length/60:.1f}min)")
            return True
        except Exception as e:
            messagebox.showwarning("Warning", f"Invalid or corrupted file: {os.path.basename(file_path)}")
            logging.error(f"Invalid file {file_path}: {e}")
            return False


    def on_track_select(self, event=None):
        """Handle track selection from playlist."""
        if not self.playlist.curselection():
            return
        self.current_track_index = self.playlist.curselection()[0]
        self.load_and_play()


    def load_and_play(self):
        """Load and play the selected track."""
        if self.current_track_index < 0 or self.current_track_index >= len(self.tracks):
            return
        self.stop(reset_ui=False)
        try:
            track_path = self.tracks[self.current_track_index]
            start_time = time.time()
            pygame.mixer.music.load(track_path)
            audio = MP3(track_path) if track_path.lower().endswith('.mp3') else WAVE(track_path)
            self.track_length = audio.info.length
            self.track_label.config(text=os.path.basename(track_path))
            self.progress.config(to=self.track_length)
            self.time_label.config(text=f"00:00 / {self.format_time(self.track_length)}")
            self.play_pause()
            load_time = time.time() - start_time
            logging.info(f"Loaded {track_path} in {load_time:.2f}s")
            self.queue_next_track()
        except (pygame.error, Exception) as e:
            messagebox.showerror("Error", f"Failed to load {os.path.basename(track_path)}: {e}")
            logging.error(f"Load failed for {track_path}: {e}")
            self.current_track_index = -1
            self.track_label.config(text="No track loaded")


    def queue_next_track(self):
        """Queue the next track to reduce buffering."""
        if self.is_playing and self.current_track_index + 1 < len(self.tracks):
            try:
                pygame.mixer.music.queue(self.tracks[self.current_track_index + 1])
                logging.info(f"Queued next track: {self.tracks[self.current_track_index + 1]}")
            except pygame.error as e:
                logging.warning(f"Failed to queue next track: {e}")


    def play_pause(self):
        """Toggle play/pause state."""
        if not self.tracks:
            return
        if not self.is_playing:
            if self.is_paused:
                pygame.mixer.music.unpause()
                self.is_paused = False
            else:
                pygame.mixer.music.play(start=self.current_position)
            self.playback_start_time = time.time() - self.current_position
            self.is_playing = True
            self.play_pause_button.config(text="⏸")
            logging.info(f"Playing at position: {self.current_position}")
        else:
            pygame.mixer.music.pause()
            self.is_playing = False
            self.is_paused = True
            self.current_position = time.time() - self.playback_start_time
            self.play_pause_button.config(text="▶")
            logging.info(f"Paused at position: {self.current_position}")


    def stop(self, reset_ui=True):
        """Stop playback and optionally reset UI."""
        pygame.mixer.music.stop()
        self.is_playing = False
        self.is_paused = False
        self.current_position = 0
        self.progress.set(0)
        self.play_pause_button.config(text="▶")
        if self.track_length > 0:
            self.time_label.config(text=f"00:00 / {self.format_time(self.track_length)}")
        if reset_ui and self.current_track_index != -1:
            self.playlist.selection_clear(0, tk.END)
            self.current_track_index = -1
            self.track_label.config(text="No track loaded")
            self.time_label.config(text="00:00 / 00:00")
        logging.info("Playback stopped")


    def next_track(self):
        """Play the next track."""
        if not self.tracks:
            return
        self.current_track_index = (self.current_track_index + 1) % len(self.tracks)
        self.update_playlist_selection()
        self.load_and_play()


    def previous_track(self):
        """Play the previous track."""
        if not self.tracks:
            return
        self.current_track_index = (self.current_track_index - 1) % len(self.tracks)
        self.update_playlist_selection()
        self.load_and_play()


    def shuffle_tracks(self):
        """Shuffle the playlist and start from a random track."""
        if not self.tracks:
            return
        self.stop()
        random.shuffle(self.tracks)
        self.playlist.delete(0, tk.END)
        for track in self.tracks:
            self.playlist.insert(tk.END, os.path.basename(track))
        self.current_track_index = 0
        self.update_playlist_selection()
        self.load_and_play()


    def clear_playlist(self):
        """Clear the playlist and reset UI."""
        self.stop()
        self.tracks.clear()
        self.playlist.delete(0, tk.END)
        self.track_label.config(text="No track loaded")
        self.time_label.config(text="00:00 / 00:00")
        logging.info("Playlist cleared")


    def save_playlist(self):
        """Save the playlist to a file."""
        try:
            with open(self.PLAYLIST_FILE, "w") as f:
                for track in self.tracks:
                    f.write(f"{track}\n")
            messagebox.showinfo("Success", "Playlist saved successfully!")
            logging.info("Playlist saved")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save playlist: {e}")
            logging.error(f"Save playlist failed: {e}")


    def load_playlist(self):
        """Load a playlist from a file."""
        try:
            with open(self.PLAYLIST_FILE, "r") as f:
                files = [line.strip() for line in f if line.strip()]
            self.clear_playlist()
            for file in files:
                if os.path.exists(file) and self.is_valid_audio_file(file):
                    self.tracks.append(file)
                    self.playlist.insert(tk.END, os.path.basename(file))
            if self.tracks and self.current_track_index == -1:
                self.current_track_index = 0
                self.playlist.selection_set(0)
                self.load_and_play()
            logging.info("Playlist loaded")
        except FileNotFoundError:
            messagebox.showwarning("Warning", "No playlist file found.")
            logging.warning("Playlist file not found")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load playlist: {e}")
            logging.error(f"Load playlist failed: {e}")


    def update_playlist_selection(self):
        """Update the playlist selection UI."""
        self.playlist.selection_clear(0, tk.END)
        self.playlist.selection_set(self.current_track_index)
        self.playlist.see(self.current_track_index)


    def set_volume(self, value):
        """Set the playback volume."""
        pygame.mixer.music.set_volume(float(value))


    def on_seek(self, value):
        """Seek to a specific position in the track."""
        if not (self.is_playing or self.is_paused):
            return
        try:
            seek_pos = float(value)
            if abs(seek_pos - self.current_position) < 1:  # Avoid small seeks
                return
            self.current_position = seek_pos
            self.playback_start_time = time.time() - seek_pos
            if self.is_playing:
                pygame.mixer.music.play(start=seek_pos)
            elif self.is_paused:
                pygame.mixer.music.play(start=seek_pos)
                pygame.mixer.music.pause()
            logging.info(f"Seeking to position: {seek_pos}")
        except pygame.error as e:
            logging.error(f"Seek failed: {e}")


    def update_progress(self):
        """Update the progress bar and time label."""
        if self.is_playing and self.track_length > 0:
            self.current_position = time.time() - self.playback_start_time
            if self.current_position >= self.track_length:
                self.next_track()
            else:
                self.progress.set(self.current_position)
                self.time_label.config(text=f"{self.format_time(self.current_position)} / {self.format_time(self.track_length)}")
        self.root.after(self.UPDATE_INTERVAL_MS, self.update_progress)


    def format_time(self, seconds):
        """Format time in MM:SS."""
        seconds = max(0, seconds)
        minutes, secs = divmod(int(seconds), 60)
        return f"{minutes:02d}:{secs:02d}"


    def on_closing(self):
        """Clean up and close the application."""
        pygame.mixer.quit()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = MusicPlayer(root)
    root.mainloop()
