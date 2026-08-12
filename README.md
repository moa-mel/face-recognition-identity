Create a Virtual EnvironmentA virtual environment keeps your project dependencies organized and isolated from other projects. Navigate to your preferred project directory and run:bash
         `python3 -m venv myenv`
Use code with caution.3. Activate the EnvironmentYou must activate the virtual environment 
Use code with caution.macOS / Linux:
         `source myenv/bin/activate`

after installation, if the installed package is not in the requirement.txt, then run
          `pip freeze > requirements.txt`

To generate EDGE_API_TOKEN
`python -c "import secrets; print(secrets.token_urlsafe(48))"`