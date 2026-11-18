import sys
import subprocess

museum = sys.argv[1]
scripts = [
    [f"harvest_{museum}.py"],
    ["normalize.py", f"{museum}"],
    ["load.py", f"{museum}"],
    ["health.py"],
]

for script_cmd in scripts:
    script_name = script_cmd[0]
    print(f"Starting {script_name}")
    try:
        subprocess.run([sys.executable] + script_cmd, check=True)
        print(f"Finished {script_name}\n")
    except subprocess.CalledProcessError as e:
        print(f"Error: {script_name} failed with exit code {e.returncode}. Stopping.")
        break
    except FileNotFoundError:
        print(f"Error: Could not find {script_name}.")
        break
