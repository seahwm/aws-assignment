from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *


app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'employee'


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('AddEmp.html')

@app.route("/getemp", methods=['GET', 'POST'])
def getEmp():
    return render_template("GetEmp.html")

@app.route("/applyLeave",methods=['GET','POST'])
def applyLeave():
    id=request.form.get("id")
    date=request.form.get("date")
    print(type(date))
    
    return str(id)+str(date)

@app.route("/leave", methods=['GET', 'POST'])
def leave():
    return render_template("EmpApplyLeave.html")

@app.route("/updateEmpPage",methods=['GET', 'POST'])
def updateEmpPage():
    id=request.form.get("id")
    fname=request.form.get("fname")
    lname=request.form.get("lname")
    skill=request.form.get("skill")
    location=request.form.get("location")
    return render_template("updateEmp.html",id=id,fname=fname,
    lname=lname,skill=skill,location=location)

@app.route("/updateEmp",methods=['GET', 'POST'])
def updateEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    emp_image_file = request.files['emp_image_file']

    update_sql = "UPDATE employee set first_name=%s,last_name=%s,pri_skill=%s,location=%s where emp_id=%s"
    cursor = db_conn.cursor()

    if(emp_id==""):
        return render_template("err.html"
        ,msg="Please enter id")

    if(first_name==""):
        return render_template("err.html"
        ,msg="Please enter first name")

    if(last_name==""):
        return render_template("err.html"
        ,msg="Please enter last name")

    if(pri_skill==""):
        return render_template("err.html"
        ,msg="Please enter primary skill")

    if(location==""):
        return render_template("err.html"
        ,msg="Please enter location")

    if emp_image_file.filename == "":
        return render_template("err.html"
        ,msg="Please select a file")

    try:

        cursor.execute(update_sql, (first_name, last_name, pri_skill, location,emp_id))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

        except Exception as e:
            return render_template('err.html', msg=str(e))

    except Exception as e:
        cursor.close()
        msg=str(e)
        if(e.args[0]==1062):
            msg="Duplicated Employee Id detected!"
        return render_template('err.html', msg=msg)
    
    finally:
        cursor.close()

    print("all modification done...")
    return render_template('AddEmpOutput.html', name=emp_name)

@app.route("/deleteEmp",methods=['GET','POST'])
def delEmp():
    id=request.form.get("id")
    if(id=="" or id==None):
        return render_template("err.html",msg="Id not found!")
    del_sql = "DELETE FROM employee where emp_id=%s"
    cursor = db_conn.cursor()
    try:
        cursor.execute(del_sql,(id))
        db_conn.commit()
        emp_image_file_name_in_s3 = "emp-id-" + str(id) + "_image_file"
        
        s3 = boto3.resource('s3')
        s3.Object(custombucket, emp_image_file_name_in_s3).delete()
    except Exception as e:
        cursor.close()
        msg=str(e)
        if(e.args[0]==1062):
            msg="Duplicated Employee Id detected!"
        return render_template('err.html', msg=msg)
    finally:
        cursor.close()

    return render_template("success.html",msg="Employee with id: "+str(id)+" have successfully deleted")

@app.route("/fetchdata",methods=['GET','POST'])
def fetchdata():
    emp_id=request.form['emp_id']
    if(emp_id==""):
        return render_template("err.html",msg="Please enter employee id you want to search")
    
    first_name=""
    last_name=""
    pri_skill=""
    location=""

    retrieve_sql = "Select * from employee Where emp_id="+emp_id
    cursor = db_conn.cursor()
    cursor.execute(retrieve_sql)
    row_count = cursor.rowcount
    if(row_count==0):
        return render_template("err.html",msg="Employee Not Found!")
    for row in cursor:
        first_name=row[1]
        last_name=row[2]
        pri_skill=row[3]
        location=row[4]
    db_conn.commit()

    emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
    object_url = "https://{0}.s3.amazonaws.com/{1}".format(
       custombucket,
        emp_image_file_name_in_s3)
    return render_template("GetEmpOutput.html",id=emp_id,
    fname=first_name,lname=last_name,interest=pri_skill,location=location,image_url=object_url)

@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    emp_image_file = request.files['emp_image_file']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if(emp_id==""):
        return render_template("err.html"
        ,msg="Please enter id")

    if(first_name==""):
        return render_template("err.html"
        ,msg="Please enter first name")

    if(last_name==""):
        return render_template("err.html"
        ,msg="Please enter last name")

    if(pri_skill==""):
        return render_template("err.html"
        ,msg="Please enter primary skill")

    if(location==""):
        return render_template("err.html"
        ,msg="Please enter location")

    if emp_image_file.filename == "":
        return render_template("err.html"
        ,msg="Please select a file")

    try:

        cursor.execute(insert_sql, (emp_id, first_name, last_name, pri_skill, location))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

        except Exception as e:
            return render_template('err.html', msg=str(e))

    except Exception as e:
        msg=str(e)
        if(e.args[0]==1062):
            msg="Duplicated Employee Id detected!"
        return render_template('err.html', msg=msg)
    
    finally:
        cursor.close()

    print("all modification done...")
    return render_template('AddEmpOutput.html', name=emp_name)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
