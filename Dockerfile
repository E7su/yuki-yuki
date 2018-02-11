FROM centos:centos6
LABEL maintainer Polina Azarova <etsu4296@gmail.com>

ADD requirements.txt /app/requirements.txt

# install dependencies
RUN yum update -y && yum install -y gcc zlib-devel openssl-devel mysql-devel

# install python3
RUN mkdir /build && cd /build && \
	curl -O https://www.python.org/ftp/python/3.5.2/Python-3.5.2.tgz && \
	tar xzf Python-3.5.2.tgz && cd Python-3.5.2 && \
	./configure && make && make install && \
	rm -rf /build


# get pip alongside pip3; is this better than a symlink?
RUN pip3 install --upgrade pip
RUN pip3 install -r /app/requirements.txt
RUN python3.5 -m pip install mysqlclient

WORKDIR /app

VOLUME ["/app", "/db"]

#EXPOSE 5000

#CMD ["python3.5", "/app/server.py"]
