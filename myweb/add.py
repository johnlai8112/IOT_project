import pymysql
import time   

db = pymysql.connect("localhost","root","","mydb" )

                  # prepare a cursor object using cursor() method
cursor = db.cursor()

# Prepare SQL query to INSERT a record into the database.
# 數值在DB的欄位  對應的參數值 (要討論要有多少個參數)
heart_datetime=time.strftime('%Y-%m-%d %H:%M:%S')
#heart_beat=int(Json["Data"]["Heart_Beat"])


heart_sql = """INSERT INTO HEART_EVENT(hprikey,hdate,nodename,heartcount,event)
              VALUES (null,heart_datetime,'NODE_01',120,false)"""

try:
    # Execute the SQL command
    cursor.execute(heart_sql)
    # Commit your changes in the database
    db.commit()
except:
    # Rollback in case there is any error
	db.rollback()

    # disconnect from server
db.close()