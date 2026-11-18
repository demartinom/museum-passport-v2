import sys
import subprocess

museums = ["met", "princeton"]
failed = False

for museum in museums:
    scripts = [
        [f"harvest_{museum}.py"],
        ["normalize.py", museum],
        ["load.py", museum],
    ]

    for script_cmd in scripts:
        script_name = script_cmd[0]
        print(f"Starting {script_name}")
        try:
            subprocess.run([sys.executable] + script_cmd, check=True)
            print(f"Finished {script_name}\n")
        except subprocess.CalledProcessError as e:
            print(
                f"Error: {script_name} failed with exit code {e.returncode}. Moving on to next museum."
            )
            failed = True
            break
        except FileNotFoundError:
            print(f"Error: Could not find {script_name}.")
            failed = True
            break

try:
    subprocess.run([sys.executable, "health.py"], check=True)
except subprocess.CalledProcessError as e:
    print(f"Error: health.py failed with exit code {e.returncode}. Stopping")
    sys.exit(1)

if failed:
    sys.exit(1)
