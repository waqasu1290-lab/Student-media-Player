import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import customtkinter as ctk
import vlc
import os
import time
import threading
from PIL import Image, ImageTk, ImageDraw, ImageFont
import json
from pathlib import Path
import math
import random
import mutagen
from mutagen import File
import datetime
import glob
import io
import sys
import ctypes
from ctypes import wintypes

# Set modern theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

# Windows DPI awareness for better scaling
if os.name == 'nt':
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass

class MintGreenTheme:
    """Mint green color theme configuration for Student Media Player"""
    COLORS = {
        # Mint Green Palette
        "primary": "#98FF98",
        "secondary": "#7FE87F", 
        "tertiary": "#65D165",
        "success": "#A8FFA8",
        "warning": "#FFE87F",
        "error": "#FF98A0",
        
        # Backgrounds
        "dark_bg": "#0F1510",
        "card_bg": "#1A211B",
        "surface": "#232B23",
        "hover_bg": "#2A332A",
        
        # Text
        "text_primary": "#FFFFFF",
        "text_secondary": "#B8E6B8",
        "text_muted": "#88AA88",
        
        # Visualizer
        "viz_primary": "#98FF98",
        "viz_secondary": "#7FE87F",
        "viz_tertiary": "#65D165"
    }

class ModernVisualizer(ctk.CTkCanvas):
    """Modern audio visualizer with mint green theme"""
    def __init__(self, parent, width=300, height=80, **kwargs):
        super().__init__(parent, width=width, height=height, **kwargs)
        self.configure(bg=MintGreenTheme.COLORS["dark_bg"], highlightthickness=0)
        self.width = width
        self.height = height
        self.bars = 64
        self.data = [0] * self.bars
        self.animation_id = None
        self.is_active = False
        
    def update_visualizer(self, player=None):
        """Update visualizer only when music is playing"""
        if player and player.is_playing():
            self.is_active = True
            # Simulate audio data with more dynamic movement
            new_data = []
            for d in self.data:
                change = random.uniform(-0.2, 0.3)
                new_value = max(0, d + change)
                new_data.append(new_value)
            self.data = [min(1.0, d) for d in new_data]
            self.draw_visualizer()
            self.animation_id = self.after(50, lambda: self.update_visualizer(player))
        else:
            # Stop animation and clear when paused
            self.is_active = False
            self.clear_visualizer()
    
    def draw_visualizer(self):
        """Draw the visualizer bars"""
        if not self.is_active:
            return
            
        self.delete("all")
        bar_width = self.width / self.bars
        spacing = bar_width * 0.2
        
        for i in range(self.bars):
            x = i * bar_width + spacing / 2
            bar_height = self.data[i] * (self.height - 20)
            y = self.height - bar_height - 10
            
            # Create gradient effect with mint green colors
            if self.data[i] > 0.8:
                color = MintGreenTheme.COLORS["viz_primary"]
            elif self.data[i] > 0.5:
                color = MintGreenTheme.COLORS["viz_secondary"]
            else:
                color = MintGreenTheme.COLORS["viz_tertiary"]
            
            self.create_rectangle(
                x, y, x + bar_width - spacing, self.height - 10,
                fill=color, outline="", width=0
            )
    
    def clear_visualizer(self):
        """Clear the visualizer completely"""
        self.delete("all")
        self.data = [0] * self.bars
    
    def stop(self):
        """Stop the visualizer animation"""
        self.is_active = False
        if self.animation_id:
            self.after_cancel(self.animation_id)
        self.clear_visualizer()

class StudyTimer:
    """Pomodoro-style study timer for students"""
    def __init__(self):
        self.study_time = 25 * 60  # 25 minutes
        self.break_time = 5 * 60   # 5 minutes
        self.current_time = self.study_time
        self.is_running = False
        self.is_break = False
        self.timer_thread = None
        
    def start(self, callback=None):
        """Start the timer"""
        self.is_running = True
        self.timer_thread = threading.Thread(target=self._run_timer, args=(callback,))
        self.timer_thread.daemon = True
        self.timer_thread.start()
    
    def pause(self):
        """Pause the timer"""
        self.is_running = False
    
    def reset(self):
        """Reset the timer"""
        self.is_running = False
        self.is_break = False
        self.current_time = self.study_time
    
    def _run_timer(self, callback=None):
        """Internal timer logic"""
        while self.is_running and self.current_time > 0:
            time.sleep(1)
            self.current_time -= 1
            if callback:
                callback(self.current_time, self.is_break)
        
        if self.is_running and self.current_time <= 0:
            self.is_break = not self.is_break
            self.current_time = self.break_time if self.is_break else self.study_time
            if callback:
                callback(self.current_time, self.is_break, True)

class PlaylistManager:
    """Manage playlists for the media player"""
    def __init__(self):
        self.playlists = {}
        self.current_playlist = "Main Playlist"
        self.load_playlists()
    
    def create_playlist(self, name):
        """Create a new playlist"""
        if name not in self.playlists:
            self.playlists[name] = []
            self.save_playlists()
            return True
        return False
    
    def delete_playlist(self, name):
        """Delete a playlist"""
        if name in self.playlists and name != "Main Playlist":
            del self.playlists[name]
            self.save_playlists()
            return True
        return False
    
    def add_to_playlist(self, playlist_name, song_path):
        """Add a song to a playlist"""
        if playlist_name in self.playlists:
            if song_path not in self.playlists[playlist_name]:
                self.playlists[playlist_name].append(song_path)
                self.save_playlists()
                return True
        return False
    
    def remove_from_playlist(self, playlist_name, song_path):
        """Remove a song from a playlist"""
        if playlist_name in self.playlists and song_path in self.playlists[playlist_name]:
            self.playlists[playlist_name].remove(song_path)
            self.save_playlists()
            return True
        return False
    
    def save_playlists(self):
        """Save playlists to file"""
        try:
            with open("playlists.json", "w", encoding='utf-8') as f:
                json.dump(self.playlists, f, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving playlists: {e}")
    
    def load_playlists(self):
        """Load playlists from file"""
        try:
            if os.path.exists("playlists.json"):
                with open("playlists.json", "r", encoding='utf-8') as f:
                    self.playlists = json.load(f)
        except:
            # Create default main playlist
            self.playlists = {"Main Playlist": []}

class ImageManager:
    """Manage images and album art efficiently"""
    def __init__(self):
        self.image_cache = {}
        self.album_art_cache = {}
        self.default_album_art = self._create_famous_music_logo()
        
    def _create_famous_music_logo(self):
        """Create a famous music logo (Spotify-style) for default album art"""
        size = (200, 200)
        img = Image.new('RGB', size, color=(30, 215, 96))  # Spotify green background
        draw = ImageDraw.Draw(img)
        
        # Draw three curved sound waves (Spotify logo style)
        center_x, center_y = size[0] // 2, size[1] // 2
        wave_radius = 30
        
        # Draw three curved waves
        for i in range(3):
            wave_height = 8 - i * 2
            start_angle = 45 + i * 10
            end_angle = 315 - i * 10
            
            # Draw curved wave
            bbox = [
                center_x - wave_radius + i * 15,
                center_y - wave_radius + i * 15,
                center_x + wave_radius - i * 15,
                center_y + wave_radius - i * 15
            ]
            
            # Draw the curved line
            draw.arc(bbox, start_angle, end_angle, fill=(255, 255, 255), width=wave_height)
        
        return ctk.CTkImage(light_image=img, dark_image=img, size=size)
        
    def load_image(self, path, size=(40, 40)):
        """Load and cache image with proper error handling"""
        cache_key = f"{path}_{size[0]}x{size[1]}"
        if cache_key in self.image_cache:
            return self.image_cache[cache_key]
        
        try:
            if os.path.exists(path):
                img = Image.open(path)
                # Convert to RGB and ensure no transparency issues
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (15, 21, 16))  # Dark theme background
                    if img.mode == 'RGBA':
                        background.paste(img, mask=img.split()[-1])
                    else:
                        background.paste(img)
                    img = background
                else:
                    img = img.convert('RGB')
                
                img = img.resize(size, Image.Resampling.LANCZOS)
                ctk_image = ctk.CTkImage(light_image=img, dark_image=img, size=size)
                self.image_cache[cache_key] = ctk_image
                return ctk_image
        except Exception as e:
            print(f"Error loading image {path}: {e}")
        
        return None
    
    def extract_album_art(self, file_path, size=(150, 150)):
        """Extract album art from audio file with multiple methods"""
        cache_key = f"{file_path}_{size[0]}x{size[1]}"
        if cache_key in self.album_art_cache:
            return self.album_art_cache[cache_key]
        
        try:
            audio = File(file_path)
            if not audio:
                return self.default_album_art
            
            # Method 1: Check for embedded pictures
            if hasattr(audio, 'pictures') and audio.pictures:
                for picture in audio.pictures:
                    try:
                        img = Image.open(io.BytesIO(picture.data))
                        return self._process_album_art(img, size, cache_key)
                    except:
                        continue
            
            # Method 2: Check for APIC tag (ID3v2)
            if hasattr(audio, 'tags'):
                for tag in audio.tags.keys():
                    if 'APIC' in tag or 'covr' in tag or 'picture' in tag.lower():
                        try:
                            picture_data = audio.tags[tag].data
                            img = Image.open(io.BytesIO(picture_data))
                            return self._process_album_art(img, size, cache_key)
                        except:
                            continue
            
            # Method 3: Look for external image files
            directory = os.path.dirname(file_path)
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            
            # Common album art file names
            art_files = [
                'cover.jpg', 'cover.png', 'folder.jpg', 'folder.png',
                'album.jpg', 'album.png', 'artwork.jpg', 'artwork.png',
                'front.jpg', 'front.png', 'back.jpg', 'back.png',
                f'{base_name}.jpg', f'{base_name}.png'
            ]
            
            for art_file in art_files:
                art_path = os.path.join(directory, art_file)
                if os.path.exists(art_path):
                    img = self.load_image(art_path, size)
                    if img:
                        self.album_art_cache[cache_key] = img
                        return img
            
        except Exception as e:
            print(f"Error extracting album art from {file_path}: {e}")
        
        # Return famous music logo when no album art found
        return self.default_album_art
    
    def _process_album_art(self, img, size, cache_key):
        """Process and cache album art image"""
        # Convert to RGB and ensure proper background
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (35, 33, 35))  # Card background color
            if img.mode == 'RGBA':
                background.paste(img, mask=img.split()[-1])
            else:
                background.paste(img)
            img = background
        else:
            img = img.convert('RGB')
        
        img = img.resize(size, Image.Resampling.LANCZOS)
        ctk_image = ctk.CTkImage(light_image=img, dark_image=img, size=size)
        self.album_art_cache[cache_key] = ctk_image
        return ctk_image

class StudentMediaPlayer(ctk.CTk):
    """Main Student Media Player Application"""
    
    def __init__(self):
        super().__init__()
        
        # Window configuration
        self.title("Student Media Player 🎵")
        self.geometry("1200x700")
        self.minsize(1000, 600)
        
        # Initialize components
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.image_manager = ImageManager()
        
        # Application state
        self.current_file = None
        self.is_playing = False
        self.playlist = []
        self.current_index = 0
        self.volume = 70
        self.player.audio_set_volume(self.volume)
        self.is_muted = False
        self.pre_mute_volume = self.volume
        self.is_repeat = False
        
        # Study features
        self.study_timer = StudyTimer()
        self.study_session_active = False
        
        # Playlist manager
        self.playlist_manager = PlaylistManager()
        
        # Loading flag for large folders
        self.is_loading = False
        self.loading_thread = None
        
        # Progress bar control
        self.is_seeking = False
        
        # Create logo with multiple fallback options
        self.setup_logo()
        
        # Setup UI
        self.setup_ui()
        
        # Setup keyboard shortcuts
        self.setup_shortcuts()
        
        # Setup tooltips
        self.setup_tooltips()
        
        # Setup VLC event manager
        self.setup_vlc_events()
        
        # Start UI updates
        self.update_ui()
    
    def setup_vlc_events(self):
        """Setup VLC event manager for repeat functionality"""
        try:
            event_manager = self.player.event_manager()
            event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, self._on_media_end)
        except Exception as e:
            print(f"Error setting up VLC events: {e}")
    
    def _on_media_end(self, event):
        """Handle when media ends for repeat functionality"""
        if self.is_repeat and self.playlist:
            # Repeat the current song
            self.after(100, lambda: self.play_song(self.current_index))
        elif self.playlist and self.is_playing:
            # Play next song automatically
            next_index = (self.current_index + 1) % len(self.playlist)
            self.after(100, lambda: self.play_song(next_index))
    
    def setup_logo(self):
        """Setup logo with multiple fallback options"""
        logo_paths = [
            "logo.png", "logo.jpg", "logo.jpeg", "logo.gif", "logo.bmp",
            "my_logo.png", "my_logo.jpg", "my_logo.jpeg", 
            "assets/logo.png", "images/logo.png",
            "icon.png", "app_logo.png"
        ]
        
        self.logo_image = None
        
        for logo_path in logo_paths:
            try:
                if os.path.exists(logo_path):
                    print(f"Attempting to load logo from: {logo_path}")
                    img = Image.open(logo_path)
                    
                    # Convert to RGB with dark theme background
                    if img.mode in ('RGBA', 'LA', 'P'):
                        background = Image.new('RGB', img.size, (15, 21, 16))
                        if img.mode == 'RGBA':
                            background.paste(img, mask=img.split()[-1])
                        else:
                            background.paste(img)
                        img = background
                    else:
                        img = img.convert('RGB')
                    
                    img = img.resize((40, 40), Image.Resampling.LANCZOS)
                    self.logo_image = ctk.CTkImage(
                        light_image=img,
                        dark_image=img,
                        size=(40, 40)
                    )
                    print(f"✅ Logo successfully loaded from: {logo_path}")
                    break
            except Exception as e:
                print(f"❌ Failed to load logo from {logo_path}: {e}")
                continue
        
        if self.logo_image is None:
            print("🔄 Creating placeholder logo...")
            img = Image.new('RGB', (64, 64), color=(15, 21, 16))
            draw = ImageDraw.Draw(img)
            
            # Draw mint green circle
            draw.ellipse([10, 10, 54, 54], fill=(152, 255, 152))
            
            # Draw music note in dark color
            draw.ellipse([22, 22, 32, 32], fill=(15, 21, 16))
            draw.rectangle([30, 22, 32, 42], fill=(15, 21, 16))
            draw.rectangle([22, 38, 30, 42], fill=(15, 21, 16))
            
            self.logo_image = ctk.CTkImage(
                light_image=img,
                dark_image=img,
                size=(40, 40)
            )
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Global keyboard bindings
        self.bind('<space>', lambda e: self.toggle_playback())
        self.bind('<Right>', lambda e: self.forward_10s())
        self.bind('<Left>', lambda e: self.backward_10s())
        self.bind('<Control-Right>', lambda e: self.next_song())
        self.bind('<Control-Left>', lambda e: self.previous_song())
        self.bind('<Up>', lambda e: self.volume_up())
        self.bind('<Down>', lambda e: self.volume_down())
        self.bind('m', lambda e: self.toggle_mute())
        self.bind('M', lambda e: self.toggle_mute())
        self.bind('r', lambda e: self.toggle_repeat())
        self.bind('R', lambda e: self.toggle_repeat())
        self.bind('o', lambda e: self.open_files())
        self.bind('O', lambda e: self.open_files())
        self.bind('f', lambda e: self.open_folder())
        self.bind('F', lambda e: self.open_folder())
        self.bind('Escape', lambda e: self.minimize_player())
    
    def setup_tooltips(self):
        """Setup tooltips for buttons"""
        self.tooltip_window = None
        self.tooltip_label = None
        
    def show_tooltip(self, widget, text):
        """Show tooltip for widget"""
        if hasattr(widget, '_tooltip_bound'):
            return
            
        widget._tooltip_bound = True
        
        def on_enter(event):
            if self.tooltip_window:
                self.tooltip_window.destroy()
            
            self.tooltip_window = tk.Toplevel(self)
            self.tooltip_window.wm_overrideredirect(True)
            self.tooltip_window.wm_attributes("-topmost", True)
            self.tooltip_window.configure(bg=MintGreenTheme.COLORS["card_bg"], relief='solid', borderwidth=1)
            
            self.tooltip_label = tk.Label(
                self.tooltip_window, 
                text=text, 
                bg=MintGreenTheme.COLORS["card_bg"],
                fg=MintGreenTheme.COLORS["text_primary"],
                font=("Segoe UI", 9),
                padx=8, 
                pady=4
            )
            self.tooltip_label.pack()
            
            x = widget.winfo_rootx() + widget.winfo_width() // 2
            y = widget.winfo_rooty() - 30
            self.tooltip_window.wm_geometry(f"+{x}+{y}")
        
        def on_leave(event):
            if self.tooltip_window:
                self.tooltip_window.destroy()
                self.tooltip_window = None
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    def volume_up(self):
        """Increase volume by 10%"""
        if self.is_muted:
            self.toggle_mute()
        new_volume = min(100, self.volume + 10)
        self.volume_slider.set(new_volume)
        self.set_volume(new_volume)
    
    def volume_down(self):
        """Decrease volume by 10%"""
        if self.is_muted:
            self.toggle_mute()
        new_volume = max(0, self.volume - 10)
        self.volume_slider.set(new_volume)
        self.set_volume(new_volume)
    
    def toggle_mute(self):
        """Toggle mute/unmute"""
        if self.is_muted:
            self.is_muted = False
            self.volume = self.pre_mute_volume
            self.player.audio_set_volume(self.volume)
            self.volume_slider.set(self.volume)
            self.mute_btn.configure(text="🔊")
        else:
            self.is_muted = True
            self.pre_mute_volume = self.volume
            self.player.audio_set_volume(0)
            self.mute_btn.configure(text="🔇")
    
    def toggle_repeat(self):
        """Toggle repeat/loop mode"""
        self.is_repeat = not self.is_repeat
        if self.is_repeat:
            self.repeat_btn.configure(
                fg_color=MintGreenTheme.COLORS["primary"],
                text_color=MintGreenTheme.COLORS["dark_bg"]
            )
        else:
            self.repeat_btn.configure(
                fg_color=MintGreenTheme.COLORS["surface"],
                text_color=MintGreenTheme.COLORS["text_primary"]
            )
    
    def minimize_player(self):
        """Minimize the player window"""
        self.iconify()
    
    def setup_ui(self):
        """Setup the main user interface"""
        # Configure grid
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create sidebar
        self.create_sidebar()
        
        # Create main content area
        self.create_main_content()
        
        # Create bottom player controls
        self.create_player_controls()
    
    def create_sidebar(self):
        """Create the sidebar with navigation and features"""
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=5)
        self.sidebar.grid_propagate(False)
        
        # Logo and app name
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.pack(fill="x", padx=15, pady=(20, 15))
        
        if self.logo_image:
            ctk.CTkLabel(logo_frame, image=self.logo_image, text="").pack(side="left")
        ctk.CTkLabel(logo_frame, text="Student Media Player", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(side="left", padx=(10, 0))
        
        # Navigation buttons
        nav_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        nav_frame.pack(fill="x", padx=15, pady=10)
        
        buttons = [
            ("📁 Open Files (O)", self.open_files),
            ("📂 Open Folder (F)", self.open_folder),
            ("🎵 Playlists", self.show_playlists),
            ("⏱️ Study Timer", self.toggle_study_timer),
            ("📚 Study Focus", self.toggle_study_mode),
        ]
        
        for text, command in buttons:
            btn = ctk.CTkButton(nav_frame, text=text, command=command,
                               fg_color=MintGreenTheme.COLORS["surface"],
                               hover_color=MintGreenTheme.COLORS["hover_bg"])
            btn.pack(fill="x", pady=3)
        
        # Keyboard shortcuts info
        shortcuts_frame = ctk.CTkFrame(self.sidebar, fg_color=MintGreenTheme.COLORS["card_bg"])
        shortcuts_frame.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(shortcuts_frame, text="🎹 Shortcuts", 
                    font=ctk.CTkFont(weight="bold")).pack(pady=(8, 5))
        
        shortcuts = [
            "Space: Play/Pause",
            "←→: Seek 10s",
            "Ctrl+←→: Next/Prev",
            "↑↓: Volume",
            "M: Mute/Unmute",
            "R: Repeat",
            "O: Open Files",
            "F: Open Folder"
        ]
        
        for shortcut in shortcuts:
            ctk.CTkLabel(shortcuts_frame, text=shortcut, 
                        font=ctk.CTkFont(size=11),
                        text_color=MintGreenTheme.COLORS["text_muted"]).pack(anchor="w", padx=10, pady=1)
        
        # Study timer display
        self.timer_frame = ctk.CTkFrame(self.sidebar, fg_color=MintGreenTheme.COLORS["card_bg"])
        self.timer_frame.pack(fill="x", padx=15, pady=10)
        
        self.timer_label = ctk.CTkLabel(self.timer_frame, text="25:00", 
                                       font=ctk.CTkFont(size=24, weight="bold"))
        self.timer_label.pack(pady=8)
        
        timer_btn_frame = ctk.CTkFrame(self.timer_frame, fg_color="transparent")
        timer_btn_frame.pack(fill="x", padx=10, pady=5)
        
        self.timer_btn = ctk.CTkButton(timer_btn_frame, text="Start Timer", 
                                      command=self.toggle_timer,
                                      fg_color=MintGreenTheme.COLORS["primary"],
                                      text_color=MintGreenTheme.COLORS["dark_bg"])
        self.timer_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        ctk.CTkButton(timer_btn_frame, text="Reset", 
                     command=self.reset_timer).pack(side="left", fill="x", expand=True, padx=(5, 0))
        
        # Currently playing info
        self.now_playing_frame = ctk.CTkFrame(self.sidebar, fg_color=MintGreenTheme.COLORS["card_bg"])
        self.now_playing_frame.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(self.now_playing_frame, text="Now Playing", 
                    font=ctk.CTkFont(weight="bold")).pack(pady=(8, 5))
        
        self.current_song_label = ctk.CTkLabel(self.now_playing_frame, text="No song playing", 
                                              wraplength=190)
        self.current_song_label.pack(pady=5)
        
        # Loading progress
        self.loading_frame = ctk.CTkFrame(self.sidebar, fg_color=MintGreenTheme.COLORS["card_bg"])
        self.loading_label = ctk.CTkLabel(self.loading_frame, text="", font=ctk.CTkFont(size=12))
        self.loading_progress = ctk.CTkProgressBar(self.loading_frame)
        self.loading_frame.pack(fill="x", padx=15, pady=5)
        self.loading_frame.pack_forget()
    
    def create_main_content(self):
        """Create the main content area"""
        main_frame = ctk.CTkFrame(self, corner_radius=10)
        main_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 5), pady=5)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        
        # Header with tabs
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=15)
        
        # Tab view
        self.tabview = ctk.CTkTabview(header_frame)
        self.tabview.pack(fill="x")
        
        # Create tabs
        self.library_tab = self.tabview.add("🎵 Library")
        self.playlists_tab = self.tabview.add("📋 Playlists")
        self.albums_tab = self.tabview.add("💿 Albums")
        
        # Setup each tab
        self.setup_library_tab()
        self.setup_playlists_tab()
        self.setup_albums_tab()
        
        # Visualizer
        self.visualizer = ModernVisualizer(main_frame, width=800, height=100)
        self.visualizer.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
    
    def setup_library_tab(self):
        """Setup the music library tab"""
        # Search bar
        search_frame = ctk.CTkFrame(self.library_tab, fg_color="transparent")
        search_frame.pack(fill="x", pady=10)
        
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="🔍 Search songs...", width=300)
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", self.search_songs)
        
        ctk.CTkButton(search_frame, text="📁 Add Files", 
                     command=self.open_files, width=110).pack(side="left", padx=(0, 5))
        ctk.CTkButton(search_frame, text="📂 Add Folder", 
                     command=self.open_folder, width=110).pack(side="left")
        
        # Music library treeview
        library_frame = ctk.CTkFrame(self.library_tab)
        library_frame.pack(fill="both", expand=True, pady=10)
        
        # Create treeview with custom style
        style = ttk.Style()
        style.configure("Custom.Treeview", 
                       background=MintGreenTheme.COLORS["card_bg"],
                       foreground=MintGreenTheme.COLORS["text_primary"],
                       fieldbackground=MintGreenTheme.COLORS["card_bg"])
        
        style.map("Custom.Treeview", 
                 background=[('selected', MintGreenTheme.COLORS["primary"])],
                 foreground=[('selected', MintGreenTheme.COLORS["dark_bg"])])
        
        columns = ("#", "Title", "Artist", "Album", "Duration", "Path")
        self.library_tree = ttk.Treeview(library_frame, columns=columns, show="headings", 
                                        style="Custom.Treeview")
        
        # Configure columns
        for col in columns:
            self.library_tree.heading(col, text=col)
        
        self.library_tree.column("#", width=50)
        self.library_tree.column("Title", width=250)
        self.library_tree.column("Artist", width=180)
        self.library_tree.column("Album", width=180)
        self.library_tree.column("Duration", width=80)
        self.library_tree.column("Path", width=0, stretch=False)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(library_frame, orient="vertical", command=self.library_tree.yview)
        self.library_tree.configure(yscrollcommand=scrollbar.set)
        
        self.library_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind double-click to play
        self.library_tree.bind("<Double-1>", self.play_selected_song)
        
        # Right-click context menu
        self.create_context_menu()
    
    def setup_playlists_tab(self):
        """Setup the playlists tab"""
        playlists_frame = ctk.CTkFrame(self.playlists_tab)
        playlists_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Playlist management
        playlist_controls = ctk.CTkFrame(playlists_frame, fg_color="transparent")
        playlist_controls.pack(fill="x", pady=10)
        
        ctk.CTkButton(playlist_controls, text="➕ Create Playlist", 
                     command=self.create_new_playlist).pack(side="left", padx=(0, 8))
        ctk.CTkButton(playlist_controls, text="🗑️ Delete Playlist", 
                     command=self.delete_current_playlist).pack(side="left", padx=(0, 8))
        
        self.playlist_var = ctk.StringVar(value="Main Playlist")
        self.playlist_dropdown = ctk.CTkOptionMenu(playlist_controls, 
                                                  variable=self.playlist_var,
                                                  values=list(self.playlist_manager.playlists.keys()),
                                                  command=self.load_selected_playlist)
        self.playlist_dropdown.pack(side="left", padx=(0, 8))
        
        # Playlist songs
        self.playlist_tree = ttk.Treeview(playlists_frame, columns=("Title", "Artist", "Album", "Duration"), 
                                         show="headings", style="Custom.Treeview")
        
        for col in ("Title", "Artist", "Album", "Duration"):
            self.playlist_tree.heading(col, text=col)
            self.playlist_tree.column(col, width=180)
        
        playlist_scrollbar = ttk.Scrollbar(playlists_frame, orient="vertical", command=self.playlist_tree.yview)
        self.playlist_tree.configure(yscrollcommand=playlist_scrollbar.set)
        
        self.playlist_tree.pack(side="left", fill="both", expand=True)
        playlist_scrollbar.pack(side="right", fill="y")
        
        self.playlist_tree.bind("<Double-1>", self.play_from_playlist)
    
    def setup_albums_tab(self):
        """Setup the albums tab with album art thumbnails"""
        albums_frame = ctk.CTkFrame(self.albums_tab)
        albums_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Create scrollable canvas for albums
        self.albums_canvas = tk.Canvas(albums_frame, bg=MintGreenTheme.COLORS["dark_bg"], highlightthickness=0)
        albums_scrollbar = ttk.Scrollbar(albums_frame, orient="vertical", command=self.albums_canvas.yview)
        
        self.albums_scrollable_frame = ctk.CTkFrame(self.albums_canvas, fg_color=MintGreenTheme.COLORS["dark_bg"])
        self.albums_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.albums_canvas.configure(scrollregion=self.albums_canvas.bbox("all"))
        )
        
        self.albums_canvas.create_window((0, 0), window=self.albums_scrollable_frame, anchor="nw")
        self.albums_canvas.configure(yscrollcommand=albums_scrollbar.set)
        
        self.albums_canvas.pack(side="left", fill="both", expand=True)
        albums_scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel to scroll
        self.albums_canvas.bind("<MouseWheel>", self._on_mousewheel)
    
    def _on_mousewheel(self, event):
        """Handle mousewheel scrolling"""
        self.albums_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def create_context_menu(self):
        """Create right-click context menu"""
        self.context_menu = tk.Menu(self, tearoff=0, bg=MintGreenTheme.COLORS["card_bg"], fg=MintGreenTheme.COLORS["text_primary"])
        self.context_menu.add_command(label="Add to Playlist", command=self.add_to_playlist_dialog)
        self.context_menu.add_command(label="Remove from Library", command=self.remove_selected_song)
        
        self.library_tree.bind("<Button-3>", self.show_context_menu)
    
    def show_context_menu(self, event):
        """Show context menu on right-click"""
        item = self.library_tree.identify_row(event.y)
        if item:
            self.library_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def create_player_controls(self):
        """Create the bottom player controls"""
        controls_frame = ctk.CTkFrame(self, height=100, corner_radius=0)
        controls_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=(0, 5))
        controls_frame.grid_propagate(False)
        controls_frame.grid_columnconfigure(1, weight=1)
        
        # Album art
        self.album_art_frame = ctk.CTkFrame(controls_frame, width=80, height=80, 
                                          fg_color=MintGreenTheme.COLORS["surface"])
        self.album_art_frame.grid(row=0, column=0, rowspan=2, padx=15, pady=10)
        self.album_art_frame.grid_propagate(False)
        
        self.album_art_label = ctk.CTkLabel(self.album_art_frame, text="", 
                                          font=ctk.CTkFont(size=24),
                                          image=None)
        self.album_art_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Song info
        info_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        info_frame.grid(row=0, column=1, sticky="w", padx=15, pady=(15, 0))
        
        self.song_title_label = ctk.CTkLabel(info_frame, text="No song selected", 
                                           font=ctk.CTkFont(size=14, weight="bold"))
        self.song_title_label.pack(anchor="w")
        
        self.song_artist_label = ctk.CTkLabel(info_frame, text="Artist", 
                                            text_color=MintGreenTheme.COLORS["text_muted"])
        self.song_artist_label.pack(anchor="w")
        
        # Progress bar
        progress_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        progress_frame.grid(row=1, column=1, sticky="ew", padx=15, pady=(0, 15))
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ctk.CTkSlider(progress_frame, from_=0, to=100, 
                                         variable=self.progress_var,
                                         progress_color=MintGreenTheme.COLORS["primary"],
                                         button_color=MintGreenTheme.COLORS["secondary"])
        self.progress_bar.pack(fill="x")
        
        # Enhanced progress bar controls
        self.progress_bar.bind("<ButtonPress-1>", self.start_seeking)
        self.progress_bar.bind("<B1-Motion>", self.seek_audio)
        self.progress_bar.bind("<ButtonRelease-1>", self.stop_seeking)
        
        # Time labels
        time_frame = ctk.CTkFrame(progress_frame, fg_color="transparent")
        time_frame.pack(fill="x")
        
        self.current_time_label = ctk.CTkLabel(time_frame, text="0:00", font=ctk.CTkFont(size=11))
        self.current_time_label.pack(side="left")
        
        self.total_time_label = ctk.CTkLabel(time_frame, text="0:00", font=ctk.CTkFont(size=11))
        self.total_time_label.pack(side="right")
        
        # Control buttons
        controls_btn_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        controls_btn_frame.grid(row=0, column=2, rowspan=2, padx=15, pady=10)
        
        # Volume control with mute
        volume_frame = ctk.CTkFrame(controls_btn_frame, fg_color="transparent")
        volume_frame.pack(side="left", padx=10)
        
        self.mute_btn = ctk.CTkButton(volume_frame, text="🔊", width=35, height=35,
                                     command=self.toggle_mute)
        self.mute_btn.pack(side="left")
        self.show_tooltip(self.mute_btn, "Mute/Unmute (M)")
        
        self.volume_slider = ctk.CTkSlider(volume_frame, from_=0, to=100, 
                                          width=120, command=self.set_volume)
        self.volume_slider.set(self.volume)
        self.volume_slider.pack(side="left", padx=8)
        self.show_tooltip(self.volume_slider, "Volume Control (↑/↓)")
        
        # Repeat button
        self.repeat_btn = ctk.CTkButton(controls_btn_frame, text="🔂", width=35, height=35,
                                       command=self.toggle_repeat,
                                       fg_color=MintGreenTheme.COLORS["surface"])
        self.repeat_btn.pack(side="left", padx=(0, 15))
        self.show_tooltip(self.repeat_btn, "Repeat Mode (R)")
        
        # Playback buttons
        btn_size = 35
        buttons_frame = ctk.CTkFrame(controls_btn_frame, fg_color="transparent")
        buttons_frame.pack(side="left", padx=20)
        
        # Backward 10s
        backward_btn = ctk.CTkButton(buttons_frame, text="⏪", width=btn_size, height=btn_size,
                     command=self.backward_10s)
        backward_btn.pack(side="left", padx=3)
        self.show_tooltip(backward_btn, "Backward 10 seconds (←)")
        
        # Previous song
        prev_btn = ctk.CTkButton(buttons_frame, text="⏮", width=btn_size, height=btn_size,
                     command=self.previous_song)
        prev_btn.pack(side="left", padx=3)
        self.show_tooltip(prev_btn, "Previous song (Ctrl+←)")
        
        # Play/Pause
        self.play_btn = ctk.CTkButton(buttons_frame, text="▶", width=btn_size, height=btn_size,
                                     fg_color=MintGreenTheme.COLORS["primary"],
                                     text_color=MintGreenTheme.COLORS["dark_bg"],
                                     command=self.toggle_playback)
        self.play_btn.pack(side="left", padx=3)
        self.show_tooltip(self.play_btn, "Play/Pause (Space)")
        
        # Next song
        next_btn = ctk.CTkButton(buttons_frame, text="⏭", width=btn_size, height=btn_size,
                     command=self.next_song)
        next_btn.pack(side="left", padx=3)
        self.show_tooltip(next_btn, "Next song (Ctrl+→)")
        
        # Forward 10s
        forward_btn = ctk.CTkButton(buttons_frame, text="⏩", width=btn_size, height=btn_size,
                     command=self.forward_10s)
        forward_btn.pack(side="left", padx=3)
        self.show_tooltip(forward_btn, "Forward 10 seconds (→)")
    
    def open_files(self):
        """Open audio files and add to library - FIXED: Auto-playback management"""
        files = filedialog.askopenfilenames(
            title="Select Audio Files",
            filetypes=[
                ("Audio Files", "*.mp3 *.wav *.ogg *.flac *.m4a *.aac"),
                ("MP3 Files", "*.mp3"),
                ("WAV Files", "*.wav"),
                ("All Files", "*.*")
            ]
        )
        
        if files:
            # Stop current playback immediately
            self.stop_playback()
            # Clear existing playlist and library
            self.playlist.clear()
            for item in self.library_tree.get_children():
                self.library_tree.delete(item)
            # Add files and auto-play first one
            self.add_files_to_library(files, auto_play=True)
    
    def open_folder(self):
        """Open a folder and add all audio files"""
        folder_path = filedialog.askdirectory(title="Select Folder with Audio Files")
        
        if folder_path:
            # Stop current playback immediately
            self.stop_playback()
            # Clear existing playlist and library
            self.playlist.clear()
            for item in self.library_tree.get_children():
                self.library_tree.delete(item)
            # Scan folder and auto-play first song
            self.scan_folder_async(folder_path, auto_play=True)
    
    def add_files_to_library(self, files, auto_play=False):
        """Add multiple files to library"""
        added_count = 0
        for file_path in files:
            if self.add_song_to_library(file_path):
                added_count += 1
        
        self.update_albums_view()
        
        # Auto-play first song if requested
        if auto_play and self.playlist:
            self.after(100, lambda: self.play_song(0))
        
        if added_count > 0:
            self.show_notification(f"Added {added_count} songs to library")
    
    def scan_folder_async(self, folder_path, auto_play=False):
        """Scan folder asynchronously"""
        self.show_loading("Scanning folder...")
        
        self.is_loading = True
        self.loading_thread = threading.Thread(target=self._load_folder_thread, args=(folder_path, auto_play))
        self.loading_thread.daemon = True
        self.loading_thread.start()
    
    def _load_folder_thread(self, folder_path, auto_play):
        """Thread function for loading folder"""
        try:
            audio_extensions = {'.mp3', '.wav', '.ogg', '.flac', '.m4a', '.aac'}
            all_files = []
            
            # Scan for audio files
            for root, dirs, files in os.walk(folder_path):
                if not self.is_loading:
                    break
                for file in files:
                    if any(file.lower().endswith(ext) for ext in audio_extensions):
                        all_files.append(os.path.join(root, file))
            
            total_files = len(all_files)
            print(f"Found {total_files} audio files")
            
            # Process files in batches
            batch_size = 100
            for i in range(0, total_files, batch_size):
                if not self.is_loading:
                    break
                    
                batch = all_files[i:i + batch_size]
                for file_path in batch:
                    if not self.is_loading:
                        break
                    self.add_song_to_library(file_path)
                
                # Update progress
                progress = min(1.0, (i + len(batch)) / total_files)
                self.after(0, self._update_loading_progress, progress, i + len(batch), total_files)
            
            self.after(0, self._folder_loading_complete, total_files, auto_play)
            
        except Exception as e:
            self.after(0, lambda: self.show_error(f"Error loading folder: {str(e)}"))
            self.after(0, self.hide_loading)
    
    def add_song_to_library(self, file_path):
        """Add a song to the music library"""
        try:
            if not os.path.exists(file_path):
                return False
            
            file_size = os.path.getsize(file_path)
            if file_size < 1024:
                return False
            
            metadata = self.extract_metadata(file_path)
            if not metadata:
                return False
            
            self.playlist.append(metadata)
            self.playlist_manager.add_to_playlist("Main Playlist", file_path)
            
            self.after(0, self._add_song_to_treeview, metadata, len(self.playlist))
            
            return True
            
        except Exception as e:
            print(f"Error loading file {file_path}: {e}")
            return False
    
    def extract_metadata(self, file_path):
        """Extract metadata from audio file"""
        try:
            audio = File(file_path, easy=True)
            if not audio:
                audio = File(file_path)
            
            title = "Unknown Title"
            artist = "Unknown Artist"
            album = "Unknown Album"
            duration = "0:00"
            
            if audio is not None:
                if 'title' in audio and audio['title']:
                    title = audio['title'][0]
                else:
                    title = os.path.splitext(os.path.basename(file_path))[0]
                
                if 'artist' in audio and audio['artist']:
                    artist = audio['artist'][0]
                
                if 'album' in audio and audio['album']:
                    album = audio['album'][0]
                
                if hasattr(audio.info, 'length') and audio.info.length:
                    total_seconds = int(audio.info.length)
                    minutes = total_seconds // 60
                    seconds = total_seconds % 60
                    duration = f"{minutes}:{seconds:02d}"
            
            return {
                'path': file_path,
                'title': title[:100],
                'artist': artist[:50],
                'album': album[:50],
                'duration': duration
            }
            
        except:
            title = os.path.splitext(os.path.basename(file_path))[0]
            return {
                'path': file_path,
                'title': title[:100],
                'artist': "Unknown Artist",
                'album': "Unknown Album",
                'duration': "0:00"
            }
    
    def _add_song_to_treeview(self, song_data, index):
        """Add song to treeview from main thread"""
        try:
            self.library_tree.insert("", "end", values=(
                index, song_data['title'], song_data['artist'], song_data['album'], 
                song_data['duration'], song_data['path']
            ))
        except Exception as e:
            print(f"Error adding song to treeview: {e}")
    
    def show_loading(self, message):
        """Show loading indicator"""
        self.loading_frame.pack(fill="x", padx=15, pady=5)
        self.loading_label.configure(text=message)
        self.loading_progress.set(0)
        self.loading_progress.pack(fill="x", pady=5)
        self.loading_label.pack(pady=5)
        self.update()
    
    def _update_loading_progress(self, progress, current, total):
        """Update loading progress"""
        self.loading_progress.set(progress)
        self.loading_label.configure(text=f"Loading... {current}/{total} files")
    
    def hide_loading(self):
        """Hide loading indicator"""
        self.is_loading = False
        self.loading_frame.pack_forget()
    
    def _folder_loading_complete(self, total_files, auto_play):
        """Handle folder loading completion"""
        self.hide_loading()
        self.update_albums_view()
        
        # Auto-play first song if requested
        if auto_play and self.playlist:
            self.after(100, lambda: self.play_song(0))
        
        self.show_notification(f"🎵 Loaded {total_files} songs!")
    
    def show_notification(self, message):
        """Show a temporary notification"""
        print(f"Notification: {message}")
    
    def show_error(self, message):
        """Show error message"""
        messagebox.showerror("Error", message)
    
    def play_selected_song(self, event=None):
        """Play the selected song from library"""
        selection = self.library_tree.selection()
        if selection:
            item = selection[0]
            values = self.library_tree.item(item, 'values')
            if values and len(values) > 5:
                song_path = values[5]
                for i, song in enumerate(self.playlist):
                    if song['path'] == song_path:
                        self.play_song(i)
                        break
    
    def play_song(self, index):
        """Play song at specified index - FIXED: Visualizer and auto-playback"""
        if 0 <= index < len(self.playlist):
            # Stop current playback immediately
            self.stop_playback()
            
            self.current_index = index
            song = self.playlist[index]
            self.current_file = song['path']
            
            # Load and play media immediately
            media = self.instance.media_new(song['path'])
            self.player.set_media(media)
            self.player.play()
            self.is_playing = True
            self.play_btn.configure(text="⏸")
            
            # Update UI immediately
            self.song_title_label.configure(text=song['title'])
            self.song_artist_label.configure(text=song['artist'])
            self.current_song_label.configure(text=f"{song['title']}\nby {song['artist']}")
            
            # Reset progress and time
            self.progress_var.set(0)
            self.current_time_label.configure(text="0:00")
            
            # Load album art (will show famous music logo if no image)
            self._display_default_art()
            threading.Thread(target=self._load_album_art, args=(song['path'],), daemon=True).start()
            
            # Start visualizer immediately - FIXED
            self.after(100, lambda: self.visualizer.update_visualizer(self.player))
            
            # Update total time
            self.after(500, self._update_total_time)
    
    def _update_total_time(self):
        """Update total time label after file is loaded"""
        if self.player.get_length() > 0:
            total_time = self.player.get_length()
            total_seconds = total_time // 1000
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            self.total_time_label.configure(text=f"{minutes}:{seconds:02d}")
    
    def stop_playback(self):
        """Stop current playback safely and immediately"""
        if self.player:
            try:
                self.player.stop()
                self.is_playing = False
                self.play_btn.configure(text="▶")
                self.visualizer.stop()  # This will clear the green lines
                # Reset progress bar
                self.progress_var.set(0)
                self.current_time_label.configure(text="0:00")
                self.total_time_label.configure(text="0:00")
            except Exception as e:
                print(f"Error stopping playback: {e}")
    
    def _load_album_art(self, file_path):
        """Load album art in background thread"""
        try:
            album_art = self.image_manager.extract_album_art(file_path)
            self.after(0, self._display_album_art, album_art, file_path)
        except Exception as e:
            print(f"Error loading album art: {e}")
            self.after(0, self._display_default_art)
    
    def _display_album_art(self, album_art, file_path):
        """Display album art from main thread"""
        if self.current_file == file_path:
            self.album_art_label.configure(image=album_art, text="")
    
    def _display_default_art(self):
        """Display default album art - FIXED: Show famous music logo"""
        # Show the famous music logo when no album art is available
        self.album_art_label.configure(image=self.image_manager.default_album_art, text="")
    
    def toggle_playback(self):
        """Toggle play/pause"""
        if self.current_file:
            if self.is_playing:
                self.player.pause()
                self.is_playing = False
                self.play_btn.configure(text="▶")
                self.visualizer.stop()  # Clear visualizer when paused
            else:
                self.player.play()
                self.is_playing = True
                self.play_btn.configure(text="⏸")
                self.visualizer.update_visualizer(self.player)
    
    def next_song(self):
        """Play next song in playlist"""
        if self.playlist:
            next_index = (self.current_index + 1) % len(self.playlist)
            self.play_song(next_index)
    
    def previous_song(self):
        """Play previous song in playlist"""
        if self.playlist:
            prev_index = (self.current_index - 1) % len(self.playlist)
            self.play_song(prev_index)
    
    def backward_10s(self):
        """Go backward 10 seconds"""
        if self.player.is_playing():
            current_time = self.player.get_time()
            self.player.set_time(max(0, current_time - 10000))
    
    def forward_10s(self):
        """Go forward 10 seconds"""
        if self.player.is_playing():
            current_time = self.player.get_time()
            self.player.set_time(current_time + 10000)
    
    def set_volume(self, value):
        """Set player volume"""
        if not self.is_muted:
            self.volume = int(float(value))
            self.player.audio_set_volume(self.volume)
    
    def start_seeking(self, event):
        """Start seeking"""
        self.is_seeking = True
    
    def seek_audio(self, event):
        """Seek to position in audio"""
        if self.current_file and self.player.get_length() > 0 and self.is_seeking:
            x = event.x
            total_width = self.progress_bar.winfo_width()
            seek_percent = max(0, min(1.0, x / total_width))
            
            self.progress_var.set(seek_percent * 100)
            
            if 0 <= seek_percent <= 1:
                self.player.set_position(seek_percent)
    
    def stop_seeking(self, event):
        """Stop seeking"""
        self.is_seeking = False
    
    def search_songs(self, event):
        """Search songs in library"""
        query = self.search_entry.get().lower()
        
        for item in self.library_tree.get_children():
            self.library_tree.delete(item)
        
        for i, song in enumerate(self.playlist):
            if (query in song['title'].lower() or 
                query in song['artist'].lower() or 
                query in song['album'].lower()):
                self.library_tree.insert("", "end", values=(
                    i + 1, song['title'], song['artist'], song['album'], song['duration'], song['path']
                ))
    
    def show_playlists(self):
        """Switch to playlists tab"""
        self.tabview.set("📋 Playlists")
        self.update_playlists_view()
    
    def create_new_playlist(self):
        """Create a new playlist"""
        dialog = ctk.CTkInputDialog(text="Enter playlist name:", title="Create Playlist")
        playlist_name = dialog.get_input()
        
        if playlist_name:
            if self.playlist_manager.create_playlist(playlist_name):
                self.playlist_dropdown.configure(values=list(self.playlist_manager.playlists.keys()))
                self.playlist_var.set(playlist_name)
                self.show_notification(f"Playlist '{playlist_name}' created!")
            else:
                self.show_error("Playlist already exists!")
    
    def delete_current_playlist(self):
        """Delete the current playlist"""
        current_playlist = self.playlist_var.get()
        if current_playlist != "Main Playlist":
            if messagebox.askyesno("Confirm", f"Delete playlist '{current_playlist}'?"):
                if self.playlist_manager.delete_playlist(current_playlist):
                    self.playlist_dropdown.configure(values=list(self.playlist_manager.playlists.keys()))
                    self.playlist_var.set("Main Playlist")
                    self.load_selected_playlist("Main Playlist")
    
    def load_selected_playlist(self, choice):
        """Load songs from selected playlist"""
        self.update_playlists_view()
    
    def update_playlists_view(self):
        """Update the playlists view"""
        for item in self.playlist_tree.get_children():
            self.playlist_tree.delete(item)
        
        current_playlist = self.playlist_var.get()
        if current_playlist in self.playlist_manager.playlists:
            for song_path in self.playlist_manager.playlists[current_playlist]:
                for song in self.playlist:
                    if song['path'] == song_path:
                        self.playlist_tree.insert("", "end", values=(
                            song['title'], song['artist'], song['album'], song['duration']
                        ))
                        break
    
    def play_from_playlist(self, event):
        """Play song from playlist"""
        selection = self.playlist_tree.selection()
        if selection:
            item = selection[0]
            values = self.playlist_tree.item(item, 'values')
            if values:
                title, artist = values[0], values[1]
                for i, song in enumerate(self.playlist):
                    if song['title'] == title and song['artist'] == artist:
                        self.play_song(i)
                        break
    
    def add_to_playlist_dialog(self):
        """Add selected song to playlist"""
        selection = self.library_tree.selection()
        if selection:
            item = selection[0]
            values = self.library_tree.item(item, 'values')
            if values and len(values) > 5:
                song_path = values[5]
                
                dialog = ctk.CTkInputDialog(text="Enter playlist name:", title="Add to Playlist")
                playlist_name = dialog.get_input()
                
                if playlist_name and playlist_name in self.playlist_manager.playlists:
                    if self.playlist_manager.add_to_playlist(playlist_name, song_path):
                        self.show_notification("Song added to playlist!")
                    else:
                        self.show_notification("Song already in playlist!")
                else:
                    self.show_error("Playlist not found!")
    
    def remove_selected_song(self):
        """Remove selected song from library"""
        selection = self.library_tree.selection()
        if selection:
            item = selection[0]
            values = self.library_tree.item(item, 'values')
            if values and len(values) > 5:
                song_path = values[5]
                
                self.library_tree.delete(item)
                
                for i, song in enumerate(self.playlist):
                    if song['path'] == song_path:
                        del self.playlist[i]
                        break
                
                for playlist_name in self.playlist_manager.playlists:
                    self.playlist_manager.remove_from_playlist(playlist_name, song_path)
    
    def update_albums_view(self):
        """Update the albums view with album art thumbnails"""
        for widget in self.albums_scrollable_frame.winfo_children():
            widget.destroy()
        
        albums = {}
        for song in self.playlist:
            album_key = (song['album'], song['artist'])
            if album_key not in albums:
                albums[album_key] = []
            albums[album_key].append(song)
        
        row, col = 0, 0
        max_cols = 4
        
        for (album_name, artist), songs in albums.items():
            album_frame = self.create_album_card(album_name, artist, songs, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        for i in range(max_cols):
            self.albums_scrollable_frame.grid_columnconfigure(i, weight=1)
    
    def create_album_card(self, album_name, artist, songs, row, col):
        """Create an album card with art and info"""
        album_frame = ctk.CTkFrame(self.albums_scrollable_frame, 
                                 width=180, height=220,
                                 fg_color=MintGreenTheme.COLORS["card_bg"])
        album_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        album_frame.grid_propagate(False)
        
        # Album art - will show famous music logo if no image found
        art_image = None
        if songs:
            art_image = self.image_manager.extract_album_art(songs[0]['path'], size=(120, 120))
        
        art_frame = ctk.CTkFrame(album_frame, width=140, height=140,
                               fg_color=MintGreenTheme.COLORS["surface"])
        art_frame.pack(pady=(10, 5))
        art_frame.pack_propagate(False)
        
        # Always show the famous music logo (Spotify-style) for album art
        art_label = ctk.CTkLabel(art_frame, image=art_image, text="")
        art_label.pack(expand=True)
        
        # Album info
        info_frame = ctk.CTkFrame(album_frame, fg_color="transparent")
        info_frame.pack(fill="x", padx=10, pady=5)
        
        album_label = ctk.CTkLabel(info_frame, text=self.truncate_text(album_name, 20),
                                 font=ctk.CTkFont(weight="bold"))
        album_label.pack()
        
        artist_label = ctk.CTkLabel(info_frame, text=self.truncate_text(artist, 20),
                                  text_color=MintGreenTheme.COLORS["text_muted"])
        artist_label.pack()
        
        songs_label = ctk.CTkLabel(info_frame, text=f"{len(songs)} song{'s' if len(songs) != 1 else ''}",
                                 text_color=MintGreenTheme.COLORS["text_secondary"])
        songs_label.pack()
        
        # Bind click event
        album_frame.bind("<Button-1>", lambda e, alb=album_name, art=artist: self.play_album(alb, art))
        art_frame.bind("<Button-1>", lambda e, alb=album_name, art=artist: self.play_album(alb, art))
        
        return album_frame
    
    def truncate_text(self, text, max_length):
        """Truncate text with ellipsis if too long"""
        if len(text) > max_length:
            return text[:max_length-3] + "..."
        return text
    
    def play_album(self, album_name, artist):
        """Play the first song from selected album"""
        album_songs = [i for i, song in enumerate(self.playlist) 
                      if song['album'] == album_name and song['artist'] == artist]
        
        if album_songs:
            self.play_song(album_songs[0])
            self.show_notification(f"Playing from '{album_name}'")
    
    def toggle_timer(self):
        """Toggle study timer"""
        if self.study_timer.is_running:
            self.study_timer.pause()
            self.timer_btn.configure(text="Start Timer")
        else:
            self.study_timer.start(self.update_timer_display)
            self.timer_btn.configure(text="Pause Timer")
    
    def reset_timer(self):
        """Reset study timer"""
        self.study_timer.reset()
        self.timer_btn.configure(text="Start Timer")
        self.update_timer_display(self.study_timer.study_time, False)
    
    def update_timer_display(self, seconds, is_break, completed=False):
        """Update timer display"""
        mins = seconds // 60
        secs = seconds % 60
        time_str = f"{mins:02d}:{secs:02d}"
        
        if completed:
            self.timer_label.configure(text=time_str)
            self.show_notification(f"Time for {'a break' if not is_break else 'study'}!")
        else:
            self.timer_label.configure(text=time_str)
    
    def toggle_study_mode(self):
        """Toggle study focus mode"""
        self.study_session_active = not self.study_session_active
        if self.study_session_active:
            self.show_notification("Study mode activated! 🎯")
        else:
            self.show_notification("Study mode deactivated")
    
    def toggle_study_timer(self):
        """Show study timer controls"""
        self.show_notification("Study timer controls in sidebar ⏱️")
    
    def update_ui(self):
        """Update UI elements periodically"""
        if self.is_playing and self.player.get_length() > 0 and not self.is_seeking:
            current_time = self.player.get_time()
            total_time = self.player.get_length()
            
            if total_time > 0:
                progress = (current_time / total_time) * 100
                self.progress_var.set(progress)
                
                current_seconds = current_time // 1000
                total_seconds = total_time // 1000
                
                current_minutes = current_seconds // 60
                current_seconds = current_seconds % 60
                
                total_minutes = total_seconds // 60
                total_seconds = total_seconds % 60
                
                self.current_time_label.configure(
                    text=f"{current_minutes}:{current_seconds:02d}"
                )
                self.total_time_label.configure(
                    text=f"{total_minutes}:{total_seconds:02d}"
                )
        
        self.after(100, self.update_ui)
    
    def on_closing(self):
        """Clean up when closing application"""
        self.is_loading = False
        self.visualizer.stop()
        self.player.stop()
        self.destroy()

def main():
    """Main application entry point"""
    app = StudentMediaPlayer()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Center the window on screen
    app.update()
    app.geometry(f"+{app.winfo_screenwidth()//2 - 600}+{app.winfo_screenheight()//2 - 350}")
    
    app.mainloop()

if __name__ == "__main__":
    main()
