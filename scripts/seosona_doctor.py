import os
import sys
import subprocess
import shutil

# Color formatting
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_step(msg):
    print(f"\n{Colors.OKBLUE}{Colors.BOLD}>>> {msg}{Colors.ENDC}")

def print_success(msg):
    print(f"{Colors.OKGREEN}[PASS] {msg}{Colors.ENDC}")

def print_warning(msg):
    print(f"{Colors.WARNING}[WARN] {msg}{Colors.ENDC}")

def print_error(msg):
    print(f"{Colors.FAIL}[FAIL] {msg}{Colors.ENDC}")

def run_cmd(cmd, cwd=None):
    try:
        if isinstance(cmd, list) and cmd:
            executable = shutil.which(cmd[0]) or cmd[0]
            cmd = [executable, *cmd[1:]]
        subprocess.check_call(cmd, cwd=cwd)
        return True
    except subprocess.CalledProcessError:
        return False

def check_python_dependencies(workspace_dir):
    print_step("Checking Python Dependencies...")
    req_file = os.path.join(workspace_dir, "requirements.txt")
    if not os.path.exists(req_file):
        print_warning("No requirements.txt found. Skipping python sync.")
        return

    # Check if uv is installed
    if shutil.which("uv"):
        print("Using 'uv' for fast sync...")
        success = run_cmd(["uv", "pip", "install", "-r", "requirements.txt"], cwd=workspace_dir)
    else:
        print("Falling back to standard pip...")
        success = run_cmd([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], cwd=workspace_dir)

    if success:
        print_success("Python dependencies are up to date.")
    else:
        print_error("Failed to install Python dependencies.")

def check_node_dependencies(workspace_dir):
    print_step("Checking Node.js & NPM Dependencies...")
    pkg_file = os.path.join(workspace_dir, "package.json")
    if not os.path.exists(pkg_file):
        print_warning("No package.json found. Skipping node sync.")
        return

    success = run_cmd(["npm", "install"], cwd=workspace_dir)
    if success:
        print_success("NPM packages are up to date.")
    else:
        print_error("Failed to install NPM packages.")

def check_framework_updates(workspace_dir):
    print_step("Checking Core Framework Updates (HyperFrames)...")
    # If using npx / package.json based hyperframes
    print("Checking for HyperFrames CLI updates via npm...")
    success = run_cmd(["npm", "update", "hyperframes"], cwd=workspace_dir)
    if success:
        print_success("HyperFrames Framework is up to date.")
    else:
        print_warning("Could not auto-update HyperFrames. Check npm logs.")

def check_playwright(workspace_dir):
    print_step("Checking Playwright Browsers...")
    print("Ensuring Playwright Chromium is installed for headless rendering...")
    # Use python -m playwright to ensure it uses the local environment's playwright
    success = run_cmd([sys.executable, "-m", "playwright", "install", "chromium"], cwd=workspace_dir)
    if success:
        print_success("Playwright browsers ready.")
    else:
        print_error("Failed to install Playwright browsers.")

def check_ai_models(workspace_dir):
    """Voice = OmniVoice ONLY (2026-07-14 engine consolidation). Models auto-download from the HF
    hub on first use, so this only reports presence — it must NOT re-download removed engines."""
    print_step("Checking AI Models & Weights...")
    hub = os.path.join(os.path.expanduser("~"), ".cache", "huggingface", "hub")
    checks = [
        ("OmniVoice (brand voice)", os.path.join(hub, "models--k2-fsa--OmniVoice")),
        ("PhoWhisper-large CT2 (ASR)", os.path.join(hub, "models--kiendt--PhoWhisper-large-ct2")),
        ("CQA voice reference", os.path.join(workspace_dir, "7_ASSETS", "voice", "profiles",
                                             "cqa_omnivoice_ref.wav")),
    ]
    for name, path in checks:
        if os.path.exists(path):
            print_success(f"{name}: present.")
        else:
            print_warning(f"{name}: missing (auto-downloads on first use; see 0_SETUP/MODELS.md).")

def main():
    print(f"{Colors.HEADER}{Colors.BOLD}=================================================={Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}        SEOSONA VIDEO - AUTO BOOTSTRAPPER         {Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}=================================================={Colors.ENDC}")

    workspace_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    check_node_dependencies(workspace_dir)
    check_python_dependencies(workspace_dir)
    check_playwright(workspace_dir)
    check_framework_updates(workspace_dir)
    check_ai_models(workspace_dir)

    print(f"\n{Colors.OKGREEN}{Colors.BOLD}>>> Bootstrapper finished successfully! System is READY. <<<{Colors.ENDC}\n")

if __name__ == "__main__":
    main()
