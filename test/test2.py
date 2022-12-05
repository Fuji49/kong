import requests

def token(client_id, client_secret, username, password):
    
    #アクセストークンを発行
    da = {
        'client_id': client_id,
        'client_secret': client_secret,
        'username': username,
        'password': password,
        'grant_type': 'password'
    }

    tkn = requests.post('http://host.docker.internal:8185/auth/realms/master/protocol/openid-connect/token', data=da)
    #tknをjson形式に変換し、'access_token'のみ取り出す
    tkn_json=tkn.json()
    return tkn_json

tkn_json=token("admin-cli","aa","admin","admin")
headers = {
    'Authorization':'Bearer %s'% tkn_json['access_token']
}
#realm=request.form['realm']
realm="master"
res=requests.get("http://host.docker.internal:8185/auth/admin/realms/%s/users"% realm, headers=headers).json()
print(res)
