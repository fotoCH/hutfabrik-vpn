#!/usr/bin/env python3

import os
import sys
import yaml
import subprocess




def gen_openssl_pwd(pwd):
    '''
    generate encrypted password using openssl
    '''
    pwd = subprocess.check_output([
        'openssl',
        'passwd',
        '-1',
        pwd
    ])
    return pwd.decode().strip()



def main():
    '''
    main function
    '''
    try:
        yf = sys.argv[1]
    except:
        print('ERROR: no file specified')
        sys.exit(1)

    with open(yf) as f:
        conf = yaml.load(f, Loader=yaml.FullLoader)


    file_chap_pw = ''
    file_ipsec_pw = ''
    # fill out users file
    for user in conf['user']:
        file_chap_pw += f"\"{user['name']}\" l2tpd \"{user['pass']}\" *\n"
        enc_pw = gen_openssl_pwd(user['pass'])
        file_ipsec_pw += f"{user['name']}:{enc_pw}:xauth-psk\n"

    print(file_chap_pw)
    print(file_ipsec_pw)

    w_chap  = os.access("/etc/ppp/chap-secrets", os.W_OK)
    w_ipsec = os.access("/etc/ipsec.d/passwd", os.W_OK)
    if not w_chap or not w_ipsec:
        print("cannot update files, not writable")
        return

    with open("/etc/ppp/chap-secrets", 'w') as f:
        f.write(file_chap_pw)
    with open("/etc/ipsec.d/passwd", 'w') as f:
        f.write(file_ipsec_pw)



if __name__ == '__main__':
    main()
