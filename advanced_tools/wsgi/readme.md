# WSGI 

## Understand wsgiref

wsgiref is a default server built in by Python.

This is only good for development and testing, but it does not have a good performance in production.

## WSGI and ASGI

According to Django's server document, wsgi and asgi are both production level server supported.

Wsgi is sync

Asgi is async

In WSGI, you can choose Gunicorn and uWSGI. Gunicorn is composed in Python, rather uWSGI is in C++.

In this lesson we will choose Gunicorn since it is better to understand.

Flow: Any requests will come from the client, go to the WSGI server and then forwarded to the WSGI client,
i.e. server frameworks such as Django, flask and fastapi. Then, the response will goes back in reverse.

WSGI in the middle, who is a specification that describes the communication between web servers and Python
web applications or frameworks.

# Use Gunicorn in This Project

1. In the ubuntu system, install

    ```shell
    sudo apt install gunicorn
    # or
    sudo pip install gunicorn # suggested 
    ```

2. After installed, you can see the following:

    ```shell
    which gunicorn
    > /usr/local/bin/gunicorn
    ```

3. You can run this project just like this

    This command is running in the project directory.
    You can see wsgi.py is already in the project since created.

    ```shell
    gunicorn twitter.wsgi -w 2
    ```

## After Running

Check the [document](https://docs.gunicorn.org/en/latest/run.html) for more information.

If you have `htop`, you can press `F2` > `Display options` > Enable the followings:

- Tree view
- Hide userland process threads
- Show program path

You can see the 2 `gunicorn twitter.wsgi` processes.

If you want to have more configuration and save the settings, you can use a [configuration file](https://docs.gunicorn.org/en/latest/configure.html):

1. Create a new file called `gnuicorn.conf.py` in the root and paste following

    ```python
    import multiprocessing

    bind = "127.0.0.1:8000"
    workers = multiprocessing.cpu_count() * 2 + 1
    ```

    You need to have an approprate number of workers, since too many works will take up too much resources and switching between processes will also take time.

2. According to [settings](https://docs.gunicorn.org/en/latest/settings.html) page, you can use config files by command line `c CONFIG` or `--config CONFIG`. Of course, since the default config path is `./gnuicorn.conf.py`, so we can directly

    ```shell
    gunicorn twitter.wsgi
    ```

3. After running the Gunicorn, you will see the UI is not fully loaded. By pressing `F12` > `Network` and refresh. You will see almost all the JS and CSS were not loaded. It means we need to load the static files manually in config file.

    ```shell
    $ pip show djangorestframework
    Name: djangorestframework
    Version: 3.14.0
    Summary: Web APIs for Django, made easy.
    Home-page: https://www.django-rest-framework.org/
    Author: Tom Christie
    Author-email: tom@tomchristie.com
    License: BSD
    Location: /home/ljyou001/.local/lib/python3.6/site-packages
    Requires: django, pytz
    Required-by:

    $ cd /home/ljyou001/.local/lib/python3.6/site-packages
    $ cd rest_framework/static/rest_framework/
    ```

    Then you will see the css, js and more.

    Therefore, add this file to the `twitter/settings.py`.

    ```python
    STATIC_ROOT = os.path.join(BASE_DIR, 'static/')
    ```

    And Run:

    ```shell
    python manage.py collectstatic
    ```

    Add the following information into the URLs route

    ```python
    from django.conf.urls.static import static
    from django.conf import settings
    ...
    urlpatterns = [...]++static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
    ```

    Then re-run Gunicorn, you will see everything including statics.

