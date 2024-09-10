<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/ljyou001/django-twitter-backend">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">Django Twitter Backend</h3>

  <p align="center">
    A Production Level Social Media Backend Implementation with Django
    <br />
    <a href="https://github.com/ljyou001/django-twitter-backend"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/ljyou001/django-twitter-backend/issues/new?labels=bug">Report Bug</a>
    ·
    <a href="https://github.com/ljyou001/django-twitter-backend/issues/new?labels=enhancement">Request Feature</a>
  </p>
</div>

## Overview

This project provides a system for building scalable Twitter-liked social media backend systems and implementing robust system designs using **Python**, **Django**, and various modern technologies. The system is aimed at developers who want to enhance their backend development skills or need to implement real-world system architecture. It is inspired by industrial-grade backend systems designed to handle millions of users and offers practical tools and techniques for scalable system design.

## Features

- **Backend Development with Python and Django**: Scalable web backend architecture with Django.
- **System Design Patterns**: Implementing system design principles like Push/Pull models, Denormalization, and Asynchronous Processing.
- **Cloud Integration**: Cloud deployment and scaling using AWS. In this project, we mainly use OCI for free deployment and Blob Storage.
- **Caching**: Efficient caching mechanisms using Redis and Memcached.
- **Message Queuing**: Implementing message queues using Celery & Redis to handle asynchronous tasks.
- **Database Management**: Support for SQL (MySQL) and NoSQL (HBase) databases for scalable data storage solutions.
- **RESTful APIs**: Build and manage scalable REST APIs for microservices architecture.

## Getting Started

### Built with

This system is built with the following components. Before you use, please also get prepared for:

* [![Python][Python.com]][Python-url]
* [![Django][Django.com]][Django-url]
* [![MySQL][MySQL.com]][MySQL-url]
* [![Memcached][Memcached.com]][Memcached-url]
* [![Redis][Redis.com]][Redis-url]
* [![Celery][Celery.com]][Celery-url]
* [![HBase][HBase.com]][HBase-url]
* [![AWS][AWS.com]][AWS-url]

### Installation

1. **Clone the repository**:

    ```bash
    git clone https://github.com/ljyou001/django-twitter-backend.git
    cd system-design-backend
    ```

2. **Set up the virtual environment**:

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. **Install the required dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

4. **Configure the environment variables**:

    Create a `.env` file for environment variables and provide your database and cloud credentials:

    ```bash
    SECRET_KEY=<your-secret-key>
    DATABASE_URL=mysql://user:password@localhost:3306/db_name
    AWS_ACCESS_KEY_ID=<your-access-key>
    AWS_SECRET_ACCESS_KEY=<your-secret-key>
    ```

5. **Run the project**:

    ```bash
    python manage.py migrate
    python manage.py runserver
    ```

#### Enabling Celery for Asynchronous Task Processing

Celery is used to handle background tasks in this project, such as sending notifications or processing large data. Here's how to set it up:

1. **Install Celery**:

    Celery should already be included in the `requirements.txt`. If it's missing, install it using:

    ```bash
    pip install celery
    ```

2. **Configure Celery**:

    In your Django project's `settings.py`, add the following configurations:

    ```python
    CELERY_BROKER_URL = 'redis://localhost:6379/0'  # Using Redis as the broker
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
    ```

3. **Start Celery Worker**:

    After configuring Celery, start the worker by running:

    ```bash
    celery -A your_project_name worker --loglevel=info
    ```

#### Enabling Memcached for Caching

Memcached is used for caching frequently accessed data and reducing database load.

1. **Install Memcached**:

    If Memcached is not already installed on your system, you can install it via:

    ```bash
    sudo apt-get install memcached
    ```

    Or, for macOS, use Homebrew:

    ```bash
    brew install memcached
    ```

2. **Install the Python Memcached Client**:

    Install the Python client `pymemcache`:

    ```bash
    pip install pymemcache
    ```

3. **Configure Memcached**:

    In `settings.py`, add the following configuration for Django to use Memcached:

    ```python
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
            'LOCATION': '127.0.0.1:11211',
        }
    }
    ```

4. **Start Memcached**:

    Start Memcached using:

    ```bash
    memcached -d -m 64 -p 11211 -u memcache
    ```

#### Enabling HBase with Thrift for NoSQL Database

HBase is used for managing NoSQL data, particularly for write-heavy tables.

1. **Install HBase and Thrift**:

    Install HBase and enable Thrift support:

    ```bash
    sudo apt-get install hbase thrift
    ```

2. **Start HBase and Thrift Server**:

    Once HBase is installed, start HBase and the Thrift server with the following commands:

    ```bash
    start-hbase.sh
    hbase thrift start
    ```

3. **Install the Python Thrift Client**:

    To interact with HBase via Thrift, install the Python client:

    ```bash
    pip install happybase
    ```

4. **Configure HBase in the Project**:

    In `settings.py`, configure your HBase connection:

    ```python
    import happybase

    HBASE_HOST = 'localhost'
    HBASE_PORT = 9090

    # Example connection to HBase
    connection = happybase.Connection(HBASE_HOST, port=HBASE_PORT)
    ```

## Usage

### Example: Implementing a News Feed System

You can use this system to implement a **Twitter-like News Feed**. The project includes examples of how to:
- Handle user interactions such as **Tweets**, **Friendships**, **Likes**, and **Comments**.
- Use **Redis** & **Memcached** to cache data and reduce database load.
- Implement **Message Queues** with Celery and Redis for handling background tasks like sending notifications.

### Cloud Deployment

This project includes integration with **AWS S3** for media storage and **Elastic Load Balancer** for scalability. You can deploy the application on **EC2** or **EKS** for production use.

## Contribution

Contributions are welcome! Here's how you can help:

1. Fork this repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Submit a pull request with detailed description of the feature or fix.

### Issues

If you encounter any issues or have suggestions for improvements, feel free to open an issue in the [issues tracker](https://github.com/ljyou001/django-twitter-backend/issues).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

### Maintainers

- **[Oliver Lyu](https://github.com/ljyou001)** - Lead Developer

### Acknowledge

This project is based on the course - [Python in Real World - Twitter Backend System](https://www.jiuzhang.com/course/89)

---

> This project is inspired by professional backend system designs for large-scale applications. We aim to make scalable backend architectures accessible to everyone in the open-source community.

<!-- MARKDOWN LINKS & IMAGES -->
[Python.com]: https://img.shields.io/badge/python-3776AB?style=for-the-badge&logo=python&logoColor=white
[Python-url]: https://www.python.org/
[Django.com]: https://img.shields.io/badge/django-092E20?style=for-the-badge&logo=django&logoColor=white
[Django-url]: https://www.djangoproject.com/
[MySQL.com]: https://img.shields.io/badge/mysql-4479A1?style=for-the-badge&logo=mysql&logoColor=white
[MySQL-url]: https://www.mysql.com/
[Memcached.com]: https://img.shields.io/badge/memcached-013C39?style=for-the-badge&logo=memcached&logoColor=white
[Memcached-url]: https://memcached.org/
[Redis.com]: https://img.shields.io/badge/redis-DC382D?style=for-the-badge&logo=redis&logoColor=white
[Redis-url]: https://redis.io/
[Celery.com]: https://img.shields.io/badge/celery-37814A?style=for-the-badge&logo=celery&logoColor=white
[Celery-url]: https://docs.celeryproject.org/
[HBase.com]: https://img.shields.io/badge/hbase-FF7F00?style=for-the-badge&logo=apache-hbase&logoColor=white
[HBase-url]: https://hbase.apache.org/
[AWS.com]: https://img.shields.io/badge/AWS-232F3E?style=for-the-badge&logo=amazon-aws&logoColor=white
[AWS-url]: https://aws.amazon.com/
