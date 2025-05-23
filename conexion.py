from flask import Flask, render_template, url_for
import mysql.connector
from flask import request, redirect, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, template_folder='Menus', static_folder='static')

app.secret_key = 'clave_secreta_segura'  # Usa una más segura en producción

# ------------------ FUNCIONES DE CONEXIÓN ------------------


def obtener_maestros():
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="f7t4m7DAR_",
        database="PagWeb"
    )
    cursor = conexion.cursor()
    cursor.execute("SELECT nombreMaestro FROM maestros ORDER BY nombreMaestro ASC")
    maestros = cursor.fetchall()
    conexion.close()
    return [fila[0] for fila in maestros]

def obtener_resenas_maestro(nombre_maestro):
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="f7t4m7DAR_",
        database="PagWeb"
    )
    cursor = conexion.cursor()
    
    consulta = """
    SELECT r.comentario, r.calificacion, u.NomUsuario, m.nombreMateria
    FROM reseñas r
    JOIN usuarios u ON r.idUsuario = u.idUsuario
    JOIN maestro_materia mm ON r.idMaestro_Materia = mm.idMaestro_Materia
    JOIN maestros ma ON mm.idMaestro = ma.idMaestro
    JOIN materias m ON mm.idMateria = m.idMateria
    WHERE ma.nombreMaestro = %s
    """
    cursor.execute(consulta, (nombre_maestro,))
    resultados = cursor.fetchall()
    conexion.close()
    
    return resultados

def obtener_nombre_materia(idMateria):
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="f7t4m7DAR_",
        database="PagWeb"
    )
    cursor = conexion.cursor()
    cursor.execute("SELECT nombreMateria FROM materias WHERE idMateria = %s", (idMateria,))
    resultado = cursor.fetchone()
    conexion.close()
    return resultado[0] if resultado else "Materia desconocida"

def obtener_materias():
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="f7t4m7DAR_",
        database="PagWeb"
    )
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT idMateria, nombreMateria FROM materias ORDER BY nombreMateria ASC")
    materias = cursor.fetchall()
    conexion.close()
    return materias

# ------------------ RUTAS ------------------

@app.route('/maestro/<nombre>')
def ver_resenas_maestro(nombre):
    resenas = obtener_resenas_maestro(nombre)
    return render_template('resenasMaestro.html', nombre=nombre, resenas=resenas)

@app.route('/')
def inicio():
    return render_template('inicio.html')

@app.route('/agregar-resena')  # Define la URL de acceso (ej: /agregar-resena)
def agregar_resena():
    return render_template('agregarReseña.html')  # Renderiza el HTML

@app.route('/materias')
def mostrar_materias():
    materias = obtener_materias()
    return render_template('menuMateria.html', materias=materias)

@app.route('/maestros')
def mostrar_maestros():
    maestros = obtener_maestros()
    return render_template('menuMaestro.html', maestros=maestros)

@app.route('/login')
def inicio_sesion():
    return render_template('inicioSesion.html')

@app.route('/materia/<int:idMateria>')
def reseñas_por_materia(idMateria):
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="f7t4m7DAR_",
        database="PagWeb"
    )
    cursor = conexion.cursor(dictionary=True)
    
    query = """
    SELECT r.comentario, r.calificacion, u.NomUsuario, m.nombreMaestro
    FROM reseñas r
    JOIN maestro_materia mm ON r.idMaestro_Materia = mm.idMaestro_Materia
    JOIN maestros m ON mm.idMaestro = m.idMaestro
    JOIN usuarios u ON r.idUsuario = u.idUsuario
    WHERE mm.idMateria = %s
    """
    cursor.execute(query, (idMateria,))
    reseñas = cursor.fetchall()
    conexion.close()
    
    # También puedes traer el nombre de la materia para mostrar en la plantilla
    nombre_materia = obtener_nombre_materia(idMateria)

    return render_template('resenasMaterias.html', reseñas=reseñas, nombre_materia=nombre_materia)

@app.route('/test-template')
def test_template():
    try:
        return render_template('resenasMaterias.html', reseñas=[], nombre_materia="Prueba")
    except Exception as e:
        return f"Error cargando template: {str(e)}"

@app.route('/login', methods=['POST'])
def login_post():
    username = request.form['username']
    password = request.form['password']

    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="f7t4m7DAR_",
        database="PagWeb"
    )
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("""
        SELECT u.idUsuario, u.NomUsuario, u.contraseña, r.NomRol 
        FROM usuarios u 
        JOIN Roles r ON u.idRol = r.idRol 
        WHERE u.NomUsuario = %s
    """, (username,))
    usuario = cursor.fetchone()
    conexion.close()

    if usuario and check_password_hash(usuario['contraseña'], password):
        session['usuario'] = usuario['NomUsuario']
        session['rol'] = usuario['NomRol']
        if usuario['NomRol'] == 'Administrador':
            return redirect('/admin')
        else:
            return redirect('/estudiante')
    else:
        flash("Usuario o contraseña incorrectos")
        return redirect('/login')

@app.route('/register', methods=['POST'])
def register_post():
    username = request.form['username']
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    if password != confirm_password:
        flash("Las contraseñas no coinciden.")
        return redirect('/login')

    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="f7t4m7DAR_",
        database="PagWeb"
    )
    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM usuarios WHERE NomUsuario = %s", (username,))
    if cursor.fetchone():
        flash("El nombre de usuario ya existe.")
        conexion.close()
        return redirect('/login')

    # Obtener id del rol 'Estudiante'
    cursor.execute("SELECT idRol FROM Roles WHERE NomRol = 'Estudiante'")
    id_rol = cursor.fetchone()
    if not id_rol:
        flash("No existe el rol Estudiante en la base de datos.")
        conexion.close()
        return redirect('/login')

    hashed_password = generate_password_hash(password)
    cursor.execute(
        "INSERT INTO usuarios (NomUsuario, contraseña, idRol) VALUES (%s, %s, %s)",
        (username, hashed_password, id_rol[0])
    )
    conexion.commit()
    conexion.close()
    flash("Registro exitoso, ahora puedes iniciar sesión.")
    return redirect('/login')

@app.route('/admin')
def admin_dashboard():
    return render_template('pagAdmi.html')

@app.route('/estudiante')
def estudiante_dashboard():
    return render_template('pagEstudiante.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('inicio'))


# ------------------ INICIO DEL SERVIDOR ------------------


if __name__ == '__main__':
    app.run(debug=True, port=5001)


