service ssh restart
service redis-server start
service mysql start
/etc/init.d/memcached start

celery -A twitter worker -l INFO

sudo /vagrant/hbase-2.6.0/bin/start-hbase.sh
/vagrant/hbase-2.6.0/bin/hbase-daemon.sh start thrift
