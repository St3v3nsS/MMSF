FROM openjdk:7u221-slim-jessie
RUN sed -i -e 's/deb.debian.org/archive.debian.org/g' \
           -e 's|security.debian.org|archive.debian.org/|g' \
           -e '/stretch-updates/d' /etc/apt/sources.list
RUN apt-get update && \
	apt-get install \
		python \
		python-pip \
		python-protobuf \
		python-openssl \
		python-twisted \
		python-yaml \
		git \
		protobuf-compiler \
		libexpat1 \
		libexpat1-dev \
		libpython-dev \
		libpython2.7 \
		libpython2.7-dev \
		python-dev \
		python2.7-dev \
		-y --force-yes
RUN git clone https://github.com/mwrlabs/drozer/ /tmp/drozer
RUN cd /tmp/drozer && \
	make deb
RUN dpkg -i /tmp/drozer/dist/drozer*.deb
