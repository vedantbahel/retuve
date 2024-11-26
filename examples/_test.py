import os
import subprocess

import pytest

BLACKLIST = ["custom_ai_and_config.py"]


# Dynamically collect scripts for testing
def collect_scripts():
    examples_dir = os.path.dirname(__file__)
    module_dir = os.path.abspath(
        os.path.join(examples_dir, "..")
    )  # Assuming your module is one level up from the examples directory

    scripts = []
    for root, _, files in os.walk(examples_dir):
        for file in files:
            if file.endswith(".py") and file not in BLACKLIST:
                scripts.append((os.path.join(root, file), module_dir))
    return scripts


# Dynamically create test functions for pytest
scripts = collect_scripts()
for i, (script_path, module_dir) in enumerate(scripts):
    # test_name should be derived from the script name
    test_name = f'test_{script_path.split("/")[-1].replace(".py", "")}'

    def create_test(script_path, module_dir):
        def test():
            try:
                env = os.environ.copy()
                env["PYTHONPATH"] = module_dir
                subprocess.run(["python", script_path], check=True, env=env)
            except subprocess.CalledProcessError as e:
                pytest.fail(
                    f"Script failed: {script_path}\nError message: {e}"
                )

        return test

    # Add the test function to the global scope
    globals()[test_name] = create_test(script_path, module_dir)
