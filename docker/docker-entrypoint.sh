#!/bin/bash

ipv4_network=`ip -4 addr show dev eth0 | grep inet | awk '{printf("%s", $2);}'`
ipv4_address=`echo ${ipv4_network} | sed 's/\/.*//g'`

ipv6_network=`ip -6 addr show dev eth0 | grep inet | awk '{printf("%s", $2);}'`
ipv6_address=`echo ${ipv6_network} | sed 's/\/.*//g'`

echo

cd /r/aioice

echo IPv4: ${ipv4_address}
echo IPv6: ${ipv6_address}
echo

exec "$@"