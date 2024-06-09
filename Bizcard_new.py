import streamlit as st
from streamlit_option_menu import option_menu
import easyocr
from PIL import Image
import pandas as pd
import numpy as np
import re
import mysql
import mysql.connector
import io
import time as t



def img_text(path):
  input_image = Image.open(path)
  #converting image into array format
  imag_array = np.array(input_image)
  reader = easyocr.Reader(['en'])
  text = reader.readtext(imag_array,detail=0)
  return text,input_image

# Data Extraction from image

def extracted_text(text):
  extrd_dict ={"NAME":[], "DESIGNATION":[], "COMPANY_NAME":[], "CONTACT":[], "EMAIL":[], "WEBSITE":[],
                "ADDRESS":[], "PINCODE":[]}

  extrd_dict["NAME"].append(text[0])
  extrd_dict["DESIGNATION"].append(text[1])

  pattern =r'\+\d{3}-\d{3}-\d{4}'
  extrd_dict["CONTACT"] =[]
  for tex in text:
    matches = re.findall(pattern,tex)
    extrd_dict["CONTACT"].extend(matches)
  pattern_1 =r'^\w+'
  extrd_dict["COMPANY_NAME"] =[]
  for tex in text:
    matches= re.match(pattern_1,tex)
  result =text[0] + " "+ matches.group()
  extrd_dict["COMPANY_NAME"].append(result)
  pattern_2 = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,3}'
  extrd_dict["EMAIL"] = []
  for tex in text:
    matches= re.findall(pattern_2,tex)
    extrd_dict["EMAIL"].extend(matches)
  pattern_4 = r'((https?://)?(www\.)?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,3}))'
  extrd_dict["WEBSITE"] = []
  for tex in text:
    matches = re.findall(pattern_4,tex)
    for i in matches:
      url =  i[0]
      extrd_dict["WEBSITE"].append(url)
  extrd_dict["WEBSITE"].pop()
  pattern_5 = r'\d+.*(?:St|Rd|Chennai|TamilNadu|\d{5}|\d{6})'
  extrd_dict["ADDRESS"] = []
  for tex in text:
    matches = re.findall(pattern_5,tex)
    if matches:
      extrd_dict["ADDRESS"].append(matches)
  flattened_address = [item for sublist in extrd_dict["ADDRESS"] for item in sublist]
  extrd_dict["ADDRESS"] = flattened_address
  pattern_6 = r'TamilNadu\s*\d{6}'
  extrd_dict["PINCODE"]= []
  for tex in text:
    matches = re.findall(pattern_6,tex)
    if matches:
      extrd_dict["PINCODE"].append(matches)
  flattened_pincode = [item for sublist in extrd_dict["PINCODE"] for item in sublist]
  extrd_dict["PINCODE"] = flattened_pincode

  # to convert into dataframe

  for key,value in extrd_dict.items():
    if len(value)>0:
      concadenate= " ".join(value)
      extrd_dict[key] = [concadenate]

    else:
      value = "NA"
      extrd_dict[key] = [value]
  return extrd_dict


#Creating table

def create_table():

    connection = mysql.connector.connect(host="localhost",user="root",password="Bairavi@17",database="biz_card",auth_plugin = 'mysql_native_password')
    mycursor = connection.cursor()

    create_table_query = '''CREATE TABLE IF NOT EXISTS bizcard_details(name varchar(225),
                                                                            designation varchar(225),
                                                                            company_name varchar(225),
                                                                            contact varchar(225),
                                                                            email varchar(225),
                                                                            website text,
                                                                            address text,
                                                                            pincode varchar(225),
                                                                            image LONGBLOB)'''
    mycursor.execute(create_table_query)
    connection.commit()
    return create_table_query

#Data insertion into table

def insert_table():   
   
    connection = mysql.connector.connect(host="localhost",user="root",password="Bairavi@17",database="biz_card",auth_plugin = 'mysql_native_password')
    mycursor = connection.cursor()

    for index,row in con_df.iterrows():

        insert_query = '''INSERT INTO bizcard_details(name, designation, company_name,contact, email, website, address,
                                                        pincode,image)

                                                        values(%s,%s,%s,%s,%s,%s,%s,%s,%s)'''

                                        
        rows=(row['NAME'],row['DESIGNATION'],row['COMPANY_NAME'],row['CONTACT'],row['EMAIL'],row['WEBSITE'],row['ADDRESS'],
                row['PINCODE'],row['IMAGE'])
        mycursor.execute(insert_query,rows)
        connection.commit()

        query = "select * from bizcard_details"
        mycursor.execute(query)
        result = mycursor.fetchall()
        return result
    
def preview_table():
    
    connection = mysql.connector.connect(host="localhost",user="root",password="Bairavi@17",database="biz_card",auth_plugin = 'mysql_native_password')
    mycursor = connection.cursor()
    
    query = "select * from bizcard_details"
    mycursor.execute(query)
    result=mycursor.fetchall()
    result_1 = pd.DataFrame(result,columns=("NAME","DESIGNATION","COMPANY_NAME","CONTACT","EMAIL","WEBSITE",
                                            "ADDRESS","PINCODE","IMAGE"))
    return result_1

def name_table():
    query = "select * from bizcard_details where name = %s"
    mycursor.execute(query,(selected_name,))
    result=mycursor.fetchall()
    result_1 = pd.DataFrame(result,columns=("NAME","DESIGNATION","COMPANY_NAME","CONTACT","EMAIL","WEBSITE",
                                            "ADDRESS","PINCODE","IMAGE"))
    return result_1

# Streamlit part

st.set_page_config(layout="wide")

st.title(":violet[BizCardX] :rainbow[EXTRACTING BUSINESS CARD DATA WITH OCR]")


with st.sidebar:
   select = option_menu("Main Menu",["Home","Data Extraction","Modification","Deletion"])

if select == "Home":

  st.subheader(":red[**About the Application**]")

  st.write(" Users can save the information extracted from the card image using easy OCR. The information can be uploaded into a database (MySQL) after alterations that supports multiple entries. ")
  
  st.subheader(":green[**Easy OCR:**]")

  st.write("Easy OCR is user-friendly Optical Character Recognition (OCR) technology, converting documents like scanned paper, PDFs, or digital camera images into editable and searchable data. A variety of OCR solutions, including open-source libraries, commercial software, and cloud-based services, are available. These tools are versatile, used for extracting text from images, recognizing printed or handwritten text, and making scanned documents editable.")
  
  st.subheader(":violet[**Technologies Used :**]")

  st.write("Python,Easy OCR, Streamlit, SQL, Pandas")  

  st.subheader(":blue[**Project Objective:**]")

  st.write('The objective of Bizcard is to automate the process of extracting key details from business card images, such as the name, designation, company, contact information, and other relevant data. By leveraging the power of OCR (Optical Character Recognition) provided by EasyOCR, Bizcard is able to extract text from the images.')


elif select == "Data Extraction":
   
   img = st.file_uploader("Upload the Image",type = ["png","jpg","jpeg"])

   if img != None:
     
     st.image(img,width=350)
  

   button = st.button("Submit",use_container_width=True)

   if button:

        with st.spinner("Extracting Data:satellite_antenna:"):
          t.sleep(25)

   if img != None:
      
        #st.image(img,width=350)
        
        text_img,input_image = img_text(img)

        text_dict = extracted_text(text_img)

        if text_dict:
          
          st.success("TEXT IS EXTRACTED SUCCESSFULLY")
        
        df = pd.DataFrame(text_dict)

    # Converting image into Binary format

        Image_bytes = io.BytesIO()
        input_image.save(Image_bytes,format = "PNG")
        image_data = Image_bytes.getvalue()

        data = {"IMAGE":[image_data]}
        df_1 = pd.DataFrame(data)

        # Merging two dataframes

        con_df = pd.concat([df,df_1],axis = 1)

        st.dataframe(con_df) 

        sql_button = st.button("Save",use_container_width=True)

        if sql_button:

          with st.spinner("Uploading Data...:running:"):
            t.sleep(25)

            create_table()

            insert_table()          

            st.success("Uploaded Sucessfully")


elif select == "Modification":

  radio_buttons = ['NONE','PREVIEW','MODIFY']
  buttons = st.radio("Select the Options to View",radio_buttons)
  st.write("**You Selected:**",buttons,":point_left:")

  if buttons == "PREVIEW":     
     st.header(":green[**TABLE DATA DISPLAY**]:clipboard:")
     st.dataframe(preview_table())

  if buttons == "MODIFY":
     
    show_table = preview_table()
    show_table

    connection = mysql.connector.connect(host="localhost",user="root",password="Bairavi@17",database="biz_card",auth_plugin = 'mysql_native_password')
    mycursor = connection.cursor()

    name_list = []    
    query = "select * from bizcard_details"
    mycursor.execute(query)
    result=mycursor.fetchall()
    for i in result:
        name_list.append(i[0])
    
    selected_name = st.selectbox("Select the name",name_list)

    result_1 = name_table()
    result_1 

    col1,col2 = st.columns(2)

    with col1:
       
       mod_name = st.text_input("Name",result_1["NAME"].unique()[0])
       mod_designation = st.text_input("DESIGNATION",result_1["DESIGNATION"].unique()[0])
       mod_comp_name = st.text_input("COMPANY_NAME",result_1["COMPANY_NAME"].unique()[0])
       mod_contact = st.text_input("CONTACT",result_1["CONTACT"].unique()[0])
       mod_email = st.text_input("EMAIL",result_1["EMAIL"].unique()[0])

    with col2:
       
       mod_website = st.text_input("WEBSITE",result_1["WEBSITE"].unique()[0])
       mod_address = st.text_input("ADDRESS",result_1['ADDRESS'].unique()[0])
       mod_pincode = st.text_input("PINCODE",result_1['PINCODE'].unique()[0])
       mod_image = st.text_input("IMAGE",result_1["IMAGE"].unique()[0])

       

    with col1:
       
       button_1 = st.button(":violet[Modify] :maple_leaf:",use_container_width=True)

    if button_1:
       
       query = '''Update bizcard_details set name = %s, designation = %s, company_name = %s,contact = %s, email = %s, website = %s,
                  address = %s,pincode = %s,image = %s WHERE name = %s'''
       parameters = (mod_name, mod_designation, mod_comp_name, mod_contact, mod_email, mod_website, mod_address, mod_pincode, mod_image, selected_name)
       result_2 = mycursor.execute(query,parameters)
       connection.commit()                                                       
       
       st.success("Updated Sucessfully")

       button_2 = st.button("Updated View",use_container_width=True)

       if button_2:
        st.write("**TABLE DATA DISPLAY**")
        st.dataframe(preview_table())     

elif select == "Deletion":
   
  connection = mysql.connector.connect(host="localhost",user="root",password="Bairavi@17",database="biz_card",auth_plugin = 'mysql_native_password')
  mycursor = connection.cursor()

  col1,col2 = st.columns(2)

  col1,col2 = st.columns(2)
  with col1:

    select_query = "SELECT NAME FROM bizcard_details"

    mycursor.execute(select_query)
    table1 = mycursor.fetchall()
    connection.commit()

    names = []

    for i in table1:
      names.append(i[0])

    name_select = st.selectbox("Select the name", names)

  with col2:

    select_query = f"SELECT DESIGNATION FROM bizcard_details WHERE NAME ='{name_select}'"

    mycursor.execute(select_query)
    table2 = mycursor.fetchall()
    connection.commit()

    designations = []

    for j in table2:
      designations.append(j[0])

    designation_select = st.selectbox("Select the designation", options = designations)

  if name_select and designation_select:
    col1,col2,col3 = st.columns(3)

    with col1:
      st.write(f"Selected Name : {name_select}")
      st.write("")
      st.write("")
      st.write("")
      st.write(f"Selected Designation : {designation_select}")

    with col2:
      st.write("")
      st.write("")
      st.write("")
      st.write("")

      remove = st.button("Delete", use_container_width= True)

      if remove:

        mycursor.execute(f"DELETE FROM bizcard_details WHERE NAME ='{name_select}' AND DESIGNATION = '{designation_select}'")
        connection.commit()

        st.warning("DELETED")

    button_5 =  st.button("Updated Table",use_container_width=True)

    if button_5:     
        st.write("**TABLE DATA DISPLAY**")
        st.dataframe(preview_table())