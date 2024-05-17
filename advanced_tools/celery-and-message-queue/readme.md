# Celery and MQ

## Understanding async task?

Asynchronous task means you don't need to wait task finishing to execute you next operation/task. Normal function calls are all synchronous, which means you need to wait until the finish of the function.

In some cases, you don't want your user wait for long for the result, then you might need to set such kind into async task.

In the following cases, you need to use async task:

1. Tasks that can be distributedly processed to get a performance improvement
2. Tasks that could take a long time
3. Tasks that requires retry mechanisms, including tasks involves 3rd party components
4. Tasks that need to processed later or scheduled tasks
5. Resource racing cases, such as queuing during the request peaks

## What async you want to use in our system?

In this course, fanout_to_follower() function will be utilized into a celery managed async task.

This is because with more user in the system, DB operations such as bulk_create cannot serve everyone immediately with so many people tweeting so many tweets. Plenty of timeouts will occurs.

User don't want any waits while tweeting in this case, but it is not a severe problem for people who cannot read new tweets immediately.

## What is Message Queue and any provider?

Message Queue, also in term "broker" in Celery, is a queue managing async tasks to be executed, which preserve the task call and its parameters. This is mandatory for async tasks.

! High frequent in interview: system design.

## What does Celery do?

Celery is to help web servers & worker machines communicate with brokers. It does not rely on Django.

## What is worker machine and the whole process?

Async tasks will be executed on machines called workers. Normally worker:web server is 1:10 to 1:30 depends on task.

Normally, workers execute same piece of code as web server, but it will execute worker section of code.

1. After a worker started, it starts to listen the message queue
2. When there are tasks in MQ, workers will obtain tasks from the MQ
3. After worker finished its async task
4. Results will be write into database or return the result back to web server through internal API

Note: sometimes, due to the security concern, worker will have no access to DB.

## Environment Setup

In this project, we will directly use Redis as message queue. 

1. Install 

```shell
pip install celery
pip freeze > requirements.txt
```

2. (selective) Add these 2 lines into the ~/.bashrc

```shell
export LC_ALL=C.UTF-8
export LANG=C.UTF-8
```

3. After added requirement files in the project. https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html#using-celery-with-django. You can try the following command to test whether the celery can work.

```shell
celery -A twitter worker -l INFO
```

If you `celery` command cannot be found, you may need to add a line into `~/.bashrc`

```shell
export PATH=/where-you-install/.local/bin:$PATH
```

You will see the following after you executed the shell command

```shell
 -------------- celery@50c72a0f9185 v5.1.2 (sun-harmonics)
--- ***** ----- 
-- ******* ---- Linux-6.6.26-linuxkit-x86_64-with-Ubuntu-18.04-bionic 2024-05-17 05:57:38
- *** --- * --- 
- ** ---------- [config]
- ** ---------- .> app:         twitter:0x7f83d9f2a1d0
- ** ---------- .> transport:   redis://127.0.0.1:6379/2
- ** ---------- .> results:     disabled://
- *** --- * --- .> concurrency: 8 (prefork)
-- ******* ---- .> task events: OFF (enable -E to monitor tasks in this worker)
--- ***** ----- 
 -------------- [queues]
                .> celery           exchange=celery(direct) key=celery


[tasks]
  . twitter.celery.debug_task

[2024-05-17 05:57:39,082: INFO/MainProcess] Connected to redis://127.0.0.1:6379/2
[2024-05-17 05:57:39,085: INFO/MainProcess] mingle: searching for neighbors
[2024-05-17 05:57:40,094: INFO/MainProcess] mingle: all alone
[2024-05-17 05:57:40,101: WARNING/MainProcess] /home/ljyou001/.local/lib/python3.6/site-packages/celery/fixups/django.py:204: UserWarning: Using settings.DEBUG leads to a memory
            leak, never use this setting in production environments!
  leak, never use this setting in production environments!''')
```

In which, `transport` is the broker endpoint, `results: disabled` means we don't need to return any results now,
`concurrency` mean how many async task this instance can execute, this can be configured.

In the `task` section, it found one task which is the default task in ./twitter/celery.py

To test the debug task, you can

```shell
$ python manage.py shell
bash: warning: setlocale: LC_ALL: cannot change locale (en_US.utf-8)
Python 3.6.9 (default, Mar 10 2023, 16:46:00) 
[GCC 8.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
(InteractiveConsole)
>>> from twitter.celery import debug_task
>>> debug_task.delay()
<AsyncResult: 6ead0c8d-c202-4b15-8703-411a47ddcef5>
```

Then you will see the celery logs show:

```shell
[2024-05-17 06:07:47,060: INFO/MainProcess] Task twitter.celery.debug_task[6ead0c8d-c202-4b15-8703-411a47ddcef5] received
[2024-05-17 06:07:47,061: WARNING/ForkPoolWorker-6] Request: <Context: {'lang': 'py', 'task': 'twitter.celery.debug_task', 'id': '6ead0c8d-c202-4b15-8703-411a47ddcef5', 'shadow': None, 'eta': None, 'expires': None, 'group': None, 'group_index': None, 'retries': 0, 'timelimit': [None, None], 'root_id': '6ead0c8d-c202-4b15-8703-411a47ddcef5', 'parent_id': None, 'argsrepr': '()', 'kwargsrepr': '{}', 'origin': 'gen1631@50c72a0f9185', 'ignore_result': True, 'reply_to': '5ba57958-390f-3ade-bbd0-af1c5d39a359', 'correlation_id': '6ead0c8d-c202-4b15-8703-411a47ddcef5', 'hostname': 'celery@50c72a0f9185', 'delivery_info': {'exchange': '', 'routing_key': 'celery', 'priority': 0, 'redelivered': None}, 'args': [], 'kwargs': {}, 'is_eager': False, 'callbacks': None, 'errbacks': None, 'chain': None, 'chord': None, 'called_directly': False, '_protected': 1}>
[2024-05-17 06:07:47,061: WARNING/ForkPoolWorker-6] 
```

If you have ever changed the async tasks registered to Celery, you must restart the Celery worker server to reload the tasks.

If you started a async task in Django but did not start the Celery worker, the task will stay in the MD and wait to be executed. After one Celery worker started, the task will be executed.
