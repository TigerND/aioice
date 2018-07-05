
FROM teego/node:8.11.3-Ubuntu-artful

MAINTAINER Aleksandr Zykov <tiger@mano.email>

ENV DEBIAN_FRONTEND noninteractive

RUN ( \
        apt-get update -q \
    &&  apt-get upgrade -qy --no-install-recommends \
    &&  apt-get clean -qy \
    )
    
RUN ( \
        apt-get install -qy --no-install-recommends \
            iproute2 \
            inetutils-traceroute \
    &&  apt-get clean -qy \
    )

RUN ( \
        apt-get install -qy --no-install-recommends \
            python3 \
            python3-pip \
    &&  apt-get clean -qy \
    )

RUN ( \
        pip3 install \
            aioice \
            websockets \
    )
    
RUN mkdir -p /r/aioice

ADD . /r/aioice

ADD docker/docker-entrypoint.sh /docker-entrypoint.sh 

RUN chmod a+x /docker-entrypoint.sh 

ENTRYPOINT ["/docker-entrypoint.sh"]

CMD ["npm", "start"]