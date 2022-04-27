FROM ubuntu:latest

RUN apt update && \
    apt install -y gobject-introspection \
    tox \
    dbus \
    libdbus-1-dev \
    libgirepository1.0-dev \
    python3-cairo-dev \
    #pylint3 \
    #flake8 \
    python3-dbus \
    python3-dev \
    systemd

COPY networkd-dispatcher /usr/bin

COPY networkd-dispatcher.conf /etc/conf.d

COPY entry.sh /

RUN chmod +x /entry.sh

RUN mkdir -p /etc/networkd-dispatcher/{routable,dormant,no-carrier,off,carrier,degraded,configuring,configured}.d

ENTRYPOINT ["/entry.sh"]
