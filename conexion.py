import mysql.connector

conexion = mysql.connector.connect(
    host="localhost",
    user="root",         # o tu usuario de MySQL
    password="f7t4m7DAR_",  # tu contraseña
    database="PagWeb"    # asegúrate de que esta base exista
)

cursor = conexion.cursor()
cursor.execute("SELECT * FROM usuarios")

for fila in cursor.fetchall():
    print(fila)

conexion.close()
