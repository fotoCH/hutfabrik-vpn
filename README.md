## Install

```
apt install bash-completion dnsutils python3-yaml net-tools htop git curl python3-yaml rsync python3-pip

wget https://git.io/vpnsetup -O vpnsetup.sh
sh vpnsetup.sh

pip3 install flask
pip3 install flask_httpauth

cd /opt/
git clone git@github.com:fotoCH/hutfabrik-vpn.git
cd vpn

# adjust config
vim config/vpn-users.yaml

cp -ra systemd/* /etc/systemd/system/
systemctl daemon-reload

systemctl start vpngui.service
systemctl enable vpngui.service

systemctl enable --now vpnupdate.timer

systemctl disable fail2ban

```


## Notes
pass:

- /etc/ppp/chap-secrets
  "username" l2tpd "password" *

- /etc/ipsec.d/passwd
  username:password-enc:xauth-psk

  password enc:
  openssl passwd -1 "123qwe"

- /etc/ipsec.secrets
  PSK
  %any  %any  : PSK "$VPN_IPSEC_PSK"
