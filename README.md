schritte:

[x] router checken
[x] ddns einrichten
[ ] vpn-vm aufsetzen
  -> https://github.com/hwdsl2/setup-ipsec-vpn
[x] portweiterleitung
[x] vpn testen auf ipad

[ ] scripts um yaml in configs umzuwandeln
[ ] daily ip check script
[ ] backend um config abzufüllen
[ ] frontend







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



install:

apt install bash-completion dnsutils python3-yaml net-tools htop git curl
wget https://git.io/vpnsetup -O vpnsetup.sh
sh vpnsetup.sh
