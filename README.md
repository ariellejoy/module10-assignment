# How to run tests locally 
In order to run tests, a user will need to ensure that they are running the project in a virtual environment and all requirements + dependencies have been added. 

To add a virtual environment, enter the following in the terminal: 
FOR MAC (what I used)-
```
python3 -m venv .venv
```
FOR WINDOWS-
```
python -m venv .venv 
```

*Interesting note: as I was running through the assignment, I generally would run into issues with getting my requirements file to install as expected. A workaround that I used was running python**3.12** instead of python3 when adding a virtual environment to start off with*

To run the virtual environment: 
FOR MAC (what I used)- 
```
source venv/bin/activate
```
FOR WINDOWS-
``` 
venv\Scripts\activate.bat 
```

To install necessary dependencies, run the following in the terminal: 
```
pip install -r requirements.txt
```
*Note: I ran into a warning that pip will need to be upgraded. This was easy to resolve by running the following in the terminal:* 
```
pip install --upgrade pip 
```

To run the unit tests, enter the following in the terminal: 
```
pytest
```
This command will run your test files, which will return a complete output with successful tests, as well as any errors/failures that come up. Traceback calls are also helpful to determine how to fix these errors and failed tests. 

A user can also check test coverage through the pytest output! A table will be displayed that shows the overall coverage and what lines do not have any tests covering them. You can better view the code by opening the **index.html** file from the htmlcov folder in the browser.

## Link to Docker Hub: 
https://hub.docker.com/r/ariellejoy/module10-assignment
