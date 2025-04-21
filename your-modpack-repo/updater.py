import os
import hashlib
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import urllib.request
import platform
from datetime import datetime
import sv_ttk
from typing import Optional, Callable, Tuple
from PIL import Image, ImageTk

# ========================
# Configuration Management
# ========================
def get_config_dir() -> str:
    system = platform.system()
    if system == "Windows":
        return os.path.join(os.environ['APPDATA'], "ModpackUpdater")
    elif system == "Darwin":
        return os.path.expanduser("~/Library/Application Support/ModpackUpdater")
    return os.path.expanduser("~/.config/ModpackUpdater")

CONFIG_PATH = os.path.join(get_config_dir(), "config.json")

# !! CONFIGURE THESE URLS TO MATCH YOUR REPOSITORY !!
MANIFEST_URL = "https://raw.githubusercontent.com/you-cant-run/minecraft-modpack-updater/main/manifest.json"
MOD_FOLDER_URL = "https://raw.githubusercontent.com/you-cant-run/minecraft-modpack-updater/main/your-modpack-repo/mods/"
CONFIG_FOLDER_URL = "https://raw.githubusercontent.com/you-cant-run/minecraft-modpack-updater/main/your-modpack-repo/config/"

# ==================
# Core Updater Class
# ==================
class ModUpdater:
    def __init__(self):
        self.config = self._load_config()
    
    def _load_config(self) -> dict:
        os.makedirs(get_config_dir(), exist_ok=True)
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {"mod_folder": "", "remove_old": True, "theme": "dark"}
    
    def save_config(self):
        with open(CONFIG_PATH, 'w') as f:
            json.dump(self.config, f)
    
    def calculate_sha256(self, filepath: str) -> Optional[str]:
        if not os.path.exists(filepath):
            return None
        sha256 = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def download_file(self, url: str, dest: str, progress_callback: Callable[[float], None]) -> Tuple[bool, str]:
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
            return True, None
        except Exception as e:
            return False, str(e)

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
        
        if self.updater.config.get("mod_folder"):
            self.log(f"Mod folder: {self.updater.config['mod_folder']}")
        self.update_status("Ready")
        self.root.mainloop()

    def _setup_window(self):
        self.root.title("Minecraft Modpack Updater")
        self.root.geometry("900x650")
        self.root.minsize(800, 600)
        self._set_window_icon()

    def _set_window_icon(self):
        try:
            base_path = sys._MEIPASS
        except AttributeError:
            base_path = os.path.dirname(os.path.abspath(__file__))

        ico_path = os.path.join(base_path, "assets", "fish.ico")
        if os.path.exists(ico_path):
            try:
                self.root.iconbitmap(ico_path)
                return
            except Exception as e:
                print(f"ICO load failed: {e}")

        png_path = os.path.join(base_path, "assets", "fish1.png")
        if os.path.exists(png_path):
            try:
                img = Image.open(png_path)
                photo = ImageTk.PhotoImage(img)
                self.root.iconphoto(True, photo)
            except Exception as e:
                print(f"PNG load failed: {e}")

    def _create_widgets(self):
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.header = ttk.Frame(self.main_frame)
        self.header.pack(fill="x", pady=(0, 10))
        
        ttk.Label(self.header, 
                text="Modpack Updater", 
                font=("Segoe UI", 14, "bold")).pack(side="left")
        
        btn_frame = ttk.Frame(self.header)
        btn_frame.pack(side="right")
        
        ttk.Button(btn_frame, 
                 text="🔄 Update", 
                 command=self.run_update,
                 style="Accent.TButton").pack(side="left", padx=5)
        
        ttk.Button(btn_frame, 
                 text="📂 Set Folder", 
                 command=self.set_mod_folder).pack(side="left", padx=5)
        
        self.settings_frame = ttk.LabelFrame(self.main_frame, text="Settings", padding=10)
        self.settings_frame.pack(fill="x", pady=(0, 10))
        
        self.remove_old_var = tk.BooleanVar(value=self.updater.config.get("remove_old", True))
        ttk.Checkbutton(self.settings_frame, 
                      text="Remove outdated mods",
                      variable=self.remove_old_var).pack(anchor="w")
        
        self.theme_var = tk.StringVar(value=self.updater.config.get("theme", "dark"))
        ttk.OptionMenu(self.settings_frame, 
                     self.theme_var,
                     self.theme_var.get(),
                     "dark",
                     "light",
                     command=self.change_theme).pack(anchor="w", pady=(5, 0))
        
        self.log_console = scrolledtext.ScrolledText(self.main_frame,
                                                  wrap=tk.WORD,
                                                  font=("Consolas", 10),
                                                  state="disabled")
        self.log_console.pack(fill="both", expand=True)
        
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(self.main_frame,
                                      variable=self.progress_var,
                                      maximum=100)
        
        self.status_frame = ttk.Frame(self.main_frame)
        self.status_frame.pack(fill="x", pady=(5, 0))
        
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(self.status_frame,
                textvariable=self.status_var,
                relief="sunken",
                anchor="w").pack(fill="x")

    def _setup_menu(self):
        menubar = tk.Menu(self.root)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Set Mod Folder", command=self.set_mod_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)

    def _apply_theme(self):
        sv_ttk.set_theme(self.theme_var.get())

    def set_mod_folder(self):
        folder = filedialog.askdirectory(
            title="Select Minecraft Folder",
            initialdir=self.updater.config.get("mod_folder", os.path.expanduser("~"))
        )
        
        if folder:
            self.updater.config["mod_folder"] = folder
            self.updater.save_config()
            self.log(f"Mod folder set to: {folder}")
            self.update_status(f"Root folder: {folder}")

    def run_update(self):
        if not self.updater.config.get("mod_folder"):
            messagebox.showerror("Error", "Please set a mod folder first!")
            return
        
        try:
            self.log("\n=== Configuration URLs ===")
            self.log(f"Manifest URL: {MANIFEST_URL}")
            self.log(f"Mod Folder URL: {MOD_FOLDER_URL}")
            self.log(f"Config Folder URL: {CONFIG_FOLDER_URL}")
            
            # Fetch manifest
            self.log("\nFetching manifest...")
            with urllib.request.urlopen(MANIFEST_URL) as response:
                manifest = json.load(response)
            
            modpack = manifest.get("modpack", {})
            mods = modpack.get("mods", [])
            configs = modpack.get("configs", [])
            
            if not mods and not configs:
                raise ValueError("No mods or configs found in manifest!")

            mod_folder = self.updater.config["mod_folder"]
            os.makedirs(mod_folder, exist_ok=True)
            
            files_in_manifest = set()
            existing_files = set()
            success = errors = 0

            # Process mods
            for mod in mods:
                rel_path = mod.get("file", "")
                if not rel_path:
                    continue
                
                filename = os.path.basename(rel_path)
                files_in_manifest.add(os.path.join("mods", filename))
                dest_path = os.path.join(mod_folder, "mods", filename)
                file_url = f"{MOD_FOLDER_URL}{filename}"
                
                self.log(f"\nProcessing mod: {filename}")
                self.log(f"Download URL: {file_url}")

                if os.path.exists(dest_path):
                    local_hash = self.updater.calculate_sha256(dest_path)
                    if local_hash == mod.get("sha256"):
                        self.log("File is up-to-date")
                        success += 1
                        continue

                self._download_file(file_url, dest_path, mod)
                success += 1

            # Process configs
            for config in configs:
                rel_path = config.get("path", "")
                if not rel_path:
                    continue
                
                filename = os.path.basename(rel_path)
                files_in_manifest.add(os.path.join("config", filename))
                dest_path = os.path.join(mod_folder, "config", filename)
                file_url = f"{CONFIG_FOLDER_URL}{filename}"
                
                self.log(f"\nProcessing config: {filename}")
                self.log(f"Download URL: {file_url}")

                if os.path.exists(dest_path):
                    local_hash = self.updater.calculate_sha256(dest_path)
                    if local_hash == config.get("sha256"):
                        self.log("File is up-to-date")
                        success += 1
                        continue

                self._download_file(file_url, dest_path, config)
                success += 1

            # Cleanup old files
            if self.updater.config.get("remove_old", True):
                self._cleanup_files(mod_folder, files_in_manifest, existing_files)

            self.log("\n=== Update Complete ===")
            self.log(f"Successful: {success} | Failed: {errors}")
            self.update_status(f"Updated {success} files" + (f" ({errors} errors)" if errors else ""))

        except urllib.error.HTTPError as e:
            self.log(f"\n💥 HTTP Error {e.code}: {e.reason}")
            self.log(f"Verify URL: {e.url}")
            messagebox.showerror("HTTP Error", f"{e.code} {e.reason}\nCheck log for details")
        except Exception as e:
            self.log(f"\n💥 Unexpected Error: {str(e)}")
            messagebox.showerror("Error", str(e))
        
        finally:
            self.progress.pack_forget()

    def _download_file(self, url: str, dest: str, entry: dict):
        self.progress_var.set(0)
        self.progress.pack(fill="x", pady=(5, 0))
        
        def progress_callback(pct):
            self.progress_var.set(pct)
            self.root.update_idletasks()

        download_ok, error_msg = self.updater.download_file(url, dest, progress_callback)
        
        if download_ok:
            new_hash = self.updater.calculate_sha256(dest)
            if "sha256" in entry and new_hash != entry["sha256"]:
                self.log(f"⚠️ Hash mismatch! Expected: {entry['sha256']} | Got: {new_hash}")
                return False
            return True
        else:
            self.log(f"❌ Download failed: {error_msg}")
            return False

    def _cleanup_files(self, mod_folder: str, files_in_manifest: set, existing_files: set):
        removed = 0
        for file in existing_files - files_in_manifest:
            full_path = os.path.join(mod_folder, file)
            try:
                os.remove(full_path)
                self.log(f"🗑️ Removed: {file}")
                removed += 1
            except Exception as e:
                self.log(f"⚠️ Failed to remove {file}: {str(e)}")
        if removed:
            self.log(f"Removed {removed} outdated files")

    def show_about(self):
        about_text = """
        Minecraft Modpack Updater
        Version: 2.1
        Features:
        - Separate URL configuration
        - Enhanced error logging
        - Hash verification
        - Automatic cleanup
        """
        messagebox.showinfo("About", about_text.strip())

    def log(self, message: str):
        timestamp = datetime.now().strftime("[%H:%M:%S]")
        self.log_console.config(state="normal")
        self.log_console.insert("end", f"{timestamp} {message}\n")
        self.log_console.see("end")
        self.log_console.config(state="disabled")
        self.root.update_idletasks()

    def update_status(self, message: str):
        self.status_var.set(message)
        self.root.update_idletasks()

    def change_theme(self, theme_name: str):
        sv_ttk.set_theme(theme_name)
        self.updater.config["theme"] = theme_name
        self.updater.save_config()

if __name__ == "__main__":
    import sys
    app = ModUpdaterApp()
