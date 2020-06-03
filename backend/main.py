#!/usr/bin/env python3

import os
import sys
import yaml
import flask
import subprocess
import flask_httpauth
from werkzeug.security import generate_password_hash, check_password_hash



def reload_config():
    """
    function to reload config file
    """
    global conf
    global users
    global conffile
    with open(conffile) as f:
        if hasattr(yaml, 'FullLoader'):
            conf = yaml.load(f, Loader=yaml.FullLoader)
        else:
            conf = yaml.load(f)
    users={}
    for user in conf['user']:
        users[user['name']] = generate_password_hash(user['pass'])



# get config file
try:
    conffile = os.path.abspath(sys.argv[1])
    rootpath = os.path.dirname(os.path.dirname(conffile))
    reload_config()
except:
    print('ERR: cannot read config file')
    sys.exit(1)


app = flask.Flask(
    __name__,
    static_url_path='',
    static_folder=os.path.join( rootpath, 'frontend' ),
    template_folder=os.path.join( rootpath, 'templates' )
)
app.config['TEMPLATES_AUTO_RELOAD'] = True
auth = flask_httpauth.HTTPBasicAuth()


def main():
    app.run(
        host='0.0.0.0',
        port=conf['config']['port']
    )

#
# User & password validation
#

# generate users dict
reload_config()

# return user roles
@auth.get_user_roles
def get_user_roles(user):
    reload_config()
    for u in conf['user']:
        if u['name'] == user:
            return u['role']

def get_user_desc(user):
    reload_config()
    for u in conf['user']:
        if u['name'] == user:
            return u['desc']

def user_exists(user):
    reload_config()
    for u in conf['user']:
        if u['name'] == user:
            return True
    return False

def get_current_user_role():
    username = auth.current_user()
    return get_user_roles(username)


def gen_openssl_pwd(pwd):
    pwd = subprocess.check_output([
        'openssl',
        'passwd',
        '-1',
        pwd
    ])
    return pwd.decode().strip()


def rewrite_vpnfiles():
    w_chap  = os.access("/etc/ppp/chap-secrets", os.W_OK)
    w_ipsec = os.access("/etc/ipsec.d/passwd", os.W_OK)
    if not w_chap or not w_ipsec:
        print("cannot update files, not writable")
        return
    file_chap_pw = ''
    file_ipsec_pw = ''
    for user in conf['user']:
        file_chap_pw += f"\"{user['name']}\" l2tpd \"{user['pass']}\" *\n"
        enc_pw = gen_openssl_pwd(user['pass'])
        file_ipsec_pw += f"{user['name']}:{enc_pw}:xauth-psk\n"
    with open("/etc/ppp/chap-secrets", 'w') as f:
        f.write(file_chap_pw)
    with open("/etc/ipsec.d/passwd", 'w') as f:
        f.write(file_ipsec_pw)



# verify user_pass
@auth.verify_password
def verify_password(username, password):
    reload_config()
    if username in users and \
            check_password_hash(users.get(username), password):
        return username


# update password on yaml file
def update_conf_user(user, pw, role='user', desc=''):
    global conf
    if role not in ['user', 'admin']:
        role='user'
    new_users = []
    for u in conf['user']:
        if u['name'] == user:
            u['pass'] = pw
            u['role'] = role
            u['desc'] = desc
        new_users.append(u)
    conf['user'] = new_users
    with open(conffile, 'w') as f:
        yaml.dump(conf, f, default_flow_style=False)
    rewrite_vpnfiles()


# all logged in users: change password of own account
@app.route('/mypass', methods=['POST'])
@auth.login_required(role=['admin', 'user'])
def change_my_pass():
    username = auth.current_user()
    if not user_exists(username):
        return "404"

    newpass = flask.request.form.get('pass')
    role = get_user_roles(username)
    desc = get_user_desc(username)
    update_conf_user(username, newpass, role, desc)
    rewrite_vpnfiles()
    return "200"


# only admin: change pass of every user
@app.route('/pass', methods=['POST'])
@auth.login_required(role=['admin'])
def change_any_pass():
    username = flask.request.form.get('user')
    if not user_exists(username):
        return "404"
    newpass = flask.request.form.get('pass')
    role = flask.request.form.get('role', get_user_roles(username))
    desc = flask.request.form.get('desc', get_user_desc(username))
    update_conf_user(username, newpass, role, desc)
    rewrite_vpnfiles()
    return "200"


# only admin: create new user
@app.route('/newuser', methods=['POST'])
@auth.login_required(role=['admin'])
def create_new_user():
    username = flask.request.form.get('user')
    if user_exists(username):
        return "500"
    newpass = flask.request.form.get('pass')
    role = flask.request.form.get('role', 'user')
    desc = flask.request.form.get('desc', '')
    conf['user'].append({
        "name": username,
        "pass": newpass,
        "role": role,
        "desc": desc
    })
    with open(conffile, 'w') as f:
        yaml.dump(conf, f, default_flow_style=False)
    rewrite_vpnfiles()
    return "200"


# only admin: delete user
@app.route('/deluser', methods=['POST'])
@auth.login_required(role=['admin'])
def delete_user():
    username = flask.request.form.get('user')
    if not user_exists(username):
        return "404"
    new_users = []
    for u in conf['user']:
        if u['name'] == username:
            continue
        else:
            new_users.append(u)
    conf['user'] = new_users
    with open(conffile, 'w') as f:
        yaml.dump(conf, f, default_flow_style=False)
    rewrite_vpnfiles()
    return "200"


# only admin: list all
@app.route('/list', methods=['GET'])
@auth.login_required(role=['admin'])
def list_all_users():
    response = app.response_class(
        response=flask.json.dumps(conf),
        status=200,
        mimetype='application/json'
    )
    return response


# everyone: change own pass GUI
@app.route('/')
@auth.login_required(role=['admin', 'user'])
def index():
    return flask.render_template(
        'mypw.html',
        user_role=get_current_user_role()
    )


# admin: all users GUI
@app.route('/admin')
@auth.login_required(role='admin')
def admin():
    return flask.render_template(
        'admin.html',
        user_role=get_current_user_role()
    )





if __name__ == '__main__':
    main()
