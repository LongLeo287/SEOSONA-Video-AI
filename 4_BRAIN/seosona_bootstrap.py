import os
import sys
import subprocess
import urllib.request
import zipfile
import shutil

def check_and_install_ffmpeg(project_root):
    """
    Check and install FFmpeg when it is not available on PATH.
    """
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    # Prefer the bundled node ffmpeg-static (what the render already uses) — no separate ffmpeg/ needed.
    ffstatic = os.path.join(project_root, "node_modules", "ffmpeg-static")
    if os.path.exists(os.path.join(ffstatic, "ffmpeg.exe")) or os.path.exists(os.path.join(ffstatic, "ffmpeg")):
        os.environ["PATH"] = ffstatic + os.pathsep + os.environ.get("PATH", "")
        return

    ffmpeg_dir = os.path.join(project_root, "ffmpeg")
    ffmpeg_bin = os.path.join(ffmpeg_dir, "ffmpeg-8.1.1-essentials_build", "bin")
    
    if os.path.exists(os.path.join(ffmpeg_bin, "ffmpeg.exe")):
        os.environ["PATH"] = ffmpeg_bin + os.pathsep + os.environ["PATH"]
        return

    print("[BOOTSTRAP] FFmpeg not found. Downloading a local FFmpeg build...")
    os.makedirs(ffmpeg_dir, exist_ok=True)
    zip_path = os.path.join(ffmpeg_dir, "ffmpeg.zip")
    
    try:
        # per-call timeout (not socket.setdefaulttimeout, which would globally cap later LLM/researcher
        # sockets) — a stalled fetch must not hang startup forever.
        with urllib.request.urlopen(
                "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip", timeout=60) as _r, \
                open(zip_path, "wb") as _f:
            shutil.copyfileobj(_r, _f)
        print("[BOOTSTRAP] Extracting FFmpeg...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(ffmpeg_dir)
        os.remove(zip_path)
        
        # Determine actual extracted folder name
        extracted_folders = [f for f in os.listdir(ffmpeg_dir) if os.path.isdir(os.path.join(ffmpeg_dir, f))]
        if extracted_folders:
            ffmpeg_bin = os.path.join(ffmpeg_dir, extracted_folders[0], "bin")
            os.environ["PATH"] = ffmpeg_bin + os.pathsep + os.environ["PATH"]
            print("[BOOTSTRAP] FFmpeg is ready.")
    except Exception as e:
        print(f"[BOOTSTRAP] FFmpeg setup failed: {e}")

def check_npm_packages(project_root):
    """
    Check and update required NPM packages.
    """
    print("[BOOTSTRAP] Checking HyperFrames package...")
    npx_exe = shutil.which("npx") or shutil.which("npx.cmd")
    if not npx_exe:
        print("[BOOTSTRAP] npx executable not found; HyperFrames render may fail.")
        return
    print("[BOOTSTRAP] HyperFrames can be launched via npx.")

def check_python_packages():
    """
    Check and install missing Python packages.
    """
    required_packages = {
        "moviepy": "moviepy",
        "playwright": "playwright",
        "yaml": "PyYAML"
    }
    
    missing = []
    for module, pkg in required_packages.items():
        try:
            __import__(module)
        except ImportError:
            missing.append(pkg)
            
    if missing:
        print(f"[BOOTSTRAP] Missing Python packages detected: {missing}. Installing...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", *missing], check=True)
        except Exception as e:
            print(f"[BOOTSTRAP] Python package installation failed: {e}")
            
    # Always try to install playwright browsers if playwright was just installed
    if "playwright" in missing:
        print("[BOOTSTRAP] Installing Chromium for Playwright...")
        try:
            subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
        except Exception as e:
            print(f"[BOOTSTRAP] Chromium installation failed: {e}")

def bootstrap():
    """
    Entry point for startup dependency checks.
    Verifies FFmpeg, NPM packages, and Python packages.
    """
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    check_python_packages()
    check_and_install_ffmpeg(project_root)
    check_npm_packages(project_root)

if __name__ == "__main__":
    bootstrap()
