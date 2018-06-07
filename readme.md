Kassensystem
=

Currenty this system is still under heavy development. Use in production environments at your own risk.

Installation
-
It's a standard django project.
1. install requirements
2. install bower dependencies in static folder
3. ```cp config/config.default.ini config/config.ini```
4. edit config
5. if you want to set the clock through web interface start ```rootSystemDeamon.py``` with root permissions as a service.
6. migrate database ```python3 manage.py migrate```
7. generate initial user ```python3 managa.py createsuperuser```