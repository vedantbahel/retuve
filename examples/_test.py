import os
import subprocess

BLACKLIST = ["custom_ai_and_config.py"]


def test_example_scripts():
    examples_dir = os.path.dirname(__file__)
    module_dir = os.path.abspath(
        os.path.join(examples_dir, "..")
    )  # Assuming your module is one level up from the examples directory

    # walk through all the examples
    for root, _, files in os.walk(examples_dir):
        for file in files:
            if file.endswith(".py") and file not in BLACKLIST:
                # run the script
                script_path = os.path.join(root, file)
                try:
                    env = os.environ.copy()
                    env["PYTHONPATH"] = module_dir
                    subprocess.run(
                        ["python", script_path], check=True, env=env
                    )
                except subprocess.CalledProcessError as e:
                    print(f"Error running script: {script_path}")
                    print(f"Error message: {e}")
                    assert False
