#Kong redirect
# SQLAlchemy はデータベース(DB)を object のように扱えるライブラリである。
# 今回は DB との連結を担当する。
# models.py の User クラスで、どのような object として扱うかを決める。
from flask import Flask, render_template, request, url_for, redirect, jsonify
#from sqlalchemy import create_engine, exc
#from sqlalchemy.orm import sessionmaker
#from models import User, Url
#import hashlib
#from datetime import datetime
#from werkzeug import exceptions

import requests
import json
import subprocess

# Flask クラスから作成された インスタンスを app に代入する。
app = Flask(__name__)

#url input
@app.route("/url_input", methods=["get"])
def url_input():
    return render_template("url_input.html")

@app.route("/rev_settings", methods=["get"])
def get_rev_settings():
    return redirect("http://host.docker.internal:8080/admin/url_input")

#url registration
@app.route("/rev_settings", methods=["post"])
def rev_settings():
    url=request.form["url"]
    name=request.form["user_url"]
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
        "config.key_names":"apikey"
    }
    #Keyauth introduction
    response=requests.post(url3,auth_setting)
    return redirect("http://host.docker.internal:8080/admin/web_url")

@app.route("/url_del",methods=["get"])
def get_url_del():
    return redirect("http://host.docker.internal:8080/admin/web_url")
@app.route("/url_del", methods=["post"])
def url_del():
    num_str=request.form["num"]
    num=int(num_str)+1
    #cmd="""sudo sh -c 'sed {num}d rev/url > rev/url_tmp' """.format(num=num)
    #cmd2="sudo mv rev/url_tmp rev/url"
    cmd="""sh -c 'sed {num}d rev/url > rev/url_tmp' """.format(num=num)
    cmd2="mv rev/url_tmp rev/url"
    subprocess.call(cmd,shell=True)
    subprocess.call(cmd2,shell=True)
    return redirect("http://host.docker.internal:8080/admin/web_url")
    #サービス名を入力してもらってKongから削除

@app.route("/container", methods=["get"])
def container():
    return render_template("container.html")

@app.route("/web_url",methods=["get"])
def web_url():
    res=requests.get("http://host.docker.internal:8001/services/").json()
    res=res["data"]
    return render_template("web_url.html", res=res)
    

@app.route("/home_menu",methods=["get"])
def home_menu():
    return render_template("home_menu.html")

#ユーザを表示する
@app.route("/users",methods=["get"])
def users():
    res=requests.get("http://host.docker.internal:8001/consumers/").json()
    res=res["data"]
    return render_template("users.html", res=res)
# ユーザー登録画面へ 
@app.route("/add_user_input", methods=['get'])
def add_user_input():
    return render_template("add_user_input.html")
# ユーザー作成
@app.route("/add_user", methods=['post'])
def add_user():
    username=request.form['username']
    apikey=request.form['password']
    #apikey=request.form['apikey']
    user_data = {
        'username':username,
        'custom_id':username,
    }
    response = requests.post('http://host.docker.internal:8001/consumers/', data=user_data)

    url="http://host.docker.internal:8001/consumers/"+username+"/key-auth"

    key_data={
        'key':apikey,
    }
    response2=requests.post(url,key_data)
    res=requests.get("http://host.docker.internal:8001/consumers/").json()
    res=res["data"]
    return render_template("users_local.html",res=res)

    # ユーザー登録画面へ 
@app.route("/delete_user_input", methods=['get'])
def delete_user_input():
    res=requests.get("http://host.docker.internal:8001/consumers/").json()
    res=res["data"]
    return render_template("delete_user_input.html",res=res)
# ユーザー作成
@app.route("/delete_user", methods=['post'])
def delete_user():
    username=request.form['username']
    user_data = {
        'username':username,
    }
    url="http://host.docker.internal:8001/consumers/"+username
    response = requests.delete(url)
    res=requests.get("http://host.docker.internal:8001/consumers/").json()
    res=res["data"]
    return render_template("users_local.html",res=res)

@app.route("/delete_url_input", methods=['get'])
def delete_url_input():
    res=requests.get("http://host.docker.internal:8001/services/").json()
    res=res["data"]
    return render_template("delete_url_input.html",res=res)

@app.route("/delete_url", methods=['post'])
def delete_url():
    servicename=request.form['servicename']
    url="http://host.docker.internal:8001/routes/"+servicename+"_route"
    response = requests.delete(url)
    url="http://host.docker.internal:8001/services/"+servicename
    response = requests.delete(url)
    return redirect("http://host.docker.internal:8080/admin/web_url")

@app.route("/fiware", methods=["get"])
def fiware():
    res=requests.get("http://host.docker.internal:1026/v2/entities").json()
    return render_template("fiware.html",res=res)

#Kong container
@app.route("/docker_run_kong", methods=["get"])
def docker_run_kong():
    cmd1="""docker network create kong-net"""
    cmd2="""docker run -d --name kong-database \
  --network=kong-net \
  -p 5432:5432 \
  -e "POSTGRES_USER=kong" \
  -e "POSTGRES_DB=kong" \
  -e "POSTGRES_PASSWORD=kongpass" \
  postgres:9.6"""
    cmd3="""docker run --rm --network=kong-net \
  -e "KONG_DATABASE=postgres" \
  -e "KONG_PG_HOST=kong-database" \
  -e "KONG_PG_PASSWORD=kongpass" \
  -e "KONG_PASSWORD=test" \
 kong/kong-gateway:3.0.1.0 kong migrations bootstrap"""
    cmd4="""docker run -d --name kong-gateway \
  --network=kong-net \
  -e "KONG_DATABASE=postgres" \
  -e "KONG_PG_HOST=kong-database" \
  -e "KONG_PG_USER=kong" \
  -e "KONG_PG_PASSWORD=kongpass" \
  -e "KONG_PROXY_ACCESS_LOG=/dev/stdout" \
  -e "KONG_ADMIN_ACCESS_LOG=/dev/stdout" \
  -e "KONG_PROXY_ERROR_LOG=/dev/stderr" \
  -e "KONG_ADMIN_ERROR_LOG=/dev/stderr" \
  -e "KONG_ADMIN_LISTEN=0.0.0.0:8001" \
  -e "KONG_ADMIN_GUI_URL=http://localhost:8002" \
  -e KONG_LICENSE_DATA \
  -p 8000:8000 \
  -p 8443:8443 \
  -p 8001:8001 \
  -p 8444:8444 \
  -p 8002:8002 \
  -p 8445:8445 \
  -p 8003:8003 \
  -p 8004:8004 \
  kong/kong-gateway:3.0.1.0"""
    subprocess.run(cmd1)
    subprocess.run(cmd2)
    subprocess.run(cmd3)
    subprocess.run(cmd4)
    return redirect("http://host.docker.internal:8080/admin/container")





