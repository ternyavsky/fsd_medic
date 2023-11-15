import MySQLdb


db = MySQLdb.connect(
     host="188.225.85.228",
     user="gen_user",
     passwd="#i*InO79XJn\ZP",
     db="default_db",
     port=3306 
)

cursor = db.cursor()

#  prod_sql = "DELETE FROM api_user WHERE verification_code = 1"
#  cursor.execute(prod_sql)

dev_sql = "delete from api_user where id=117"
cursor.execute(dev_sql)

db.commit()

print(cursor.rowcount, "record(s) deleted")
