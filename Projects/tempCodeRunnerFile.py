import tkinter as tk
from tkinter import filedialog, ttk
import pygame
import os
import time
from mutagen.mp3 import MP3
from mutagen.wave import WAVE

class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Functional Music Player")
        self.root.geometry("600x450")
        self.root.resizable(False, False)

        # Initialize pygame mixer
        try:
            pygame.mixer.init()
        except pygame.error as e:
            print(f"Error initializing pygame mixer: {e}")
            tk.messagebox.showerror("Error", "Could not initialize audio mixer. Please ensure you have a working audio device.")
            self.root.destroy()
            return

        # --- State and Track Variables ---
        self.track_list = []
        self.current_index = -1
        self.is_playing = False
        self.is_paused = False
        self.track_length = 0
        
        # --- Time tracking for progress bar ---
        # This is crucial for accurate progress updates
        self.current_position = 0
        self.playback_start_time = 0

        # --- GUI Elements ---

        # Playlist
        self.playlist_frame = tk.Frame(self.root)
        self.playlist_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        self.playlist_scroll = tk.Scrollbar(self.playlist_frame)
        self.playlist_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.playlist = tk.Listbox(self.playlist_frame, bg="#f0f0f0", fg="black", selectbackground="#3498db", selectforeground="white", yscrollcommand=self.playlist_scroll.set)
        self.playlist.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.playlist_scroll.config(command=self.playlist.yview)
        self.playlist.bind('<<ListboxSelect>>', self.on_track_select)

        # Track info
        self.track_label = tk.Label(self.root, text="No track loaded", wraplength=580, font=("Helvetica", 10))
        self.track_label.pack(pady=5)

        # Progress bar
        self.progress_frame = tk.Frame(self.root)
        self.progress_frame.pack(fill=tk.X, padx=20)
        self.time_label = tk.Label(self.progress_frame, text="00:00 / 00:00", font=("Helvetica", 9))
        self.time_label.pack()
        self.progress = ttk.Scale(self.progress_frame, from_=0, to=100, orient=tk.HORIZONTAL, command=self.on_seek)
        self.progress.pack(fill=tk.X, pady=5)
        
        # Controls
        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack(pady=20)
        
        style = {"font": ("Helvetica", 12), "width": 5}
        tk.Button(self.control_frame, text="⏮", **style, command=self.previous_track).pack(side=tk.LEFT, padx=5)
        self.play_pause_button = tk.Button(self.control_frame, text="▶", **style, command=self.play_pause)
        self.play_pause_button.pack(side=tk.LEFT, padx=5)
        tk.Button(self.control_frame, text="⏹", **style, command=self.stop).pack(side=tk.LEFT, padx=5)
        tk.Button(self.control_frame, text="⏭", **style, command=self.next_track).pack(side=tk.LEFT, padx=5)
        tk.Button(self.root, text="Add Tracks", command=self.add_tracks).pack(pady=5)

        # Volume
        self.volume_frame = tk.Frame(self.root)
        self.volume_frame.pack(pady=5, side=tk.RIGHT, padx=20)
        tk.Label(self.volume_frame, text="Volume:").pack(side=tk.LEFT)
        self.volume = ttk.Scale(self.volume_frame, from_=0, to=1, orient=tk.HORIZONTAL, command=self.set_volume)
        self.volume.set(0.5)
        pygame.mixer.music.set_volume(0.5)
        self.volume.pack(side=tk.LEFT, padx=5)
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.update_progress()

    def add_tracks(self):
        files = filedialog.askopenfilenames(filetypes=[("Audio Files", "*.mp3 *.wav")])
        if files:
            for file in files:
                if file not in self.track_list:
                    self.track_list.append(file)
                    track_name = os.path.basename(file)
                    self.playlist.insert(tk.END, track_name)
            if not self.is_playing and not self.is_paused:
                self.current_index = 0
                self.playlist.selection_set(0)
                self.load_and_play()

    def on_track_select(self, event=None):
        if not self.playlist.curselection():
            return
        self.current_index = self.playlist.curselection()[0]
        self.load_and_play()

    def load_and_play(self):
        self.stop(reset_ui=False) # Stop current track but don't reset the selection
        try:
            current_track_path = self.track_list[self.current_index]
            pygame.mixer.music.load(current_track_path)

            if current_track_path.lower().endswith('.mp3'):
                audio = MP3(current_track_path)
            elif current_track_path.lower().endswith('.wav'):
                audio = WAVE(current_track_path)
            self.track_length = audio.info.length

            self.track_label.config(text=os.path.basename(current_track_path))
            self.progress.config(to=self.track_length)
            self.time_label.config(text=f"00:00 / {self.format_time(self.track_length)}")
            self.play_pause()
            
        except (pygame.error, Exception) as e:
            print(f"Error loading track {current_track_path}: {e}")
            self.track_label.config(text=f"Error loading {os.path.basename(current_track_path)}")
            self.current_index = -1

    def play_pause(self):
        if not self.track_list:
            return
            
        if not self.is_playing:  # If stopped or paused
            if self.is_paused:
                pygame.mixer.music.unpause()
                self.is_paused = False
            else: # Was stopped
                pygame.mixer.music.play(start=self.current_position)
            
            self.playback_start_time = time.time() - self.current_position
            self.is_playing = True
            self.play_pause_button.config(text="⏸")
        
        else: # Is playing, so pause it
            pygame.mixer.music.pause()
            self.is_playing = False
            self.is_paused = True
            self.current_position = time.time() - self.playback_start_time
            self.play_pause_button.config(text="▶")

    def stop(self, reset_ui=True):
        pygame.mixer.music.stop()
        self.is_playing = False
        self.is_paused = False
        self.current_position = 0
        self.progress.set(0)
        self.play_pause_button.config(text="▶")
        if self.track_length > 0:
             self.time_label.config(text=f"00:00 / {self.format_time(self.track_length)}")
        if reset_ui and self.current_index != -1:
             self.playlist.selection_clear(self.current_index, self.current_index)
             self.current_index = -1
             self.track_label.config(text="No track loaded")
             self.time_label.config(text="00:00 / 00:00")


    def next_track(self):
        if not self.track_list: return
        if self.current_index < len(self.track_list) - 1:
            self.current_index += 1
        else:
            self.current_index = 0 # Loop to the beginning
        
        self.playlist.selection_clear(0, tk.END)
        self.playlist.selection_set(self.current_index)
        self.load_and_play()

    def previous_track(self):
        if not self.track_list: return
        if self.current_index > 0:
            self.current_index -= 1
        else:
            self.current_index = len(self.track_list) - 1 # Loop to the end

        self.playlist.selection_clear(0, tk.END)
        self.playlist.selection_set(self.current_index)
        self.load_and_play()

    def set_volume(self, value):
        pygame.mixer.music.set_volume(float(value))

    def on_seek(self, value_str):
        if not pygame.mixer.music.get_busy() and not self.is_paused:
            return
            
        seek_pos = float(value_str)
        self.current_position = seek_pos
        self.playback_start_time = time.time() - seek_pos
        
        if self.is_playing:
            pygame.mixer.music.play(start=self.current_position)
        elif self.is_paused:
            # To seek while paused, we play and immediately pause.
            pygame.mixer.music.play(start=self.current_position)
            pygame.mixer.music.pause()


    def update_progress(self):
        if self.is_playing and self.track_length > 0:
            # Calculate position based on real time elapsed
            self.current_position = time.time() - self.playback_start_time
            if self.current_position >= self.track_length:
                self.next_track()
            else:
                self.progress.set(self.current_position)
                self.time_label.config(text=f"{self.format_time(self.current_position)} / {self.format_time(self.track_length)}")
        
        self.root.after(100, self.update_progress) # Update every 100ms for smoother progress bar

    def format_time(self, seconds):
        if seconds < 0: seconds = 0
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"

    def on_closing(self):
        pygame.mixer.quit()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MusicPlayer(root)
    root.mainloop()