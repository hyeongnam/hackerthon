django 설치

$ pip install django



프로젝트 생성

$ django-admin startproject telegram .



앱생성

$ python manage.py startapp bus



테스트

$ python manage.py runserver



$ pip install python-decouple 

$ pip install requests

$ pip install bs4



```python
#...
INSTALLED_APPS = [
    'bus',
    #...
]
#...
LANGUAGE_CODE = 'ko-kr' 
TIME_ZONE = 'Asia/Seoul'
```





$ python manage.py makemigrations

$ python manage.py migrate