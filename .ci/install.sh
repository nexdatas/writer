#!/usr/bin/env bash

# workaround for incomatibility of default ubuntu 16.04 and tango configuration
if [ $1 = "ubuntu16.04" ]; then
    docker exec  --user root ndts sed -i "s/\[mysqld\]/\[mysqld\]\nsql_mode = NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION/g" /etc/mysql/mysql.conf.d/mysqld.cnf
fi
if [ $1 = "ubuntu20.04" ]; then
    docker exec  --user root ndts sed -i "s/\[mysql\]/\[mysqld\]\nsql_mode = NO_ZERO_IN_DATE,NO_ENGINE_SUBSTITUTION\ncharacter_set_server=latin1\ncollation_server=latin1_swedish_ci\n\[mysql\]/g" /etc/mysql/mysql.conf.d/mysql.cnf
fi

echo "restart mysql"
if [ $1 = "debian9" ] || [ $1 = "debian10" ]; then
    # workaround for a bug in debian9, i.e. starting mysql hangs
    docker exec  --user root ndts service mysql stop
    docker exec  --user root ndts /bin/sh -c '$(service mysql start &) && sleep 30'
else
    docker exec  --user root ndts service mysql restart
fi

docker exec  --user root ndts /bin/sh -c 'export DEBIAN_FRONTEND=noninteractive; apt-get -qq update; apt-get -qq install -y   tango-db tango-common; sleep 10'
if [ $? -ne "0" ]
then
    exit -1
fi
echo "install tango servers"
docker exec  --user root ndts /bin/sh -c 'export DEBIAN_FRONTEND=noninteractive;  apt-get -qq update; apt-get -qq install -y  tango-starter tango-test liblog4j1.2-java'
if [ $? -ne "0" ]
then
    exit -1
fi

docker exec  --user root ndts service tango-db restart
docker exec  --user root ndts service tango-starter restart

if [ $2 = "2" ]; then
    echo "install python-pytango"
    docker exec  --user root ndts /bin/sh -c 'export DEBIAN_FRONTEND=noninteractive; apt-get -qq update; apt-get -qq install -y   python-pytango python-tz; apt-get -qq install -y nxsconfigserver-db python-nxstools python-setuptools; sleep 10'
else
    echo "install python3-pytango"
    if [ $1 = "ubuntu20.04" ]; then
	docker exec  --user root ndts /bin/sh -c 'export DEBIAN_FRONTEND=noninteractive; apt-get -qq update; apt-get -qq install -y   python3-tango python3-tz; apt-get -qq install -y nxsconfigserver-db python3-nxstools python3-setuptools git cython3 libhdf5-dev python3-dev; sleep 10'
	docker exec  --user root ndts /bin/sh -c 'git clone -b 2.10.x https://github.com/h5py/h5py h5py'
	docker exec  --user root ndts /bin/sh -c 'cd h5py; python3 setup.py install'

    else
	docker exec  --user root ndts /bin/sh -c 'export DEBIAN_FRONTEND=noninteractive; apt-get -qq update; apt-get -qq install -y   python3-pytango python3-tz; apt-get -qq install -y nxsconfigserver-db python3-nxstools python3-setuptools; sleep 10'
    fi
fi
if [ $? -ne "0" ]
then
    exit -1
fi

if [ $2 = "2" ]; then
    echo "install python-nxswriter"
    docker exec  --user root ndts chown -R tango:tango .
    docker exec  --user root ndts python setup.py -q install
else
    echo "install python3-nxswriter"
    docker exec  --user root ndts chown -R tango:tango .
    docker exec  --user root ndts python3 setup.py -q install
fi
if [ $? -ne "0" ]
then
    exit -1
fi
