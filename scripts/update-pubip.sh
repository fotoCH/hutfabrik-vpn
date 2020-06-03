#!/usr/bin/env bash
# Script to update ipsec VPN config

HOSTNAME="hutfabrik.ddns.net"

CURR_IP_CONF=$(grep leftid /etc/ipsec.conf | cut -d"=" -f2)
CURR_IP_DNS=$(dig +short ${HOSTNAME})

if [[ "${CURR_IP_DNS}" != "${CURR_IP_CONF}" ]]; then
  sed -i "s/${CURR_IP_CONF}/${CURR_IP_DNS}/g" /etc/ipsec.conf
  systemctl restart ipsec.service
  systemctl restart xl2tpd.service
fi
