# calorie_counter
Build simple web to estimate Calories based on the uploaded image

# Prepare Environment
Here is the step-by-step guide to creating a virtual environment and installing your requirements.txt into it.

Think of a Virtual Environment (venv) as a separate, isolated "toolbox" just for this specific project. It prevents the libraries for this app (like google-generativeai) from clashing with other Python projects on your computer.

Step 1: Create the Virtual Environment
python -m venv venv

Step 2: Activate the Virtual EnvironmentBefore you install anything, you must "turn on" the environment. The command depends on your operating system:
Operating System,Command to Run
Windows (Command Prompt),venv\Scripts\activate
Windows (PowerShell),venv\Scripts\Activate.ps1
Mac / Linux,source venv/bin/activate

Step 3: Install Your Requirements
Now that the environment is active, any install command will go strictly into that venv folder, not your main computer.
pip install -r requirements.txt

Step 4: Verify Installation
To double-check that the libraries are installed inside the virtual environment, run:
pip list