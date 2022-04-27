#!/bin/sh
mkdir -p /var/run/dbus && dbus-daemon --config-file=/usr/share/dbus-1/system.conf --print-address

while :
do
	sleep 1
done
