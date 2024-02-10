from django.shortcuts import render
from flask import Flask, render_template,request,redirect,url_for,jsonify
from app.controller import *
app=Flask(__name__)

e_mail=str
password=str
id=int
name=str
surname=str
p_name=str
p_year=str
p_place=str
p_type=str
todo=str
todo2=str
todo3=str
todo4=str
searching_name=[]





@app.route("/data",methods=['POST','GET'])
def data():
    global todo,todo2,todo3,todo4,searching_name
    if request.method=='POST':
        todo = request.form.get("todo")
        todo2 = request.form.get("todo2")
        todo3 = request.form.get("todo3")
        todo4 = request.form.get("todo4")    
        researcher_id,researcher_name,researcher_surname,researcher_teammate,publication_name_general,publication_year_general,publication_place_general,publication_type_general,teammate_id_general=send_informaiton_for_query(todo,todo2,todo3,todo4)  
        data={'researcher_name':researcher_name,'researcher_id':researcher_id,'researcher_surname':researcher_surname,'researcher_teammate':researcher_teammate,'publication_name_general':publication_name_general,'publication_year_general':publication_year_general,'publication_place_general':publication_place_general,'publication_type_general':publication_type_general,'teammate_id_general':teammate_id_general}
    return data

@app.route("/",methods=['POST','GET'])
def home():
    return render_template('home.html')

@app.route("/node_data",methods=['POST','GET'])
def node_data():
    if request.method=='POST':
        todo = request.form.get("ID")

        r_name,r_publication_name,r_surname,p_publication_id,p_publication_name,p_publication_place,p_publication_type,p_publication_year,t_type_id,t_type_place,t_type_type,r_teammate_id,r_teammate_name,r_teammate_publication_name,r_teammate_surname,r_node_id,p_node_id,type_node_id,r_teammate_node_id,teammate_p_node_id_general=send_information_for_graph(todo)
        data_dict={'r_name':r_name,'r_publication_name':r_publication_name,'r_surname':r_surname,'p_publication_id':p_publication_id,'p_publication_name':p_publication_name,'p_publication_place':p_publication_place,'p_publication_type':p_publication_type,'p_publication_year':p_publication_year,'t_type_id':t_type_id,'t_type_place':t_type_place,'t_type_type':t_type_type,'r_teammate_id':r_teammate_id,'r_teammate_name':r_teammate_name,'r_teammate_publication_name':r_teammate_publication_name,'r_teammate_surname':r_teammate_surname,'r_node_id':r_node_id,'p_node_id':p_node_id,'type_node_id':type_node_id,'r_teammate_node_id':r_teammate_node_id,'teammate_p_node_id_general':teammate_p_node_id_general}
        
    
    return data_dict
    

@app.route("/node",methods=['POST','GET'])
def node():
    return render_template('node.html')


@app.route("/login",methods=['POST','GET'])
def login():
    global e_mail,password
    if request.method=='POST':    
        e_mail=request.form["email"]
        password=request.form["password"] 
        if(user_exist(e_mail,password)):
            print("Giriş Başarılı")
            return redirect(url_for("admin_home"))       

        else:
            print("Hatalı Giriş")
    
    return render_template("login.html")

@app.route("/admin_dashboard",methods=['POST','GET'])
def admin_home():
    global id,name,surname,p_name,p_year,p_place,p_type
    if request.method=='POST':
        id=request.form["ID"]
        name=request.form["name"]
        surname=request.form["surname"]
        p_id=request.form["p_id"]
        p_name=request.form["p_name"]
        p_year=request.form["p_year"]
        p_place=request.form["p_place"]
        p_type=request.form["p_type"]
        if id!="" and name!="" and surname!="":
            send_publication_information(id,name,surname,p_id,p_name,p_year,p_place,p_type)
   
    return render_template("admin_home.html")

