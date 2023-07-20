import mysql.connector

def connect_mysql():
    mydb = mysql.connector.connect(
        host="localhost",
        user="",
        password="",
        database='academicworld'
    )
    return mydb