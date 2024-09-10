# Nginx: Reverse Proxy and Static Proxy

## Originally

Originally, all the requests are forwarded by WSGI servers.

Now, we want to have a Nginx server before the WSGI server, then goes to WSGI client(Django).

## Install

Run:

```shell
sudo apt install nginx
sudo service nginx start # <- If in docker
```

Then install `ranger`

```shell
sudo pip install ranger-fm
```

## Configuring

After installation, you can go to the nginx directory to make some configs

```shell
cd /etc/nginx/
ranger
cd sites-available/
sudo vi django-twitter.com
```

Then compose the config file

```code
server {
    charset utf-8;
    listen 80;
    server_name YOUR_IP;
    location /static {
        alias /vagrant/static/;
    }
    location /media {
        alias /vagrant/media;
    }
    location / {
        proxy_set_header Host $host;
        proxy_pass http://unix:/tmp/YOUR_IP.socket;
    }
}
```

Run

```shell
sudo ln -s /etc/nginx/sites-available/django-twitter.com /etc/nginx/sites-enabled
```

Then you will see the site in `ranger`, restart `nginx` by

```shell
sudo service nginx reload
```
