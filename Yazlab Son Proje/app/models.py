from ctypes import sizeof
from neo4j import GraphDatabase
#That module connects to database

id=int
p_id=int
type_id=int
name=str
surname=str
p_name=str
p_year=str
p_place=str
p_type=str



class Neo4jConnection:
    
    def __init__(self, uri, user, pwd):
        self.__uri = uri
        self.__user = user
        self.__pwd = pwd
        self.__driver = None
        try:
            self.__driver = GraphDatabase.driver(self.__uri, auth=(self.__user, self.__pwd))
        except Exception as e:
            print("Failed to create the driver:", e)
        
    def close(self):
        if self.__driver is not None:
            self.__driver.close()
        
    def query(self, query, db=None):
        assert self.__driver is not None, "Driver not initialized!"
        session = None
        response = None
        try: 
            session = self.__driver.session(database=db) if db is not None else self.__driver.session() 
            response = list(session.run(query))
        except Exception as e:
            print("Query failed:", e)
        finally: 
            if session is not None:
                session.close()
        return response

conn = Neo4jConnection(uri="bolt://localhost:7687", user="ofucer", pwd="2020Avrasya")

#Adminin Email ve Sifresini db'den ceken fonksiyon
def get_admin_email_password():

    query=("MATCH(n:Admin) return(n)")
    sorgu=conn.query(query, db='yazlab')

    results = [record for record in sorgu]
    node = results[0]['n']
    password=results[0]['n'].get('password')
    email=results[0]['n'].get('email')
    query_for_getting_publication_id=("MATCH(n:Publications) RETURN n")

    result=conn.query(query_for_getting_publication_id,db='yazlab')
    results = [record for record in result]
    
    
    return email,password

def get_publication_information(ID,Name,Surname,P_id,P_name,P_year,P_place,P_type):
    global id,name,surname,p_name,p_year,p_place,p_type,p_id,type_id
    id=ID
    p_id=P_id
    name=Name
    surname=Surname
    p_name=P_name
    p_year=P_year
    p_place=P_place
    p_type=P_type
    if(P_id!=""):
        type_id=int(P_id)+1
    create_publication()



def create_publication():
   global id,name,surname,p_name,p_year,p_place,p_type,type_id,p_id
  
   
   #Yayın id kontrol sağlamak için sorgu
   query_control_p_id=("MATCH(n:Publications) WHERE n.publication_id='"+str(p_id)+"'return n")
   query_control_conn_p_id=conn.query(query_control_p_id,db='yazlab')
   result_for_control_p_id=[record for record in query_control_conn_p_id]
   #Araştırmacı id kontrol sağlamak için sorgu


   query_control_r_id=("MATCH(n:Researcher) WHERE n.Researcher_ID='"+str(id)+"'return n")
   query_control_conn_r_id=conn.query(query_control_r_id,db='yazlab')
   result_for_control_r_id=[record for record in query_control_conn_r_id]

   #Eğer yayın id girilmişse ve database de öyle bir yayın yoksa
   if(len(result_for_control_p_id)==0 and p_id!=""):
        
        #Tür tablosu yaratmak için sorgu
        query_create_type=("MERGE (n:Type {Type_id:'"+str(type_id)+"',publication_place:'"+str(p_place)+"', publication_type:'"+str(p_type)+"'})") 
        conn.query(query_create_type,db='yazlab')
        
        #Tür tablosundan yayın tablosuna yer ve türü aktarmak için sorgu
        query_for_get_place_and_type=("MATCH(n:Type) WHERE n.Type_id='"+str(type_id)+"'return n")
        results_type_place_and_type=conn.query(query_for_get_place_and_type,db='yazlab')
        result_t_place_and_type=[record for record in results_type_place_and_type]
        type_to_publication_place = result_t_place_and_type[0]['n'].get('publication_place')
        type_to_publication_type=result_t_place_and_type[0]['n'].get('publication_type')

        #Tür tablosundan aldığımı yer ve tür değişkenlerini yayın tablosuna aktarma
        query_create_publication=("MERGE (n:Publications {publication_id:'"+str(p_id)+"',publication_name:'"+str(p_name)+"', publication_year:'"+str(p_year)+"',publication_type:'"+str(type_to_publication_type)+"',publication_place:'"+str(type_to_publication_place)+"'})")
        conn.query(query_create_publication,db='yazlab')  

        #Tür tablosu ve yayın tablosu arası ilişki kurma
        query_publication_connect_to_type=("MATCH(a:Publications), (b:Type) WHERE a.publication_id='"+str(p_id)+"'AND b.Type_id= '"+str(type_id)+"'MERGE (a)-[r:PUBLISHED]->(b)")
        conn.query(query_publication_connect_to_type,db='yazlab')
        query_for_get_publication_name=("MATCH(n:Publications) WHERE n.publication_id='"+str(p_id)+"'return n")
        results_type_publication_name=conn.query(query_for_get_publication_name,db='yazlab')
        result_t_publication_name=[record for record in results_type_publication_name]
        type_to_publication_name= result_t_publication_name[0]['n'].get('publication_name')


        #Eğer öyle bir araştırmacı database de yoksa
        if(len(result_for_control_r_id)==0):  
            #Araştırmacı oluşturmak için
            query_create_researcher=("MERGE (n:Researcher {Researcher_ID:'"+str(id)+"', name:'"+str(name)+"', surname:'"+str(surname)+"',publication_name:'"+str(type_to_publication_name)+"'})")
            conn.query(query_create_researcher,db='yazlab')

        #Araştırmacı ve yayın tablosu arası ilişki kurma
        query_researcher_to_connection=("MATCH(a:Researcher), (b:Publications) WHERE a.Researcher_ID='"+str(id)+"'AND b.publication_id= '"+str(p_id)+"'MERGE (a)-[r:PUBLICATION_WRITER]->(b)")
        conn.query(query_researcher_to_connection,db='yazlab')


   #Eğer yayın id girilmişse ve öyle bir yayın database de varsa    
   if(len(result_for_control_p_id)!=0 and p_id!=""):
            #Eğer database de öyle bir araştırmacı yoksa
            if(len(result_for_control_r_id)==0):
                #Yayın tablosundan yayın ismini çekmek için sorgu
                query_for_get_publication_name2=("MATCH(n:Publications) WHERE n.publication_id='"+str(p_id)+"'return n")
                results_type_publication_name2=conn.query(query_for_get_publication_name2,db='yazlab')
                result_t_publication_name2=[record for record in results_type_publication_name2]
                type_to_publication_name2= result_t_publication_name2[0]['n'].get('publication_name')
                #Araştırmacı oluşturmak için sorgu
                query_create_researcher=("MERGE (n:Researcher {Researcher_ID:'"+str(id)+"', name:'"+str(name)+"', surname:'"+str(surname)+"',publication_name:'"+str(type_to_publication_name2)+"'})")
                conn.query(query_create_researcher,db='yazlab')
            #Araştırmacı ve yayın tablosu arası ilişki kurmak için sorgu
            query_researcher_to_connection=("MATCH(a:Researcher), (b:Publications) WHERE a.Researcher_ID='"+str(id)+"'AND b.publication_id= '"+str(p_id)+"'MERGE (a)-[r:PUBLICATION_WRITER]->(b)")
            conn.query(query_researcher_to_connection,db='yazlab')
   
   
   #Eğer database de öyle bir araştırmacı yoksa ve yayın id girilmemişse
   if(len(result_for_control_r_id)==0 and p_id==""):
            #Yayını olmayan Araştırmacı oluşturmak için sorgu
            query_create_researcher=("MERGE (n:Researcher {Researcher_ID:'"+str(id)+"', name:'"+str(name)+"', surname:'"+str(surname)+"'})")
            conn.query(query_create_researcher,db='yazlab')
   
   query_for_who_published=("MATCH(n:Researcher)-[r:PUBLICATION_WRITER]->(m:Publications) WHERE m.publication_id='"+str(p_id)+"' RETURN (n)")
   results_for_who_published=conn.query(query_for_who_published,db='yazlab')
   who_published=[record for record in results_for_who_published]
   
   list_of_who_published=[]
   for i in range(len(who_published)):
     if(who_published[i]['n'].get("Researcher_ID")!=id):
        list_of_who_published.append(who_published[i]['n'].get("Researcher_ID"))       
   if len(who_published)>0:
        for i in list_of_who_published:
            query_for_works_collaboratıvely=("MATCH(n:Researcher {Researcher_ID: '"+str(id)+"'}),(m:Researcher {Researcher_ID: '"+str(i)+"'})MERGE (n)-[r:WORKS_COLLABORATIVELY]->(m) MERGE (m)-[w:WORKS_COLLABORATIVELY]->(n)")
            conn.query(query_for_works_collaboratıvely,db='yazlab')
   
   query_for_publications_to_researcher=("MATCH(n:Researcher)-[r:PUBLICATION_WRITER]->(m:Publications) WHERE n.Researcher_ID='"+str(id)+"' RETURN (m)")
   results_for_shared_publication=conn.query(query_for_publications_to_researcher,db='yazlab')
   shared_publication=[record for record in results_for_shared_publication]
   list_of_shared_publication=[]
   mass_publication=""
   for i in range(len(shared_publication)):
       list_of_shared_publication.append(shared_publication[i]['m'].get("publication_name"))
       if(i!=len(shared_publication)-1):
           mass_publication+=str(str(list_of_shared_publication[i])+",")
       else:
           mass_publication+=str(list_of_shared_publication[i]) 
   query_change_the_researcher_publication=("MATCH(n:Researcher) WHERE n.Researcher_ID='"+str(id)+"' SET n.publication_name='"+str(mass_publication)+"'")
   conn.query(query_change_the_researcher_publication,db='yazlab')

   
def query(name,surname,p_name,p_year):
    if(name!="" and surname!="" and p_name!="" and p_year!=""):
        pass
    if(p_name!=""):
       #Query For Year
       query_for_publicaton_id=("MATCH(n:Publications) WHERE n.publication_name='"+str(p_name)+"' RETURN n")
       query_result_for_publicaton_id=conn.query(query_for_publicaton_id, db='yazlab')
       
       if(p_year!=""):
           query_for_publicaton_id=("MATCH(n:Publications) WHERE n.publication_name='"+str(p_name)+"' AND n.publication_year='"+str(p_year)+"' RETURN n")
           query_result_for_publicaton_id=conn.query(query_for_publicaton_id, db='yazlab')
      

       list_of_publication_id=[]
       list_of_publication_id_general=[]
       year_list=[]
       list_of_researcher_name=[]
       list_of_researcher_surname=[]
       name_general=[]
       surname_general=[]
       list_of_researcher_id=[]
       researcher_id_general=[]
       researcher_id_general_copy=[]
       teammate_id_general=[]
       publication_name_general=[]
       publication_year_general=[]
       publication_place_general=[]
       publication_type_general=[]
       researcher_teammate_name_general=[]
       researcher_teammate_surname_general=[]
       copy_list_of_researcher_id_control=[]   
       who_writed_teammate_general=[]
       publication_id_general=[]
       name_surname_holder=str

       for i in range(len(query_result_for_publicaton_id)):
           publication_id_result=[record for record in query_result_for_publicaton_id]
           list_of_publication_id.append(publication_id_result[i]['n'].get("publication_id"))
       list_of_publication_id_general.append(list_of_publication_id)
    #Query for getting year
       for i,k in zip(range(len(list_of_publication_id_general)),list_of_publication_id_general):
           for j in k:
               query_for_year=("MATCH(n:Publications) WHERE n.publication_id='"+str(j)+"' RETURN n")
               query_result_for_year=conn.query(query_for_year, db='yazlab')
               year_result=[record for record in query_result_for_year]
               year_list.append(year_result[0]['n'].get("publication_year")) 
       
    #Query for getting researcher id
       for i in list_of_publication_id_general:     
           for j in i:
               query_for_researcher_id=("MATCH(n:Researcher)-[r:PUBLICATION_WRITER]->(m:Publications) WHERE m.publication_id='"+str(j)+"' RETURN (n)")
               query_result_for_researcher_id=conn.query(query_for_researcher_id, db='yazlab')
               researcher_result=[record for record in query_result_for_researcher_id]
               list_of_researcher_id=[]
               for k in range(len(researcher_result)):
                   list_of_researcher_id.append(researcher_result[k]['n'].get("Researcher_ID"))
               researcher_id_general.append(list_of_researcher_id)
                
    
        
       

       #If there is the same person, do not reduce them to one person 
       for x in range(len(researcher_id_general)):
           
           for y in range(len(researcher_id_general[x])):
               if researcher_id_general[x][y] not in copy_list_of_researcher_id_control:
                   copy_list_of_researcher_id_control.append(researcher_id_general[x][y])
               
       researcher_id_general_copy.append(copy_list_of_researcher_id_control)

       if(surname!="" and name==""):
           list_of_researcher_id=[]
           researcher_id_general_copy=[]
           query_for_researcher_id=("MATCH(n:Researcher) WHERE n.surname='"+str(surname)+"' RETURN n")
           query_result_for_researcher_id=conn.query(query_for_researcher_id, db='yazlab') 
           researcher_id_result=[record for record in query_result_for_researcher_id]        
           for i in range(len(researcher_id_result)):
                list_of_researcher_id.append(researcher_id_result [i]['n'].get("Researcher_ID"))
           researcher_id_general_copy.append(list_of_researcher_id)
           

       if(name!="" and surname==""):
           list_of_researcher_id=[]
           researcher_id_general_copy=[]
           query_for_researcher_id=("MATCH(n:Researcher) WHERE n.name='"+str(name)+"' RETURN n")
           query_result_for_researcher_id=conn.query(query_for_researcher_id, db='yazlab') 
           researcher_id_result=[record for record in query_result_for_researcher_id]
           for i in range(len(researcher_id_result)):
                list_of_researcher_id.append(researcher_id_result [i]['n'].get("Researcher_ID"))
           researcher_id_general_copy.append(list_of_researcher_id)

       if(name!="" and surname!=""):
           list_of_researcher_id=[]
           researcher_id_general_copy=[]
           query_for_researcher_id=("MATCH(n:Researcher) WHERE n.name='"+str(name)+"'AND n.surname='"+str(surname)+"' RETURN n")
           query_result_for_researcher_id=conn.query(query_for_researcher_id, db='yazlab') 
           researcher_id_result=[record for record in query_result_for_researcher_id]
           for i in range(len(researcher_id_result)):
                list_of_researcher_id.append(researcher_id_result [i]['n'].get("Researcher_ID"))
           researcher_id_general_copy.append(list_of_researcher_id)

       
       #Query for getting researcher name and surname
       for i in researcher_id_general_copy:
           list_of_researcher_name=[]
           list_of_researcher_surname=[]
           for j in i:          
                query_for_researcher_id=("MATCH(n:Researcher) WHERE n.Researcher_ID='"+str(j)+"' RETURN (n)")
                query_result_for_researcher_information=conn.query(query_for_researcher_id,db="yazlab")
                researcher_information_result=[record for record in query_result_for_researcher_information]
                for k in range(len(researcher_information_result)):
                   list_of_researcher_name.append(researcher_information_result[k]['n'].get("name"))
                   list_of_researcher_surname.append(researcher_information_result[k]['n'].get("surname"))
           name_general.append(list_of_researcher_name)
           surname_general.append(list_of_researcher_surname)
           
       
       
                
       #Query for getting researcher teammate id , name , surname
       for i in researcher_id_general_copy:         
           for j in i:       
                query_for_researcher_teammate_id=("MATCH(m:Researcher)-[r:WORKS_COLLABORATIVELY]->(n:Researcher) WHERE m.Researcher_ID='"+str(j)+"' RETURN (n)")
                query_result_for_researcher_teammate_information=conn.query(query_for_researcher_teammate_id,db="yazlab")
                researcher_information_teammate_result=[record for record in query_result_for_researcher_teammate_information]
                list_of_researcher_teammate_id=[]
                list_of_researcher_teammate_name=[]
                list_of_researcher_teammate_surname=[]   
                list_of_researcher_teammate=[]     
                for k in range(len(researcher_information_teammate_result)):
                   teammate_id_holder=researcher_information_teammate_result [k]['n'].get("Researcher_ID")
                   query_for_reseacher_teammate_name_surname=("MATCH(n:Researcher) WHERE n.Researcher_ID='"+str(teammate_id_holder)+"' RETURN (n)")
                   query_result_for_researcher_teammate_name_surname_information=conn.query(query_for_reseacher_teammate_name_surname,db="yazlab")
                   researcher_information_teammate_name_surname_result=[record for record in query_result_for_researcher_teammate_name_surname_information]
                   list_of_researcher_teammate_name.append(researcher_information_teammate_name_surname_result [0]['n'].get("name"))
                   list_of_researcher_teammate_surname.append(researcher_information_teammate_name_surname_result [0]['n'].get("surname"))
                   name_surname_holder=researcher_information_teammate_name_surname_result [0]['n'].get("name")+" "+researcher_information_teammate_name_surname_result [0]['n'].get("surname")
                   list_of_researcher_teammate_id.append(researcher_information_teammate_result [k]['n'].get("Researcher_ID"))
                   list_of_researcher_teammate.append(name_surname_holder)
                teammate_id_general.append(list_of_researcher_teammate_id)
                researcher_teammate_name_general.append(list_of_researcher_teammate_name)
                researcher_teammate_surname_general.append(list_of_researcher_teammate_surname)
                who_writed_teammate_general.append(list_of_researcher_teammate)

       #Query for getting researcher publication id
       for i in researcher_id_general_copy:         
           for j in i:       
                query_for_researcher_p_id=("MATCH(m:Researcher)-[r:PUBLICATION_WRITER]->(n:Publications) WHERE m.Researcher_ID='"+str(j)+"' RETURN (n)")
                query_result_for_researcher_p_id_information=conn.query(query_for_researcher_p_id,db="yazlab")
                researcher_information_p_id_result=[record for record in query_result_for_researcher_p_id_information]       
                list_of_researcher_p_id=[]
                for a in range(len(researcher_information_p_id_result)):
                    list_of_researcher_p_id.append(researcher_information_p_id_result[a]['n'].get("publication_id"))
                publication_id_general.append(list_of_researcher_p_id)
       
       
       counter=0
       for i in range(len(publication_id_general)):
           for j in range(len(publication_id_general[i])):
               if publication_id_general[i][j] in list_of_publication_id:
                   counter+=1
       if(counter==0):
            researcher_id_general_copy=[]
            #Query for getting researcher publication name
       if(counter!=0):
            for i in range(len(publication_id_general)): 
                list_of_researcher_p_name=[]       
                for j in range(len(publication_id_general[i])):
                        query_for_researcher_publication_name=("MATCH(m:Researcher)-[r:PUBLICATION_WRITER]->(n:Publications) WHERE m.Researcher_ID='"+str(researcher_id_general_copy[0][i])+"' AND n.publication_id='"+str(publication_id_general[i][j])+"' RETURN (n)")
                        query_result_for_researcher_p_name_information=conn.query(query_for_researcher_publication_name,db="yazlab")
                        researcher_information_p_name_result=[record for record in query_result_for_researcher_p_name_information]
                                
                        for k in range(len(researcher_information_p_name_result)):
                                list_of_researcher_p_name.append(researcher_information_p_name_result [k]['n'].get("publication_name"))
                        
                            
                publication_name_general.append(list_of_researcher_p_name)


            #Query for getting researcher publication year
            for i in range(len(publication_id_general)): 
                list_of_researcher_p_year=[]        
                for j in range(len(publication_id_general[i])):
                        query_for_researcher_p_year=("MATCH(m:Researcher)-[r:PUBLICATION_WRITER]->(n:Publications) WHERE m.Researcher_ID='"+str(researcher_id_general_copy[0][i])+"' AND n.publication_id='"+str(publication_id_general[i][j])+"' RETURN (n)")
                        query_result_for_researcher_p_year_information=conn.query(query_for_researcher_p_year,db="yazlab")
                        researcher_information_p_year_result=[record for record in query_result_for_researcher_p_year_information]
                                
                        for k in range(len(researcher_information_p_year_result)):
                            list_of_researcher_p_year.append(researcher_information_p_year_result [k]['n'].get("publication_year"))
                            
                publication_year_general.append(list_of_researcher_p_year)
                

            
            #Query for getting researcher publication place
            for i in range(len(publication_id_general)): 
                list_of_researcher_p_place=[]        
                for j in range(len(publication_id_general[i])):       
                        query_for_researcher_p_place=("MATCH(m:Researcher)-[r:PUBLICATION_WRITER]->(n:Publications) WHERE m.Researcher_ID='"+str(researcher_id_general_copy[0][i])+"' AND n.publication_id='"+str(publication_id_general[i][j])+"' RETURN (n)")
                        query_result_for_researcher_p_place_information=conn.query(query_for_researcher_p_place,db="yazlab")
                        researcher_information_p_place_result=[record for record in query_result_for_researcher_p_place_information]       
                        for k in range(len(researcher_information_p_place_result)):
                            list_of_researcher_p_place.append(researcher_information_p_place_result [k]['n'].get("publication_place"))
                publication_place_general.append(list_of_researcher_p_place)

            
            #Query for getting researcher publication type
            for i in range(len(publication_id_general)): 
                list_of_researcher_p_type=[]        
                for j in range(len(publication_id_general[i])):       
                        query_for_researcher_p_type=("MATCH(m:Researcher)-[r:PUBLICATION_WRITER]->(n:Publications) WHERE m.Researcher_ID='"+str(researcher_id_general_copy[0][i])+"' AND n.publication_id='"+str(publication_id_general[i][j])+"' RETURN (n)")
                        query_result_for_researcher_p_type_information=conn.query(query_for_researcher_p_type,db="yazlab")
                        researcher_information_p_type_result=[record for record in query_result_for_researcher_p_type_information]       
                        for k in range(len(researcher_information_p_type_result)):
                            list_of_researcher_p_type.append(researcher_information_p_type_result [k]['n'].get("publication_type"))
                publication_type_general.append(list_of_researcher_p_type)
            


    if(surname!="" and name=="" and p_name=="" and p_year==""):
       #Query For Researcher id
       query_for_researcher_id=("MATCH(n:Researcher) WHERE n.surname='"+str(surname)+"' RETURN n")
       query_result_for_researcher_id=conn.query(query_for_researcher_id, db='yazlab') 
       researcher_id_result=[record for record in query_result_for_researcher_id]
       list_of_researcher_id=[]
       researcher_id_general_copy=[]
       for i in range(len(researcher_id_result)):
           list_of_researcher_id.append(researcher_id_result [i]['n'].get("Researcher_ID"))
       researcher_id_general_copy.append(list_of_researcher_id)
       
       who_writed_teammate_general=[] 
       list_of_publication_id=[]
       list_of_publication_id_general=[]
       p_name_list=[]
       list_of_researcher_name=[]
       list_of_researcher_surname=[]
       name_general=[]
       surname_general=[]
       researcher_id_general=[]
       teammate_id_general=[]
       publication_id_general=[]
       publication_name_general=[]
       publication_year_general=[]
       publication_place_general=[]
       publication_type_general=[]
       researcher_teammate_name_general=[]
       researcher_teammate_surname_general=[]
       copy_list_of_researcher_id_control=[]  
       #Query for getting researcher name and surname
       for i in researcher_id_general_copy:
           list_of_researcher_name=[]
           list_of_researcher_surname=[]
           for j in i:        
                query_for_researcher_id=("MATCH(n:Researcher) WHERE n.Researcher_ID='"+str(j)+"' RETURN (n)")
                query_result_for_researcher_information=conn.query(query_for_researcher_id,db="yazlab")
                researcher_information_result=[record for record in query_result_for_researcher_information]
                for k in range(len(researcher_information_result)):
                   list_of_researcher_name.append(researcher_information_result[k]['n'].get("name"))
                   list_of_researcher_surname.append(researcher_information_result[k]['n'].get("surname"))
           name_general.append(list_of_researcher_name)
           surname_general.append(list_of_researcher_surname)
           


                
       #Query for getting researcher teammate id , name , surname
       for i in researcher_id_general_copy:         
           for j in i:       
                query_for_researcher_teammate_id=("MATCH(m:Researcher)-[r:WORKS_COLLABORATIVELY]->(n:Researcher) WHERE m.Researcher_ID='"+str(j)+"' RETURN (n)")
                query_result_for_researcher_teammate_information=conn.query(query_for_researcher_teammate_id,db="yazlab")
                researcher_information_teammate_result=[record for record in query_result_for_researcher_teammate_information]
                list_of_researcher_teammate_id=[]
                list_of_researcher_teammate_name=[]
                list_of_researcher_teammate_surname=[]
                list_of_researcher_teammate=[]        
                for k in range(len(researcher_information_teammate_result)):
                   teammate_id_holder=researcher_information_teammate_result [k]['n'].get("Researcher_ID")
                   query_for_reseacher_teammate_name_surname=("MATCH(n:Researcher) WHERE n.Researcher_ID='"+str(teammate_id_holder)+"' RETURN (n)")
                   query_result_for_researcher_teammate_name_surname_information=conn.query(query_for_reseacher_teammate_name_surname,db="yazlab")
                   researcher_information_teammate_name_surname_result=[record for record in query_result_for_researcher_teammate_name_surname_information]
                   list_of_researcher_teammate_name.append(researcher_information_teammate_name_surname_result [0]['n'].get("name"))
                   list_of_researcher_teammate_surname.append(researcher_information_teammate_name_surname_result [0]['n'].get("surname"))
                   name_surname_holder=researcher_information_teammate_name_surname_result [0]['n'].get("name")+" "+researcher_information_teammate_name_surname_result [0]['n'].get("surname")
                   list_of_researcher_teammate_id.append(researcher_information_teammate_result [k]['n'].get("Researcher_ID"))
                   list_of_researcher_teammate.append(name_surname_holder)
                teammate_id_general.append(list_of_researcher_teammate_id)
                researcher_teammate_name_general.append(list_of_researcher_teammate_name)
                researcher_teammate_surname_general.append(list_of_researcher_teammate_surname)
                who_writed_teammate_general.append(list_of_researcher_teammate)
                


        #Query for getting researcher publication id
       for i in researcher_id_general_copy:         
           for j in i:       
                query_for_researcher_p_id=("MATCH(m:Researcher)-[r:PUBLICATION_WRITER]->(n:Publications) WHERE m.Researcher_ID='"+str(j)+"' RETURN (n)")
                query_result_for_researcher_p_id_information=conn.query(query_for_researcher_p_id,db="yazlab")
                researcher_information_p_id_result=[record for record in query_result_for_researcher_p_id_information]       
                list_of_researcher_p_id=[]
                for a in range(len(researcher_information_p_id_result)):
                    list_of_researcher_p_id.append(researcher_information_p_id_result[a]['n'].get("publication_id"))
                publication_id_general.append(list_of_researcher_p_id)
       


       #Query for getting researcher publication name
       for i in range(len(publication_id_general)): 
           list_of_researcher_p_name=[]       
           for j in range(len(publication_id_general[i])):
                query_for_researcher_publication_name=("MATCH(m:Researcher)-[r:PUBLICATION_WRITER]->(n:Publications) WHERE m.Researcher_ID='"+str(researcher_id_general_copy[0][i])+"' AND n.publication_id='"+str(publication_id_general[i][j])+"' RETURN (n)")
                query_result_for_researcher_p_name_information=conn.query(query_for_researcher_publication_name,db="yazlab")
                researcher_information_p_name_result=[record for record in query_result_for_researcher_p_name_information]
                        
                for k in range(len(researcher_information_p_name_result)):
                   list_of_researcher_p_name.append(researcher_information_p_name_result [k]['n'].get("publication_name"))
                
                    
           publication_name_general.append(list_of_researcher_p_name)
           

       #Query for getting researcher publication year
       for i in range(len(publication_id_general)): 
           list_of_researcher_p_year=[]        
           for j in range(len(publication_id_general[i])):
                query_for_researcher_p_year=("MATCH(m:Researcher)-[r:PUBLICATION_WRITER]->(n:Publications) WHERE m.Researcher_ID='"+str(researcher_id_general_copy[0][i])+"' AND n.publication_id='"+str(publication_id_general[i][j])+"' RETURN (n)")
                query_result_for_researcher_p_year_information=conn.query(query_for_researcher_p_year,db="yazlab")
                researcher_information_p_year_result=[record for record in query_result_for_researcher_p_year_information]
                        
                for k in range(len(researcher_information_p_year_result)):
                    list_of_researcher_p_year.append(researcher_information_p_year_result [k]['n'].get("publication_year"))
                    
           publication_year_general.append(list_of_researcher_p_year)
        

       
       #Query for getting researcher publication place
       for i in range(len(publication_id_general)): 
           list_of_researcher_p_place=[]        
           for j in range(len(publication_id_general[i])):       
                query_for_researcher_p_place=("MATCH(m:Researcher)-[r:PUBLICATION_WRITER]->(n:Publications) WHERE m.Researcher_ID='"+str(researcher_id_general_copy[0][i])+"' AND n.publication_id='"+str(publication_id_general[i][j])+"' RETURN (n)")
                query_result_for_researcher_p_place_information=conn.query(query_for_researcher_p_place,db="yazlab")
                researcher_information_p_place_result=[record for record in query_result_for_researcher_p_place_information]       
                for k in range(len(researcher_information_p_place_result)):
                      list_of_researcher_p_place.append(researcher_information_p_place_result [k]['n'].get("publication_place"))
           publication_place_general.append(list_of_researcher_p_place)

       
       #Query for getting researcher publication type
       for i in range(len(publication_id_general)): 
           list_of_researcher_p_type=[]        
           for j in range(len(publication_id_general[i])):       
                query_for_researcher_p_type=("MATCH(m:Researcher)-[r:PUBLICATION_WRITER]->(n:Publications) WHERE m.Researcher_ID='"+str(researcher_id_general_copy[0][i])+"' AND n.publication_id='"+str(publication_id_general[i][j])+"' RETURN (n)")
                query_result_for_researcher_p_type_information=conn.query(query_for_researcher_p_type,db="yazlab")
                researcher_information_p_type_result=[record for record in query_result_for_researcher_p_type_information]       
                for k in range(len(researcher_information_p_type_result)):
                      list_of_researcher_p_type.append(researcher_information_p_type_result [k]['n'].get("publication_type"))
           publication_type_general.append(list_of_researcher_p_type)
      

    if(name!="" and surname=="" and p_name=="" and p_year==""):
       #Query For Researcher id
       query_for_researcher_id=("MATCH(n:Researcher) WHERE n.name='"+str(name)+"' RETURN n")
       query_result_for_researcher_id=conn.query(query_for_researcher_id, db='yazlab') 
       researcher_id_result=[record for record in query_result_for_researcher_id]
       list_of_researcher_id=[]
       researcher_id_general_copy=[]
       for i in range(len(researcher_id_result)):
           list_of_researcher_id.append(researcher_id_result [i]['n'].get("Researcher_ID"))
       researcher_id_general_copy.append(list_of_researcher_id)
       
       who_writed_teammate_general=[] 
       list_of_publication_id=[]
       list_of_publication_id_general=[]
       p_name_list=[]
       list_of_researcher_name=[]
       list_of_researcher_surname=[]
       name_general=[]
       surname_general=[]
       researcher_id_general=[]
       teammate_id_general=[]
       publication_id_general=[]
       publication_name_general=[]
       publication_year_general=[]
       publication_place_general=[]
       publication_type_general=[]
       researcher_teammate_name_general=[]
       researcher_teammate_surname_general=[]
       copy_list_of_researcher_id_control=[]  
       #Query for getting researcher name and surname
       for i in researcher_id_general_copy:
           list_of_researcher_name=[]
           list_of_researcher_surname=[]
           for j in i:        
                query_for_researcher_id=("MATCH(n:Researcher) WHERE n.Researcher_ID='"+str(j)+"' RETURN (n)")
                query_result_for_researcher_information=conn.query(query_for_researcher_id,db="yazlab")
                researcher_information_result=[record for record in query_result_for_researcher_information]
                for k in range(len(researcher_information_result)):
                   list_of_researcher_name.append(researcher_information_result[k]['n'].get("name"))
                   list_of_researcher_surname.append(researcher_information_result[k]['n'].get("surname"))
           name_general.append(list_of_researcher_name)
           surname_general.append(list_of_researcher_surname)
           

                
       #Query for getting researcher teammate id , name , surname
       for i in researcher_id_general_copy:         
           for j in i:       
                query_for_researcher_teammate_id=("MATCH(m:Researcher)-[r:WORKS_COLLABORATIVELY]->(n:Researcher) WHERE m.Researcher_ID='"+str(j)+"' RETURN (n)")
                query_result_for_researcher_teammate_information=conn.query(query_for_researcher_teammate_id,db="yazlab")
                researcher_information_teammate_result=[record for record in query_result_for_researcher_teammate_information]
                list_of_researcher_teammate_id=[]
                list_of_researcher_teammate_name=[]
                list_of_researcher_teammate_surname=[]
                list_of_researcher_teammate=[]        
                for k in range(len(researcher_information_teammate_result)):
                   teammate_id_holder=researcher_information_teammate_result [k]['n'].get("Researcher_ID")
                   query_for_reseacher_teammate_name_surname=("MATCH(n:Researcher) WHERE n.Researcher_ID='"+str(teammate_id_holder)+"' RETURN (n)")
                   query_result_for_researcher_teammate_name_surname_information=conn.query(query_for_reseacher_teammate_name_surname,db="yazlab")
                   researcher_information_teammate_name_surname_result=[record for record in query_result_for_researcher_teammate_name_surname_information]
                   list_of_researcher_teammate_name.append(researcher_information_teammate_name_surname_result [0]['n'].get("name"))
                   list_of_researcher_teammate_surname.append(researcher_information_teammate_name_surname_result [0]['n'].get("surname"))
                   name_surname_holder=researcher_information_teammate_name_surname_result [0]['n'].get("name")+" "+researcher_information_teammate_name_surname_result [0]['n'].get("surname")
                   list_of_researcher_teammate_id.append(researcher_information_teammate_result [k]['n'].get("Researcher_ID"))
                   list_of_researcher_teammate.append(name_surname_holder)
                teammate_id_general.append(list_of_researcher_teammate_id)
                researcher_teammate_name_general.append(list_of_researcher_teammate_name)
                researcher_teammate_surname_general.append(list_of_researcher_teammate_surname)
                who_writed_teammate_general.append(list_of_researcher_teammate)
                


        #Query for getting researcher publication id
       for i in researcher_id_general_copy:         
           for j in i:       
                query_for_researcher_p_id=("MATCH(m:Researcher)-[r:PUBLICATION_WRITER]->(n:Publications) WHERE m.Researcher_ID='"+str(j)+"' RETURN (n)")
                query_result_for_researcher_p_id_information=conn.query(query_for_researcher_p_id,db="yazlab")
                researcher_information_p_id_result=[record for record in query_result_for_researcher_p_id_information]       
                list_of_researcher_p_id=[]
                for a in range(len(researcher_information_p_id_result)):
                    list_of_researcher_p_id.append(researcher_information_p_id_result[a]['n'].get("publication_id"))
                publication_id_general.append(list_of_researcher_p_id)
       


       #Query for getting researcher publication name
       for i in range(len(publication_id_general)): 
           list_of_researcher_p_name=[]       
           for j in range(len(publication_id_general[i])):
                query_for_researcher_publication_name=("MATCH(m:Researcher)-[r:PUBLICATION_WRITER]->(n:Publications) WHERE m.Researcher_ID='"+str(researcher_id_general_copy[0][i])+"' AND n.publication_id='"+str(publication_id_general[i][j])+"' RETURN (n)")
                query_result_for_researcher_p_name_information=conn.query(query_for_researcher_publication_name,db="yazlab")
                researcher_information_p_name_result=[record for record in query_result_for_researcher_p_name_information]
                        
                for k in range(len(researcher_information_p_name_result)):
                   list_of_researcher_p_name.append(researcher_information_p_name_result [k]['n'].get("publication_name"))
                
                    
           publication_name_general.append(list_of_researcher_p_name)
           
 
       #Query for getting researcher publication year
       for i in range(len(publication_id_general)): 
           list_of_researcher_p_year=[]        
           for j in range(len(publication_id_general[i])):
                query_for_researcher_p_year=("MATCH(m:Researcher)-[r:PUBLICATION_WRITER]->(n:Publications) WHERE m.Researcher_ID='"+str(researcher_id_general_copy[0][i])+"' AND n.publication_id='"+str(publication_id_general[i][j])+"' RETURN (n)")
                query_result_for_researcher_p_year_information=conn.query(query_for_researcher_p_year,db="yazlab")
                researcher_information_p_year_result=[record for record in query_result_for_researcher_p_year_information]
                        
                for k in range(len(researcher_information_p_year_result)):
                    list_of_researcher_p_year.append(researcher_information_p_year_result [k]['n'].get("publication_year"))
                    
           publication_year_general.append(list_of_researcher_p_year)
        

       
       #Query for getting researcher publication place
       for i in range(len(publication_id_general)): 
           list_of_researcher_p_place=[]        
           for j in range(len(publication_id_general[i])):       
                query_for_researcher_p_place=("MATCH(m:Researcher)-[r:PUBLICATION_WRITER]->(n:Publications) WHERE m.Researcher_ID='"+str(researcher_id_general_copy[0][i])+"' AND n.publication_id='"+str(publication_id_general[i][j])+"' RETURN (n)")
                query_result_for_researcher_p_place_information=conn.query(query_for_researcher_p_place,db="yazlab")
                researcher_information_p_place_result=[record for record in query_result_for_researcher_p_place_information]       
                for k in range(len(researcher_information_p_place_result)):
                      list_of_researcher_p_place.append(researcher_information_p_place_result [k]['n'].get("publication_place"))
           publication_place_general.append(list_of_researcher_p_place)

       
       #Query for getting researcher publication type
       for i in range(len(publication_id_general)): 
           list_of_researcher_p_type=[]        
           for j in range(len(publication_id_general[i])):       
                query_for_researcher_p_type=("MATCH(m:Researcher)-[r:PUBLICATION_WRITER]->(n:Publications) WHERE m.Researcher_ID='"+str(researcher_id_general_copy[0][i])+"' AND n.publication_id='"+str(publication_id_general[i][j])+"' RETURN (n)")
                query_result_for_researcher_p_type_information=conn.query(query_for_researcher_p_type,db="yazlab")
                researcher_information_p_type_result=[record for record in query_result_for_researcher_p_type_information]       
                for k in range(len(researcher_information_p_type_result)):
                      list_of_researcher_p_type.append(researcher_information_p_type_result [k]['n'].get("publication_type"))
           publication_type_general.append(list_of_researcher_p_type)
      

    if(name!="" and surname!="" and  p_name=="" and p_year==""):
       #Query For Researcher id
       query_for_researcher_id=("MATCH(n:Researcher) WHERE n.name='"+str(name)+"'and n.surname='"+str(surname)+"' RETURN n")
       query_result_for_researcher_id=conn.query(query_for_researcher_id, db='yazlab') 
       researcher_id_result=[record for record in query_result_for_researcher_id]
       list_of_researcher_id=[]
       researcher_id_general_copy=[]
       for i in range(len(researcher_id_result)):
           list_of_researcher_id.append(researcher_id_result [i]['n'].get("Researcher_ID"))
       researcher_id_general_copy.append(list_of_researcher_id)
       
       who_writed_teammate_general=[] 
       list_of_publication_id=[]
       list_of_publication_id_general=[]
       p_name_list=[]
       list_of_researcher_name=[]
       list_of_researcher_surname=[]
       name_general=[]
       surname_general=[]
       researcher_id_general=[]
       teammate_id_general=[]
       publication_id_general=[]
       publication_name_general=[]
       publication_year_general=[]
       publication_place_general=[]
       publication_type_general=[]
       researcher_teammate_name_general=[]
       researcher_teammate_surname_general=[]
       copy_list_of_researcher_id_control=[]  
       #Query for getting researcher name and surname
       for i in researcher_id_general_copy:
           list_of_researcher_name=[]
           list_of_researcher_surname=[]
           for j in i:        
                query_for_researcher_id=("MATCH(n:Researcher) WHERE n.Researcher_ID='"+str(j)+"' RETURN (n)")
                query_result_for_researcher_information=conn.query(query_for_researcher_id,db="yazlab")
                researcher_information_result=[record for record in query_result_for_researcher_information]
                for k in range(len(researcher_information_result)):
                   list_of_researcher_name.append(researcher_information_result[k]['n'].get("name"))
                   list_of_researcher_surname.append(researcher_information_result[k]['n'].get("surname"))
           name_general.append(list_of_researcher_name)
           surname_general.append(list_of_researcher_surname)
           

                
       #Query for getting researcher teammate id , name , surname
       for i in researcher_id_general_copy:         
           for j in i:       
                query_for_researcher_teammate_id=("MATCH(m:Researcher)-[r:WORKS_COLLABORATIVELY]->(n:Researcher) WHERE m.Researcher_ID='"+str(j)+"' RETURN (n)")
                query_result_for_researcher_teammate_information=conn.query(query_for_researcher_teammate_id,db="yazlab")
                researcher_information_teammate_result=[record for record in query_result_for_researcher_teammate_information]
                list_of_researcher_teammate_id=[]
                list_of_researcher_teammate_name=[]
                list_of_researcher_teammate_surname=[]
                list_of_researcher_teammate=[]        
                for k in range(len(researcher_information_teammate_result)):
                   teammate_id_holder=researcher_information_teammate_result [k]['n'].get("Researcher_ID")
                   query_for_reseacher_teammate_name_surname=("MATCH(n:Researcher) WHERE n.Researcher_ID='"+str(teammate_id_holder)+"' RETURN (n)")
                   query_result_for_researcher_teammate_name_surname_information=conn.query(query_for_reseacher_teammate_name_surname,db="yazlab")
                   researcher_information_teammate_name_surname_result=[record for record in query_result_for_researcher_teammate_name_surname_information]
                   list_of_researcher_teammate_name.append(researcher_information_teammate_name_surname_result [0]['n'].get("name"))
                   list_of_researcher_teammate_surname.append(researcher_information_teammate_name_surname_result [0]['n'].get("surname"))
                   name_surname_holder=researcher_information_teammate_name_surname_result [0]['n'].get("name")+" "+researcher_information_teammate_name_surname_result [0]['n'].get("surname")
                   list_of_researcher_teammate_id.append(researcher_information_teammate_result [k]['n'].get("Researcher_ID"))
                   list_of_researcher_teammate.append(name_surname_holder)
                teammate_id_general.append(list_of_researcher_teammate_id)
                researcher_teammate_name_general.append(list_of_researcher_teammate_name)
                researcher_teammate_surname_general.append(list_of_researcher_teammate_surname)
                who_writed_teammate_general.append(list_of_researcher_teammate)
                


        #Query for getting researcher publication id
       for i in researcher_id_general_copy:         
           for j in i:       
                query_for_researcher_p_id=("MATCH(m:Researcher)-[r:PUBLICATION_WRITER]->(n:Publications) WHERE m.Researcher_ID='"+str(j)+"' RETURN (n)")
                query_result_for_researcher_p_id_information=conn.query(query_for_researcher_p_id,db="yazlab")
                researcher_information_p_id_result=[record for record in query_result_for_researcher_p_id_information]       
                list_of_researcher_p_id=[]
                for a in range(len(researcher_information_p_id_result)):
                    list_of_researcher_p_id.append(researcher_information_p_id_result[a]['n'].get("publication_id"))
                publication_id_general.append(list_of_researcher_p_id)
       


       #Query for getting researcher publication name
       for i in range(len(publication_id_general)): 
           list_of_researcher_p_name=[]       
           for j in range(len(publication_id_general[i])):
                query_for_researcher_publication_name=("MATCH(m:Researcher)-[r:PUBLICATION_WRITER]->(n:Publications) WHERE m.Researcher_ID='"+str(researcher_id_general_copy[0][i])+"' AND n.publication_id='"+str(publication_id_general[i][j])+"' RETURN (n)")
                query_result_for_researcher_p_name_information=conn.query(query_for_researcher_publication_name,db="yazlab")
                researcher_information_p_name_result=[record for record in query_result_for_researcher_p_name_information]
                        
                for k in range(len(researcher_information_p_name_result)):
                   list_of_researcher_p_name.append(researcher_information_p_name_result [k]['n'].get("publication_name"))
                
                    
           publication_name_general.append(list_of_researcher_p_name)
           

       #Query for getting researcher publication year
       for i in range(len(publication_id_general)): 
           list_of_researcher_p_year=[]        
           for j in range(len(publication_id_general[i])):
                query_for_researcher_p_year=("MATCH(m:Researcher)-[r:PUBLICATION_WRITER]->(n:Publications) WHERE m.Researcher_ID='"+str(researcher_id_general_copy[0][i])+"' AND n.publication_id='"+str(publication_id_general[i][j])+"' RETURN (n)")
                query_result_for_researcher_p_year_information=conn.query(query_for_researcher_p_year,db="yazlab")
                researcher_information_p_year_result=[record for record in query_result_for_researcher_p_year_information]
                        
                for k in range(len(researcher_information_p_year_result)):
                    list_of_researcher_p_year.append(researcher_information_p_year_result [k]['n'].get("publication_year"))
                    
           publication_year_general.append(list_of_researcher_p_year)
        

       
       #Query for getting researcher publication place
       for i in range(len(publication_id_general)): 
           list_of_researcher_p_place=[]        
           for j in range(len(publication_id_general[i])):       
                query_for_researcher_p_place=("MATCH(m:Researcher)-[r:PUBLICATION_WRITER]->(n:Publications) WHERE m.Researcher_ID='"+str(researcher_id_general_copy[0][i])+"' AND n.publication_id='"+str(publication_id_general[i][j])+"' RETURN (n)")
                query_result_for_researcher_p_place_information=conn.query(query_for_researcher_p_place,db="yazlab")
                researcher_information_p_place_result=[record for record in query_result_for_researcher_p_place_information]       
                for k in range(len(researcher_information_p_place_result)):
                      list_of_researcher_p_place.append(researcher_information_p_place_result [k]['n'].get("publication_place"))
           publication_place_general.append(list_of_researcher_p_place)

       
       #Query for getting researcher publication type
       for i in range(len(publication_id_general)): 
           list_of_researcher_p_type=[]        
           for j in range(len(publication_id_general[i])):       
                query_for_researcher_p_type=("MATCH(m:Researcher)-[r:PUBLICATION_WRITER]->(n:Publications) WHERE m.Researcher_ID='"+str(researcher_id_general_copy[0][i])+"' AND n.publication_id='"+str(publication_id_general[i][j])+"' RETURN (n)")
                query_result_for_researcher_p_type_information=conn.query(query_for_researcher_p_type,db="yazlab")
                researcher_information_p_type_result=[record for record in query_result_for_researcher_p_type_information]       
                for k in range(len(researcher_information_p_type_result)):
                      list_of_researcher_p_type.append(researcher_information_p_type_result [k]['n'].get("publication_type"))
           publication_type_general.append(list_of_researcher_p_type)
      

    if(p_name!="" and p_year!="" and name=="" and surname==""):
       #Query For Publications
       query_for_publicaton_id=("MATCH(n:Publications) WHERE n.publication_year='"+str(p_year)+"' and n.publication_name='"+str(p_name)+"' RETURN n")
       query_result_for_publicaton_id=conn.query(query_for_publicaton_id, db='yazlab')
                                   
       
       who_writed_teammate_general=[] 
       list_of_publication_id=[]
       list_of_publication_id_general=[]
       p_name_list=[]
       list_of_researcher_name=[]
       list_of_researcher_surname=[]
       name_general=[]
       surname_general=[]
       list_of_researcher_id=[]
       researcher_id_general_copy=[]
       researcher_id_general=[]
       teammate_id_general=[]
       publication_id_general=[]
       publication_name_general=[]
       publication_year_general=[]
       publication_place_general=[]
       publication_type_general=[]
       researcher_teammate_name_general=[]
       researcher_teammate_surname_general=[]
       copy_list_of_researcher_id_control=[]  

       for i in range(len(query_result_for_publicaton_id)):
           publication_id_result=[record for record in query_result_for_publicaton_id]
           list_of_publication_id.append(publication_id_result[i]['n'].get("publication_id"))
       list_of_publication_id_general.append(list_of_publication_id)
    #Query for getting year
       for i,k in zip(range(len(list_of_publication_id_general)),list_of_publication_id_general):
           for j in k:
               query_for_p_name=("MATCH(n:Publications) WHERE n.publication_id='"+str(j)+"' RETURN n")
               query_result_for_p_name=conn.query(query_for_p_name, db='yazlab')
               p_name_result=[record for record in query_result_for_p_name]
               p_name_list.append(p_name_result[0]['n'].get("publication_name")) 

    #Query for getting researcher id
       for i in list_of_publication_id_general:  
           
           for j in i:
               query_for_researcher_id=("MATCH(n:Researcher)-[r:PUBLICATION_WRITER]->(m:Publications) WHERE m.publication_id='"+str(j)+"' RETURN (n)")
               query_result_for_researcher_id=conn.query(query_for_researcher_id, db='yazlab')
               researcher_result=[record for record in query_result_for_researcher_id]
               list_of_researcher_id=[]
               
               for k in range(len(researcher_result)):
                   list_of_researcher_id.append(researcher_result[k]['n'].get("Researcher_ID"))

               researcher_id_general.append(list_of_researcher_id)
     
              
 
       #If there is the same person, do not reduce them to one person 
       for x in range(len(researcher_id_general)):
           
           for y in range(len(researcher_id_general[x])):
               if researcher_id_general[x][y] not in copy_list_of_researcher_id_control:
                   copy_list_of_researcher_id_control.append(researcher_id_general[x][y])
               
       researcher_id_general_copy.append(copy_list_of_researcher_id_control)

       #Query for getting researcher name and surname
       for i in researcher_id_general_copy:
           list_of_researcher_name=[]
           list_of_researcher_surname=[]
           for j in i:        
                query_for_researcher_id=("MATCH(n:Researcher) WHERE n.Researcher_ID='"+str(j)+"' RETURN (n)")
                query_result_for_researcher_information=conn.query(query_for_researcher_id,db="yazlab")
                researcher_information_result=[record for record in query_result_for_researcher_information]
                for k in range(len(researcher_information_result)):
                   list_of_researcher_name.append(researcher_information_result[k]['n'].get("name"))
                   list_of_researcher_surname.append(researcher_information_result[k]['n'].get("surname"))
           name_general.append(list_of_researcher_name)
           surname_general.append(list_of_researcher_surname)
           

                
       #Query for getting researcher teammate id , name , surname
       for i in researcher_id_general_copy:         
           for j in i:       
                query_for_researcher_teammate_id=("MATCH(m:Researcher)-[r:WORKS_COLLABORATIVELY]->(n:Researcher) WHERE m.Researcher_ID='"+str(j)+"' RETURN (n)")
                query_result_for_researcher_teammate_information=conn.query(query_for_researcher_teammate_id,db="yazlab")
                researcher_information_teammate_result=[record for record in query_result_for_researcher_teammate_information]
                list_of_researcher_teammate_id=[]
                list_of_researcher_teammate_name=[]
                list_of_researcher_teammate_surname=[]
                list_of_researcher_teammate=[]        
                for k in range(len(researcher_information_teammate_result)):
                   teammate_id_holder=researcher_information_teammate_result [k]['n'].get("Researcher_ID")
                   query_for_reseacher_teammate_name_surname=("MATCH(n:Researcher) WHERE n.Researcher_ID='"+str(teammate_id_holder)+"' RETURN (n)")
                   query_result_for_researcher_teammate_name_surname_information=conn.query(query_for_reseacher_teammate_name_surname,db="yazlab")
                   researcher_information_teammate_name_surname_result=[record for record in query_result_for_researcher_teammate_name_surname_information]
                   list_of_researcher_teammate_name.append(researcher_information_teammate_name_surname_result [0]['n'].get("name"))
                   list_of_researcher_teammate_surname.append(researcher_information_teammate_name_surname_result [0]['n'].get("surname"))
                   name_surname_holder=researcher_information_teammate_name_surname_result [0]['n'].get("name")+" "+researcher_information_teammate_name_surname_result [0]['n'].get("surname")
                   list_of_researcher_teammate_id.append(researcher_information_teammate_result [k]['n'].get("Researcher_ID"))
                   list_of_researcher_teammate.append(name_surname_holder)
                teammate_id_general.append(list_of_researcher_teammate_id)
                researcher_teammate_name_general.append(list_of_researcher_teammate_name)
                researcher_teammate_surname_general.append(list_of_researcher_teammate_surname)
                who_writed_teammate_general.append(list_of_researcher_teammate)
                


        #Query for getting researcher publication id
       for i in researcher_id_general_copy:         
           for j in i:       
                query_for_researcher_p_id=("MATCH(m:Researcher)-[r:PUBLICATION_WRITER]->(n:Publications) WHERE m.Researcher_ID='"+str(j)+"' RETURN (n)")
                query_result_for_researcher_p_id_information=conn.query(query_for_researcher_p_id,db="yazlab")
                researcher_information_p_id_result=[record for record in query_result_for_researcher_p_id_information]       
                list_of_researcher_p_id=[]
                for a in range(len(researcher_information_p_id_result)):
                    list_of_researcher_p_id.append(researcher_information_p_id_result[a]['n'].get("publication_id"))
                publication_id_general.append(list_of_researcher_p_id)
       


       #Query for getting researcher publication name
       for i in range(len(publication_id_general)): 
           list_of_researcher_p_name=[]       
           for j in range(len(publication_id_general[i])):
                query_for_researcher_publication_name=("MATCH(m:Researcher)-[r:PUBLICATION_WRITER]->(n:Publications) WHERE m.Researcher_ID='"+str(researcher_id_general_copy[0][i])+"' AND n.publication_id='"+str(publication_id_general[i][j])+"' RETURN (n)")
                query_result_for_researcher_p_name_information=conn.query(query_for_researcher_publication_name,db="yazlab")
                researcher_information_p_name_result=[record for record in query_result_for_researcher_p_name_information]
                        
                for k in range(len(researcher_information_p_name_result)):
                   list_of_researcher_p_name.append(researcher_information_p_name_result [k]['n'].get("publication_name"))
                
                    
           publication_name_general.append(list_of_researcher_p_name)
           

       #Query for getting researcher publication year
       for i in range(len(publication_id_general)): 
           list_of_researcher_p_year=[]        
           for j in range(len(publication_id_general[i])):
                query_for_researcher_p_year=("MATCH(m:Researcher)-[r:PUBLICATION_WRITER]->(n:Publications) WHERE m.Researcher_ID='"+str(researcher_id_general_copy[0][i])+"' AND n.publication_id='"+str(publication_id_general[i][j])+"' RETURN (n)")
                query_result_for_researcher_p_year_information=conn.query(query_for_researcher_p_year,db="yazlab")
                researcher_information_p_year_result=[record for record in query_result_for_researcher_p_year_information]
                        
                for k in range(len(researcher_information_p_year_result)):
                    list_of_researcher_p_year.append(researcher_information_p_year_result [k]['n'].get("publication_year"))
                    
           publication_year_general.append(list_of_researcher_p_year)
        

       
       #Query for getting researcher publication place
       for i in range(len(publication_id_general)): 
           list_of_researcher_p_place=[]        
           for j in range(len(publication_id_general[i])):       
                query_for_researcher_p_place=("MATCH(m:Researcher)-[r:PUBLICATION_WRITER]->(n:Publications) WHERE m.Researcher_ID='"+str(researcher_id_general_copy[0][i])+"' AND n.publication_id='"+str(publication_id_general[i][j])+"' RETURN (n)")
                query_result_for_researcher_p_place_information=conn.query(query_for_researcher_p_place,db="yazlab")
                researcher_information_p_place_result=[record for record in query_result_for_researcher_p_place_information]       
                for k in range(len(researcher_information_p_place_result)):
                      list_of_researcher_p_place.append(researcher_information_p_place_result [k]['n'].get("publication_place"))
           publication_place_general.append(list_of_researcher_p_place)

       
       #Query for getting researcher publication type
       for i in range(len(publication_id_general)): 
           list_of_researcher_p_type=[]        
           for j in range(len(publication_id_general[i])):       
                query_for_researcher_p_type=("MATCH(m:Researcher)-[r:PUBLICATION_WRITER]->(n:Publications) WHERE m.Researcher_ID='"+str(researcher_id_general_copy[0][i])+"' AND n.publication_id='"+str(publication_id_general[i][j])+"' RETURN (n)")
                query_result_for_researcher_p_type_information=conn.query(query_for_researcher_p_type,db="yazlab")
                researcher_information_p_type_result=[record for record in query_result_for_researcher_p_type_information]       
                for k in range(len(researcher_information_p_type_result)):
                      list_of_researcher_p_type.append(researcher_information_p_type_result [k]['n'].get("publication_type"))
           publication_type_general.append(list_of_researcher_p_type)
      

    if(p_year!=""):
       #Query For Publications
       query_for_publicaton_id=("MATCH(n:Publications) WHERE n.publication_year='"+str(p_year)+"' RETURN n")
       query_result_for_publicaton_id=conn.query(query_for_publicaton_id, db='yazlab')
                                   
       if(p_name!=""):
           query_for_publicaton_id=("MATCH(n:Publications) WHERE n.publication_name='"+str(p_name)+"' AND n.publication_year='"+str(p_year)+"' RETURN n")
           query_result_for_publicaton_id=conn.query(query_for_publicaton_id, db='yazlab')

       who_writed_teammate_general=[] 
       list_of_publication_id=[]
       list_of_publication_id_general=[]
       p_name_list=[]
       list_of_researcher_name=[]
       list_of_researcher_surname=[]
       name_general=[]
       surname_general=[]
       list_of_researcher_id=[]
       researcher_id_general_copy=[]
       researcher_id_general=[]
       teammate_id_general=[]
       publication_id_general=[]
       publication_name_general=[]
       publication_year_general=[]
       publication_place_general=[]
       publication_type_general=[]
       researcher_teammate_name_general=[]
       researcher_teammate_surname_general=[]
       copy_list_of_researcher_id_control=[]  

       for i in range(len(query_result_for_publicaton_id)):
           publication_id_result=[record for record in query_result_for_publicaton_id]
           list_of_publication_id.append(publication_id_result[i]['n'].get("publication_id"))
       list_of_publication_id_general.append(list_of_publication_id)

    #Query for getting year
       for i,k in zip(range(len(list_of_publication_id_general)),list_of_publication_id_general):
           for j in k:
               query_for_p_name=("MATCH(n:Publications) WHERE n.publication_id='"+str(j)+"' RETURN n")
               query_result_for_p_name=conn.query(query_for_p_name, db='yazlab')
               p_name_result=[record for record in query_result_for_p_name]
               p_name_list.append(p_name_result[0]['n'].get("publication_name")) 

    #Query for getting researcher id
       for i in list_of_publication_id_general:  
           
           for j in i:
               query_for_researcher_id=("MATCH(n:Researcher)-[r:PUBLICATION_WRITER]->(m:Publications) WHERE m.publication_id='"+str(j)+"' RETURN (n)")
               query_result_for_researcher_id=conn.query(query_for_researcher_id, db='yazlab')
               researcher_result=[record for record in query_result_for_researcher_id]
               list_of_researcher_id=[]
               
               for k in range(len(researcher_result)):
                   list_of_researcher_id.append(researcher_result[k]['n'].get("Researcher_ID"))

               researcher_id_general.append(list_of_researcher_id)
     
              

       #If there is the same person, do not reduce them to one person 
       for x in range(len(researcher_id_general)):
           
           for y in range(len(researcher_id_general[x])):
               if researcher_id_general[x][y] not in copy_list_of_researcher_id_control:
                   copy_list_of_researcher_id_control.append(researcher_id_general[x][y])
               
       researcher_id_general_copy.append(copy_list_of_researcher_id_control)

       if(surname!="" and name==""):
           list_of_researcher_id=[]
           researcher_id_general_copy=[]
           query_for_researcher_id=("MATCH(n:Researcher) WHERE n.surname='"+str(surname)+"' RETURN n")
           query_result_for_researcher_id=conn.query(query_for_researcher_id, db='yazlab') 
           researcher_id_result=[record for record in query_result_for_researcher_id]        
           for i in range(len(researcher_id_result)):
                list_of_researcher_id.append(researcher_id_result [i]['n'].get("Researcher_ID"))
           researcher_id_general_copy.append(list_of_researcher_id)
           

       if(name!="" and surname==""):
           list_of_researcher_id=[]
           researcher_id_general_copy=[]
           query_for_researcher_id=("MATCH(n:Researcher) WHERE n.name='"+str(name)+"' RETURN n")
           query_result_for_researcher_id=conn.query(query_for_researcher_id, db='yazlab') 
           researcher_id_result=[record for record in query_result_for_researcher_id]
           for i in range(len(researcher_id_result)):
                list_of_researcher_id.append(researcher_id_result [i]['n'].get("Researcher_ID"))
           researcher_id_general_copy.append(list_of_researcher_id)

       if(name!="" and surname!=""):
           list_of_researcher_id=[]
           researcher_id_general_copy=[]
           query_for_researcher_id=("MATCH(n:Researcher) WHERE n.name='"+str(name)+"'AND n.surname='"+str(surname)+"' RETURN n")
           query_result_for_researcher_id=conn.query(query_for_researcher_id, db='yazlab') 
           researcher_id_result=[record for record in query_result_for_researcher_id]
           for i in range(len(researcher_id_result)):
                list_of_researcher_id.append(researcher_id_result [i]['n'].get("Researcher_ID"))
           researcher_id_general_copy.append(list_of_researcher_id)

       #Query for getting researcher name and surname
       for i in researcher_id_general_copy:
           list_of_researcher_name=[]
           list_of_researcher_surname=[]
           for j in i:        
                query_for_researcher_id=("MATCH(n:Researcher) WHERE n.Researcher_ID='"+str(j)+"' RETURN (n)")
                query_result_for_researcher_information=conn.query(query_for_researcher_id,db="yazlab")
                researcher_information_result=[record for record in query_result_for_researcher_information]
                for k in range(len(researcher_information_result)):
                   list_of_researcher_name.append(researcher_information_result[k]['n'].get("name"))
                   list_of_researcher_surname.append(researcher_information_result[k]['n'].get("surname"))
           name_general.append(list_of_researcher_name)
           surname_general.append(list_of_researcher_surname)
           

                
       #Query for getting researcher teammate id , name , surname
       for i in researcher_id_general_copy:         
           for j in i:       
                query_for_researcher_teammate_id=("MATCH(m:Researcher)-[r:WORKS_COLLABORATIVELY]->(n:Researcher) WHERE m.Researcher_ID='"+str(j)+"' RETURN (n)")
                query_result_for_researcher_teammate_information=conn.query(query_for_researcher_teammate_id,db="yazlab")
                researcher_information_teammate_result=[record for record in query_result_for_researcher_teammate_information]
                list_of_researcher_teammate_id=[]
                list_of_researcher_teammate_name=[]
                list_of_researcher_teammate_surname=[]
                list_of_researcher_teammate=[]        
                for k in range(len(researcher_information_teammate_result)):
                   teammate_id_holder=researcher_information_teammate_result [k]['n'].get("Researcher_ID")
                   query_for_reseacher_teammate_name_surname=("MATCH(n:Researcher) WHERE n.Researcher_ID='"+str(teammate_id_holder)+"' RETURN (n)")
                   query_result_for_researcher_teammate_name_surname_information=conn.query(query_for_reseacher_teammate_name_surname,db="yazlab")
                   researcher_information_teammate_name_surname_result=[record for record in query_result_for_researcher_teammate_name_surname_information]
                   list_of_researcher_teammate_name.append(researcher_information_teammate_name_surname_result [0]['n'].get("name"))
                   list_of_researcher_teammate_surname.append(researcher_information_teammate_name_surname_result [0]['n'].get("surname"))
                   name_surname_holder=researcher_information_teammate_name_surname_result [0]['n'].get("name")+" "+researcher_information_teammate_name_surname_result [0]['n'].get("surname")
                   list_of_researcher_teammate_id.append(researcher_information_teammate_result [k]['n'].get("Researcher_ID"))
                   list_of_researcher_teammate.append(name_surname_holder)
                teammate_id_general.append(list_of_researcher_teammate_id)
                researcher_teammate_name_general.append(list_of_researcher_teammate_name)
                researcher_teammate_surname_general.append(list_of_researcher_teammate_surname)
                who_writed_teammate_general.append(list_of_researcher_teammate)
                


        #Query for getting researcher publication id
       for i in researcher_id_general_copy:         
           for j in i:       
                query_for_researcher_p_id=("MATCH(m:Researcher)-[r:PUBLICATION_WRITER]->(n:Publications) WHERE m.Researcher_ID='"+str(j)+"' RETURN (n)")
                query_result_for_researcher_p_id_information=conn.query(query_for_researcher_p_id,db="yazlab")
                researcher_information_p_id_result=[record for record in query_result_for_researcher_p_id_information]       
                list_of_researcher_p_id=[]
                for a in range(len(researcher_information_p_id_result)):
                    list_of_researcher_p_id.append(researcher_information_p_id_result[a]['n'].get("publication_id"))
                publication_id_general.append(list_of_researcher_p_id)
       


       counter=0
       for i in range(len(publication_id_general)):
           for j in range(len(publication_id_general[i])):
               if publication_id_general[i][j] in list_of_publication_id:
                   counter+=1
       if(counter==0):
            researcher_id_general_copy=[]
            #Query for getting researcher publication name
       if(counter!=0):
            for i in range(len(publication_id_general)): 
                list_of_researcher_p_name=[]       
                for j in range(len(publication_id_general[i])):
                        query_for_researcher_publication_name=("MATCH(m:Researcher)-[r:PUBLICATION_WRITER]->(n:Publications) WHERE m.Researcher_ID='"+str(researcher_id_general_copy[0][i])+"' AND n.publication_id='"+str(publication_id_general[i][j])+"' RETURN (n)")
                        query_result_for_researcher_p_name_information=conn.query(query_for_researcher_publication_name,db="yazlab")
                        researcher_information_p_name_result=[record for record in query_result_for_researcher_p_name_information]
                                
                        for k in range(len(researcher_information_p_name_result)):
                                list_of_researcher_p_name.append(researcher_information_p_name_result [k]['n'].get("publication_name"))
                        
                            
                publication_name_general.append(list_of_researcher_p_name)


            #Query for getting researcher publication year
            for i in range(len(publication_id_general)): 
                list_of_researcher_p_year=[]        
                for j in range(len(publication_id_general[i])):
                        query_for_researcher_p_year=("MATCH(m:Researcher)-[r:PUBLICATION_WRITER]->(n:Publications) WHERE m.Researcher_ID='"+str(researcher_id_general_copy[0][i])+"' AND n.publication_id='"+str(publication_id_general[i][j])+"' RETURN (n)")
                        query_result_for_researcher_p_year_information=conn.query(query_for_researcher_p_year,db="yazlab")
                        researcher_information_p_year_result=[record for record in query_result_for_researcher_p_year_information]
                                
                        for k in range(len(researcher_information_p_year_result)):
                            list_of_researcher_p_year.append(researcher_information_p_year_result [k]['n'].get("publication_year"))
                            
                publication_year_general.append(list_of_researcher_p_year)
                

            
            #Query for getting researcher publication place
            for i in range(len(publication_id_general)): 
                list_of_researcher_p_place=[]        
                for j in range(len(publication_id_general[i])):       
                        query_for_researcher_p_place=("MATCH(m:Researcher)-[r:PUBLICATION_WRITER]->(n:Publications) WHERE m.Researcher_ID='"+str(researcher_id_general_copy[0][i])+"' AND n.publication_id='"+str(publication_id_general[i][j])+"' RETURN (n)")
                        query_result_for_researcher_p_place_information=conn.query(query_for_researcher_p_place,db="yazlab")
                        researcher_information_p_place_result=[record for record in query_result_for_researcher_p_place_information]       
                        for k in range(len(researcher_information_p_place_result)):
                            list_of_researcher_p_place.append(researcher_information_p_place_result [k]['n'].get("publication_place"))
                publication_place_general.append(list_of_researcher_p_place)

            
            #Query for getting researcher publication type
            for i in range(len(publication_id_general)): 
                list_of_researcher_p_type=[]        
                for j in range(len(publication_id_general[i])):       
                        query_for_researcher_p_type=("MATCH(m:Researcher)-[r:PUBLICATION_WRITER]->(n:Publications) WHERE m.Researcher_ID='"+str(researcher_id_general_copy[0][i])+"' AND n.publication_id='"+str(publication_id_general[i][j])+"' RETURN (n)")
                        query_result_for_researcher_p_type_information=conn.query(query_for_researcher_p_type,db="yazlab")
                        researcher_information_p_type_result=[record for record in query_result_for_researcher_p_type_information]       
                        for k in range(len(researcher_information_p_type_result)):
                            list_of_researcher_p_type.append(researcher_information_p_type_result [k]['n'].get("publication_type"))
                publication_type_general.append(list_of_researcher_p_type)
            



    who_writed_publications=[]
    who_writed_publications_surname=[]
    who_writed_publications_id_copy=[]
    if(surname!="" or name!="" or p_name!="" or p_year!=""):
        for i,j in zip(name_general,surname_general):
            for x,y in zip(i,j):
                who_writed_publications.append(x)
                who_writed_publications_surname.append(y)
        for i in researcher_id_general_copy:
            for j in i:
                who_writed_publications_id_copy.append(j)
        

    if(surname=="" and name=="" and p_name=="" and p_year==""):
         who_writed_publications=[]
         who_writed_publications_surname=[]
         researcher_id_general_copy=[]
         who_writed_teammate_general=[]
         publication_name_general=[]
         publication_year_general=[]
         publication_place_general=[]
         publication_type_general=[]
    
    
    
    return who_writed_publications_id_copy,who_writed_publications,who_writed_publications_surname,who_writed_teammate_general,publication_name_general,publication_year_general,publication_place_general,publication_type_general,teammate_id_general

def graph_query(id):
     r_query_of_graph=("MATCH(m:Researcher) WHERE m.Researcher_ID='"+str(id)+"' RETURN (m) ")
     researcher_query_result_for_graph=conn.query( r_query_of_graph, db='yazlab')
     researcher_result=[record for record in researcher_query_result_for_graph]

     r_name = researcher_result[0]['m'].get('name')
     r_surname=researcher_result[0]['m'].get('surname')
     r_publication_name=researcher_result[0]['m'].get('publication_name')

     r_query_for_node_id=("MATCH(m:Researcher) WHERE m.Researcher_ID='"+str(id)+"' RETURN (ID(m))")
     r_query_node_id_information=conn.query(r_query_for_node_id, db='yazlab')
     
     r_node_id=r_query_node_id_information[0][0]
     p_node_id=[]
     r_teammate_node_id=[]
     type_node_id=[]        
     
     query_for_researcher_p_id=("MATCH(m:Researcher)-[r:PUBLICATION_WRITER]->(n:Publications) WHERE m.Researcher_ID='"+str(id)+"' RETURN (n)")
     query_result_for_researcher_p_id_information=conn.query(query_for_researcher_p_id,db="yazlab")
     researcher_information_p_id_result=[record for record in query_result_for_researcher_p_id_information]       
     p_publication_id=[]
     for a in range(len(researcher_information_p_id_result)):
            p_publication_id.append(researcher_information_p_id_result[a]['n'].get("publication_id"))
     p_publication_name=[]
     p_publication_place=[]
     p_publication_type=[]
     p_publication_year=[]
     for i in p_publication_id:
        
        p_query_of_graph=("MATCH(n:Publications) WHERE n.publication_id='"+str(i)+"' RETURN (n) ")
        publication_query_result_for_graph=conn.query(p_query_of_graph, db='yazlab')
        publication_result=[record for record in publication_query_result_for_graph]
        p_query_for_node_id=("MATCH(n:Publications) WHERE n.publication_id='"+str(i)+"' RETURN (ID(n))")
        query_result_for_p_node_id_information=conn.query(p_query_for_node_id,db="yazlab")
        p_node_id.append(query_result_for_p_node_id_information[0][0])

        p_publication_name.append(publication_result[0]['n'].get("publication_name"))
        p_publication_place.append(publication_result[0]['n'].get("publication_place"))
        p_publication_type.append(publication_result[0]['n'].get("publication_type"))
        p_publication_year.append(publication_result[0]['n'].get("publication_year"))

     t_type_id=[]
     for i in p_publication_id:
        query_for_researcher_t_id=("MATCH(m:Publications)-[r:PUBLISHED]->(n:Type) WHERE m.publication_id='"+str(i)+"' RETURN (n)")
        query_result_for_researcher_t_id_information=conn.query(query_for_researcher_t_id,db="yazlab")
        researcher_information_t_id_result=[record for record in query_result_for_researcher_t_id_information]
        t_type_id.append(researcher_information_t_id_result[0]['n'].get("Type_id"))    
    


     t_type_type=[]
     t_type_place=[]
     for i in t_type_id:
        t_query_of_graph=("MATCH(n:Type) WHERE n.Type_id='"+str(i)+"' RETURN (n) ")
        type_query_result_for_graph=conn.query(t_query_of_graph, db='yazlab')
        type_result=[record for record in type_query_result_for_graph]
        t_query_for_node_id=("MATCH(n:Type) WHERE n.Type_id='"+str(i)+"' RETURN ID(n) ")
        type_query_result_for_node_id=conn.query(t_query_for_node_id, db='yazlab')
        type_node_id.append(type_query_result_for_node_id[0][0])
        t_type_place.append(type_result[0]['n'].get("publication_place"))
        t_type_type.append(type_result[0]['n'].get("publication_type"))
    

     
     query_for_researcher_teammate_id=("MATCH(m:Researcher)-[r:WORKS_COLLABORATIVELY]->(n:Researcher) WHERE m.Researcher_ID='"+str(id)+"' RETURN (n)")
     query_result_for_researcher_teammate_information=conn.query(query_for_researcher_teammate_id,db="yazlab")
     researcher_information_teammate_result=[record for record in query_result_for_researcher_teammate_information]
     r_teammate_id=[]
     r_teammate_name=[]
     r_teammate_surname=[]
     r_teammate_publication_name=[]
     for i in range(len(researcher_information_teammate_result)):
         r_teammate_id.append(researcher_information_teammate_result[i]['n'].get('Researcher_ID'))
     
     for i in r_teammate_id:
         query_for_teammate_graph=("MATCH(m:Researcher) WHERE m.Researcher_ID='"+str(i)+"' RETURN (m) ")
         query_for_teammate_graph_information=conn.query(query_for_teammate_graph,db="yazlab")
         query_information_teammate_result=[record for record in query_for_teammate_graph_information]
         query_for_teammate_node_id=(("MATCH(m:Researcher) WHERE m.Researcher_ID='"+str(i)+"' RETURN ID(m) "))
         query_for_teammate_node_id_information=conn.query(query_for_teammate_node_id,db="yazlab")
         r_teammate_node_id.append(query_for_teammate_node_id_information[0][0])
         r_teammate_name.append(query_information_teammate_result[0]['m'].get('name'))
         r_teammate_surname.append(query_information_teammate_result[0]['m'].get('surname'))
         r_teammate_publication_name.append(query_information_teammate_result[0]['m'].get('publication_name'))
      

     teammate_p_node_id_general=[]
     for i in r_teammate_id:
         query_for_teammate_for_p_node_id=("MATCH(m:Researcher)-[r:PUBLICATION_WRITER]->(n:Publications) WHERE m.Researcher_ID='"+str(i)+"' RETURN (n)")
         query_for_teammate_p_node_id_information=conn.query(query_for_teammate_for_p_node_id,db="yazlab")
         query_information_teammate_p_node_id_result=[record for record in query_for_teammate_p_node_id_information]
         list_for_teammate_p_id=[]
         for k in range(len(query_information_teammate_p_node_id_result)):
             list_for_teammate_p_id.append(query_information_teammate_p_node_id_result[k]['n'].get('publication_id'))
         list_for_teammate_p_node_id=[]
         for i  in range(len(p_publication_id)):
            for j in range(len(list_for_teammate_p_id)):
                if p_publication_id[i]==list_for_teammate_p_id[j]:
                    list_for_teammate_p_node_id.append(p_node_id[i])
         teammate_p_node_id_general.append(list_for_teammate_p_node_id)
         




     return(r_name,r_publication_name,r_surname,p_publication_id,p_publication_name,p_publication_place,p_publication_type,p_publication_year,t_type_id,t_type_place,t_type_type,r_teammate_id,r_teammate_name,r_teammate_publication_name,r_teammate_surname,r_node_id,p_node_id,type_node_id,r_teammate_node_id,teammate_p_node_id_general)
     



#Label göstermek icin ama gerek yok simdilik


