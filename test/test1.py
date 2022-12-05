#test1 rev_setting
import requests
import json
import subprocess
name="test_auth"
url="http://host.docker.internal:8080/test"
user_url="test_auth"
cmd="""sh -c 'printf "\n{url}" >> rev/url' """.format(url=url).strip()
subprocess.call(cmd,shell=True)
url1="http://host.docker.internal:8001/services"
url_name={
    'name':name,
    'url':url,
}
#url regisration(kong) 
response=requests.post(url1,url_name)
 
url2="http://host.docker.internal:8001/services/"+name+"/routes"
path="/"+name
path_data={
    'paths[]':path,
    'name':name+"_route",
}
#proxy setting
response=requests.post(url2,path_data)

url3="http://host.docker.internal:8001/services/"+name+"/plugins"
auth_setting={
    "name":"key-auth",
    "config.key_names":"test-key",
}
#Keyauth introduction
response=requests.post(url3,auth_setting)