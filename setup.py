import os
import sys
import subprocess
import platform

def run_subprocess(cmd, shell=False):
    try:
        subprocess.run(cmd, check=True, shell=shell)
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {' '.join(cmd)}")
        sys.exit(1)

# Detect OS-specific script folder
scripts_dir = "Scripts" if platform.system() == "Windows" else "bin"
venv_dir = "sound_smart_env"

print("Creating virtual environment...")
run_subprocess([sys.executable, "-m", "venv", venv_dir])

# Paths to python and pip inside the virtual environment
pip_path = os.path.join(venv_dir, scripts_dir, "pip")
python_path = os.path.join(venv_dir, scripts_dir, "python")

print("Upgrading pip...")
run_subprocess([python_path, "-m", "pip", "install", "--upgrade", "pip"])

print("Installing packages from requirements.txt...")
run_subprocess([pip_path, "install", "-r", "requirements.txt"])

print("Reinstalling numpy 1.23.5 for compatibility...")
run_subprocess([pip_path, "install", "numpy==1.23.5", "--force-reinstall"])

print("Installing spaCy <3.7.0...")
run_subprocess([pip_path, "install", "spacy<3.7.0", "--prefer-binary"])

print("Downloading spaCy model: en_core_web_sm...")
run_subprocess([python_path, "-m", "spacy", "download", "en_core_web_sm"])

# Display activation instructions
activate_command = (
    f"{venv_dir}\\Scripts\\activate" if platform.system() == "Windows"
    else f"source {venv_dir}/bin/activate"
)

print("\nSetup complete!")
print(f"To activate your environment, run:\n    {activate_command}")
print("Then launch the app with:\n    python execution_app.py")


