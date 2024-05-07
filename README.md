# fatmug_assesment
This is a dedicated file to provide instructions on how to execute the code and validate the fumctionality.
First navigate to requirements.txt and install them(Try to keep all the files and folder inside one parent directory)
Install dependencies by: pip install -r requirements.txt
perform: python manage.py makemigrations then python manage.py migrate
Now refer to: [guide](https://docs.google.com/document/d/1MA_3U-5JInVEFpXGE4l31DspcjQlVTPMg3wcCPlz3og/edit?usp=drive_link)
**Note: Project uses the signals for real time updates on th eperformance metrices.(see signals.py)**
For the optional model HistoryPerformance, we have overriden the save method of vendor as it was not specified whether to create a separate endpoint for it or not.
