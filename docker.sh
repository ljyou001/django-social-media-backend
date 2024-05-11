# (EXT) docker run -p 80:8000 -p 9005:22 -v ".:/vagrant" -i -t --name mineos ubuntu:18.04 bash

apt install vim python3 python3-pip wget dos2unix sudo lsb-release iproute2 

passwd root

adduser ljyou001

usermod -aG sudo ljyou001

echo 'export PATH="/home/ljyou001/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

cd /vagrant
dos2unix provision.sh
dos2unix requirements.txt
./provision.sh

sudo apt install openssh-server memcached redis

sudo vim /etc/ssh/sshd_config
# 使⽤vim打开并修改配置⽂件，找到PermitRootLogin prohibit-password 这⼀⾏，修改为PermitRootLogin
# yes ，允许通过ssh远程访问docker

sudo service ssh restart
sudo service redis-server start
/etc/init.d/memcached restart
