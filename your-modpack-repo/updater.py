import os
import hashlib
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import urllib.request
import platform
from datetime import datetime
import sv_ttk  # For modern themes
from typing import Optional, Callable
from PIL import Image, ImageTk  # For icon handling

# ========================
# Configuration Management
# ========================
def get_config_dir() -> str:
    """Get OS-specific config directory."""
    system = platform.system()
    if system == "Windows":
        return os.path.join(os.environ['APPDATA'], "ModpackUpdater")
    elif system == "Darwin":  # macOS
        return os.path.expanduser("~/Library/Application Support/ModpackUpdater")
    return os.path.expanduser("~/.config/ModpackUpdater")  # Linux/Unix

CONFIG_PATH = os.path.join(get_config_dir(), "config.json")
GITHUB_REPO = "you-cant-run/minecraft-modpack-updater"
GITHUB_BRANCH = "main"
MANIFEST_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}/{GITHUB_BRANCH}/manifest.json"

# ==================
# Core Updater Class
# ==================
class ModUpdater:
    def __init__(self):
        self.config = self._load_config()
    
    def _load_config(self) -> dict:
        """Load or initialize configuration."""
        os.makedirs(get_config_dir(), exist_ok=True)
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {"mod_folder": "", "remove_old": True, "theme": "dark"}
    
    def save_config(self):
        """Persist configuration to disk."""
        with open(CONFIG_PATH, 'w') as f:
            json.dump(self.config, f)
    
    def calculate_sha256(self, filepath: str) -> Optional[str]:
        """Compute SHA256 hash of a file."""
        if not os.path.exists(filepath):
            return None
        
        sha256 = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def download_file(self, url: str, dest: str, progress_callback: Callable[[float], None]) -> bool:
        """Download with progress tracking."""
        try:
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            headers = {'User-Agent': 'ModpackUpdater/1.0'}
            req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req) as response, open(dest, 'wb') as f:
                total_size = int(response.getheader('Content-Length', 0))
                downloaded = 0
                
                while True:
                    chunk = response.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        progress_callback(downloaded / total_size * 100)
                        
            return True
        except Exception as e:
            return False

# ========================
# Enhanced GUI Application
# ========================
class ModUpdaterApp:
    def __init__(self):
        self.updater = ModUpdater()
        self.root = tk.Tk()
        self._setup_window()
        self._create_widgets()
        self._setup_menu()
        self._apply_theme()
        
        # Initial update
        if self.updater.config.get("mod_folder"):
            self.log(f"Mod folder: {self.updater.config['mod_folder']}")
        self.update_status("Ready")
        
        self.root.mainloop()
    
    def _setup_window(self):
        """Configure main window properties."""
        self.root.title("Minecraft Modpack Updater")
        self.root.geometry("900x650")
        self.root.minsize(800, 600)
        self._set_window_icon()
    
    def _set_window_icon(self):
        """Load icons from assets folder with cross-platform support"""
        # Determine the base path (works for both development and PyInstaller)
        try:
            base_path = sys._MEIPASS  # PyInstaller bundle
        except AttributeError:
            base_path = os.path.dirname(os.path.abspath(__file__))

        # Try ICO first (Windows/macOS)
        ico_path = os.path.join(base_path, "assets", "fish.ico")
        if os.path.exists(ico_path):
            try:
                self.root.iconbitmap(ico_path)
                return
            except Exception as e:
                print(f"ICO load failed: {e}")

        # Fallback to PNG (Linux)
        png_path = os.path.join(base_path, "assets", "fish1.png")
        if os.path.exists(png_path):
            try:
                img = Image.open(png_path)
                photo = ImageTk.PhotoImage(img)
                self.root.iconphoto(True, photo)
            except Exception as e:
                print(f"PNG load failed: {e}")
    
    def _get_resource_path(self, relative_path):
        """Get path for bundled resources (works with PyInstaller)"""
        try:
            base_path = sys._MEIPASS
        except AttributeError:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)
    
    def _create_widgets(self):
        """Create all GUI components."""
        # Main layout
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header
        self.header = ttk.Frame(self.main_frame)
        self.header.pack(fill="x", pady=(0, 10))
        
        ttk.Label(self.header, 
                text="Modpack Updater", 
                font=("Segoe UI", 14, "bold")).pack(side="left")
        
        # Action buttons
        btn_frame = ttk.Frame(self.header)
        btn_frame.pack(side="right")
        
        ttk.Button(btn_frame, 
                 text="🔄 Update", 
                 command=self.run_update,
                 style="Accent.TButton").pack(side="left", padx=5)
        
        ttk.Button(btn_frame, 
                 text="📂 Set Folder", 
                 command=self.set_mod_folder).pack(side="left", padx=5)
        
        # Settings panel
        self.settings_frame = ttk.LabelFrame(self.main_frame, text="Settings", padding=10)
        self.settings_frame.pack(fill="x", pady=(0, 10))
        
        self.remove_old_var = tk.BooleanVar(value=self.updater.config.get("remove_old", True))
        ttk.Checkbutton(self.settings_frame, 
                      text="Remove outdated mods",
                      variable=self.remove_old_var).pack(anchor="w")
        
        # Theme switcher
        self.theme_var = tk.StringVar(value=self.updater.config.get("theme", "dark"))
        ttk.OptionMenu(self.settings_frame, 
                     self.theme_var,
                     self.theme_var.get(),
                     "dark",
                     "light",
                     command=self.change_theme).pack(anchor="w", pady=(5, 0))
        
        # Log console
        self.log_console = scrolledtext.ScrolledText(self.main_frame,
                                                  wrap=tk.WORD,
                                                  font=("Consolas", 10),
                                                  state="disabled")
        self.log_console.pack(fill="both", expand=True)
        
        # Progress bar (initially hidden)
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(self.main_frame,
                                      variable=self.progress_var,
                                      maximum=100)
        
        # Status bar
        self.status_frame = ttk.Frame(self.main_frame)
        self.status_frame.pack(fill="x", pady=(5, 0))
        
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(self.status_frame,
                textvariable=self.status_var,
                relief="sunken",
                anchor="w").pack(fill="x")
    
    def _setup_menu(self):
        """Create menu bar."""
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Set Mod Folder", command=self.set_mod_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def _apply_theme(self):
        """Apply the selected theme."""
        sv_ttk.set_theme(self.theme_var.get())
    
    # ======================
    # Core Functionality
    # ======================
    def set_mod_folder(self):
        """Set the mod folder location."""
        folder = filedialog.askdirectory(
            title="Select Minecraft Mods Folder",
            initialdir=self.updater.config.get("mod_folder", os.path.expanduser("~"))
        )
        
        if folder:
            self.updater.config["mod_folder"] = folder
            self.updater.save_config()
            self.log(f"Mod folder set to: {folder}")
            self.update_status(f"Mods will be saved to: {folder}")
    
    def run_update(self):
        """Execute the update process."""
        if not self.updater.config.get("mod_folder"):
            messagebox.showerror("Error", "Please set a mod folder first!")
            return
        
        # Update settings from UI
        self.updater.config["remove_old"] = self.remove_old_var.get()
        self.updater.config["theme"] = self.theme_var.get()
        self.updater.save_config()
        
        # Prepare UI
        self.log("\n=== Starting Update ===")
        self.update_status("Connecting...")
        self.progress.pack(fill="x", pady=(5, 0))
        self.progress_var.set(0)
        self.root.update_idletasks()
        
        try:
            # Download manifest
            self.log("Fetching manifest...")
            with urllib.request.urlopen(MANIFEST_URL) as response:
                manifest = json.load(response)
            
            mods = manifest.get("modpack", {}).get("mods", [])
            if not mods:
                raise ValueError("No mods found in manifest!")
            
            mod_folder = self.updater.config["mod_folder"]
            os.makedirs(mod_folder, exist_ok=True)
            
            # Track files for cleanup
            existing_files = set(os.listdir(mod_folder))
            files_in_manifest = set()
            success = errors = 0
            
            # Process each mod
            for mod in mods:
                filename = mod.get("file", "").split("/")[-1]
                if not filename:
                    continue
                    
                files_in_manifest.add(filename)
                filepath = os.path.join(mod_folder, filename)
                
                # Hash verification
                if os.path.exists(filepath):
                    local_hash = self.updater.calculate_sha256(filepath)
                    if local_hash == mod.get("sha256"):
                        self.log(f"✅ {filename} (up-to-date)")
                        success += 1
                        continue
                
                # Download new version
                mod_url = mod.get("url") or f"https://raw.githubusercontent.com/{GITHUB_REPO}/{GITHUB_BRANCH}/{mod['file']}"
                self.log(f"⬇️ Downloading {filename}...")
                self.update_status(f"Downloading {filename}...")
                
                def progress_callback(pct):
                    self.progress_var.set(pct)
                    self.root.update_idletasks()
                
                if self.updater.download_file(mod_url, filepath, progress_callback):
                    new_hash = self.updater.calculate_sha256(filepath)
                    if "sha256" in mod and new_hash != mod["sha256"]:
                        self.log(f"⚠️ Hash mismatch for {filename}!")
                        errors += 1
                    else:
                        self.log(f"✅ {filename}")
                        success += 1
                else:
                    errors += 1
                self.progress_var.set(0)
            
            # Cleanup old files
            if self.updater.config.get("remove_old", True):
                removed = 0
                for file in existing_files - files_in_manifest:
                    try:
                        os.remove(os.path.join(mod_folder, file))
                        self.log(f"🗑️ Removed: {file}")
                        removed += 1
                    except:
                        self.log(f"⚠️ Failed to remove: {file}")
                if removed:
                    self.log(f"Removed {removed} outdated mod(s)")
            
            # Final status
            self.log("\n=== Update Complete ===")
            self.log(f"Successful: {success} | Failed: {errors}")
            self.update_status(f"Updated {success} mods" + (f" ({errors} errors)" if errors else ""))
            
        except Exception as e:
            self.log(f"\n💥 Error: {str(e)}")
            self.update_status("Update failed!")
            messagebox.showerror("Update Error", str(e))
        finally:
            self.progress.pack_forget()
    
    def show_about(self):
        """Show about dialog."""
        about_text = f"""
        Minecraft Modpack Updater
        Version: 1.0
        Author: Your Name
        
        Features:
        - Automatic mod updates
        - SHA256 verification
        - Dark/Light theme support
        """
        messagebox.showinfo("About", about_text.strip())
    
    # ======================
    # UI Helper Methods
    # ======================
    def log(self, message: str):
        """Add timestamped message to log console."""
        timestamp = datetime.now().strftime("[%H:%M:%S]")
        self.log_console.config(state="normal")
        self.log_console.insert("end", f"{timestamp} {message}\n")
        self.log_console.see("end")
        self.log_console.config(state="disabled")
        self.root.update_idletasks()
    
    def update_status(self, message: str):
        """Update the status bar."""
        self.status_var.set(message)
        self.root.update_idletasks()
    
    def change_theme(self, theme_name: str):
        """Switch between dark/light themes."""
        sv_ttk.set_theme(theme_name)
        self.updater.config["theme"] = theme_name
        self.updater.save_config()

if __name__ == "__main__":
    import sys  # For resource path resolution
    app = ModUpdaterApp()
