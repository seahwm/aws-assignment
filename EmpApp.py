from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *
import datetime
import calendar

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
    return render_template('Homepage.html')

@app.route("/aboutus",methods=['GET','POST'])
def aboutUs():
    return render_template("AboutUs.html")

@app.route("/addempPage", methods=['GET', 'POST'])
def addempPage():
    return render_template('AddEmp.html')

@app.route("/getemp", methods=['GET', 'POST'])
def getEmp():
    return render_template("GetEmp.html")

@app.route("/applyLeave",methods=['GET','POST'])
def applyLeave():
    id=(request.form.get("id"))
    date=request.form.get("date")
    if(id==""):
        return render_template("err.html",msg="Please enter employee id")
    if(date==""):
        return render_template("err.html",msg="Please enter the date")
    
    dateList=date.split("-")
    year=int(dateList[0])
    month=int(dateList[1])
    day=int(dateList[2])
    id=int(id)

    
    retrieve_sql = "Select * from employee.leave Where emp_id=%s and day=%s and month=%s and year=%s"
    cursor = db_conn.cursor()
    cursor.execute(retrieve_sql,(id,day,month,year))
    row_count = cursor.rowcount
    if(row_count!=0):
        return render_template("err.html",msg="You already apply leave for that day!!")
    else:
        insert_sql="INSERT INTO employee.leave VALUES (%s, %s, %s, %s)"
        cursor.execute(insert_sql,(id,day,month,year))

    db_conn.commit()

    return render_template("success.html",msg="Employee id:"
    +str(id)+" have apply leave for "+str(day)+"/"+str(month)+"/"+str(year)+" successful!")

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

@app.route("/salary",methods=['GET', 'POST'])
def salary():
    return render_template("EmpCalculateSalary.html")

@app.route("/calculateSalary",methods=['GET','POST'])
def calculateSalary():
    id=request.form.get("id")
    monthlySalary=request.form.get("salary")
    month=request.form.get("month")
    year=request.form.get("year")
    name=""
    salary=0
    if(id==""):
        return render_template("err.html"
        ,msg="Please enter id")

    if(month==""):
        return render_template("err.html"
        ,msg="Please enter month")
    
    if(year==""):
        return render_template("err.html"
        ,msg="Please enter year")

    if(salary==""):
        return render_template("err.html"
        ,msg="Please enter salary")

    retrieve_sql = "Select * from employee Where emp_id="+id
    cursor = db_conn.cursor()
    cursor.execute(retrieve_sql)
    row_count = cursor.rowcount
    if(row_count==0):
        return render_template("err.html",msg="Employee Not Found!")
    else:
        for row in cursor:
            name=row[1]+" "+row[2]
    retrieve_sql = "Select * from employee.leave Where emp_id=%s and month=%s and year=%s order by day"
    cursor.execute(retrieve_sql,(id,month,year))
    num=cursor.rowcount
    dateList=cursor
    db_conn.commit()
    
    tmp=datetime.datetime(int(year),int(month),1)
    m=tmp.strftime("%b")
    date=m+"/"+year

    max=calendar.monthrange(int(year), int(month))[1]
    salary=int(monthlySalary)*(int(max)-num)/int(max)
    deduct=int(monthlySalary)*num/int(max)
    deduct=round(deduct,2)
    salary=round(salary,2)
    print(salary)
    return render_template("EmpCalculateSalaryOutput.html",id=id,
    salary=salary,name=name,list=dateList,num=num,
    deduct=deduct,date=date)

@app.route("/performance",methods=['GET', 'POST'])
def performance():
    return render_template('performance.html')

def sortEmp(elem):
    return elem[2]

@app.route("/checkPerformance",methods=['GET','POST'])
def checkPerformance():
    year=request.form.get("year")
    if(year==""):
        return render_template("err.html"
        ,msg="Please enter year")
    retrieve_sql = "Select * from employee"
    cursor = db_conn.cursor()
    cursor.execute(retrieve_sql)
    list=cursor
    empList=[]
    tmp=[]
    for row in list:
        emp=[]
        emp.append(row[0])
        name=row[1]+row[2]
        emp.append(name)
        tmp.append(emp)
    
    for emp in tmp:
        retrieve_sql = "Select * from employee.leave Where emp_id=%s and year=%s"
        cursor.execute(retrieve_sql,(emp[0],year))
        num=cursor.rowcount
        emp.append(num)
        empList.append(emp)
    db_conn.commit()
    empList.sort(key=sortEmp)
    return render_template('performanceOutput.html',year=year,empList=empList)

@app.route("/attendance",methods=['GET', 'POST'])
def attendance():
    return render_template("CheckLeave.html")

@app.route("/checkLeave",methods=['GET','POST'])
def cehckLeave():
    id=request.form.get("emp_id")
    year=request.form.get("year")
    month=request.form.get("month")
    num=0
    dateList=[]
    if(id==""):
        return render_template("err.html"
        ,msg="Please enter id")

    if(month==""):
        return render_template("err.html"
        ,msg="Please enter month")
    
    if(year==""):
        return render_template("err.html"
        ,msg="Please enter year")

    retrieve_sql = "Select * from employee Where emp_id="+id
    cursor = db_conn.cursor()
    cursor.execute(retrieve_sql)
    row_count = cursor.rowcount
    if(row_count==0):
        return render_template("err.html",msg="Employee Not Found!")
    else:
        retrieve_sql=retrieve_sql = "Select * from employee.leave Where emp_id=%s and month=%s and year=%s order by day"
        cursor.execute(retrieve_sql,(id,month,year))
        num=cursor.rowcount
        dateList=cursor
        print(dateList)
    db_conn.commit()
    tmp=datetime.datetime(int(year),int(month),1)
    m=tmp.strftime("%b")
    date=m+"/"+year
    return render_template("CheckLeaveOutput.html",id=id,
    year=year,date=date,num=num,list=dateList)

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
