from app.models import *

def user_exist(email,password):
    db_email=get_admin_email_password()[0]
    db_password=get_admin_email_password()[1]
    if(email==db_email and password==db_password):
        return True
    else:
        return False

def send_publication_information(ID,name,surname,p_id,p_name,p_year,p_place,p_type):
    get_publication_information(ID,name,surname,p_id,p_name,p_year,p_place,p_type)

def send_informaiton_for_query(name,surname,p_name,p_year):
    return query(name,surname,p_name,p_year)

def send_information_for_graph(id):
    return graph_query(id)