from flask import Flask, jsonify, render_template, url_for
import mysql.connector
from flask import request, redirect, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS


app = Flask(__name__, template_folder='Menus', static_folder='static')

app.secret_key = 'clave_secreta_segura'  # Usa una más segura en producción

# ------------------ FUNCIONES DE CONEXIÓN ------------------

CORS(app)

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

def obtener_conexion():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='f7t4m7DAR_',
        database='PagWeb'
    )
    
    

# ------------------ RUTAS ------------------

@app.route('/maestro/<nombre>')
def ver_resenas_maestro(nombre):
    resenas = obtener_resenas_maestro(nombre)
    return render_template('resenasMaestro.html', nombre=nombre, resenas=resenas)

@app.route("/")
def inicio():
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("""
        SELECT r.comentario, r.calificacion, r.fecha,
            u.NomUsuario,
            m.nombreMateria,
            ma.nombreMaestro
        FROM reseñas r
        JOIN usuarios u ON r.idUsuario = u.idUsuario
        JOIN maestro_materia mm ON r.idMaestro_Materia = mm.idMaestro_Materia
        JOIN materias m ON mm.idMateria = m.idMateria
        JOIN maestros ma ON mm.idMaestro = ma.idMaestro
        ORDER BY r.fecha DESC
    """)
    
    resenas = cursor.fetchall()
    cursor.close()
    conexion.close()

    if 'rol' in session:
        if session['rol'] == 'Administrador':
            return render_template("inicio.html", resenas=resenas)  # Aquí sin "Menus/"
        elif session['rol'] == 'Estudiante':
            return render_template("inicio.html", resenas=resenas)

    return render_template("inicio.html", resenas=resenas)





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
        session['idUsuario'] = usuario['idUsuario']  # ✅ Aquí lo agregas
        session['rol'] = usuario['NomRol']
        if usuario['NomRol'] == 'Administrador':
            return redirect('/')
        else:
            return redirect('/')
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


@app.route('/peticion')
def mostrar_peticion():
    return render_template('peticion.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('inicio'))

@app.route('/agregarAdmi')
def agregar_admi():
    return render_template('agregarAdmi.html')

# ------------------ RUTA INICIAL pag reseñas ------------------
@app.route('/agregar-resena')
def agregar_resena():
    materias = obtener_materias()
    return render_template('agregarRes.html', materias=materias)



# ------------------ RUTA PARA OBTENER MAESTROS pag reseñas ------------------
@app.route('/obtener-maestros/<int:id_materia>')
def obtener_maestros_por_materia(id_materia):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    
    query = """
    SELECT m.idMaestro, m.nombreMaestro
    FROM maestro_materia mm
    JOIN maestros m ON mm.idMaestro = m.idMaestro
    WHERE mm.idMateria = %s
    """
    cursor.execute(query, (id_materia,))
    maestros = cursor.fetchall()
    conexion.close()
    
    return {'maestros': maestros}

# ------------------ RUTA PARA AGREGAR RESEÑA pag reseñas ------------------
@app.route('/guardar-resena', methods=['POST'])
def guardar_resena():
    if 'usuario' not in session:
        flash("Debes iniciar sesión para agregar una reseña.")
        return redirect('/login')

    comentario = request.form['comentario']
    calificacion = int(request.form['calificacion'])
    id_maestro = int(request.form['maestro'])
    id_materia = int(request.form['materia'])
    id_usuario = session['usuario']

    # Obtener idMaestro_Materia
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT idMaestro_Materia FROM maestro_materia
        WHERE idMaestro = %s AND idMateria = %s
    """, (id_maestro, id_materia))
    resultado = cursor.fetchone()

    if not resultado:
        flash("No se encontró relación maestro-materia.")
        conexion.close()
        return redirect('/agregar-resena')

    id_maestro_materia = resultado[0]

    cursor.execute("""
        INSERT INTO reseñas (comentario, calificacion, idUsuario, idMaestro_Materia)
        VALUES (%s, %s, %s, %s)
    """, (comentario, calificacion, session['idUsuario'], id_maestro_materia))
    conexion.commit()
    conexion.close()

    flash("¡Reseña guardada con éxito!")
    return redirect('/')

# ------------------ CRUD DE MATERIAS ------------------

@app.route('/admin/materias')
def crud_materias():
    if 'rol' not in session or session['rol'] != 'Administrador':
        flash("Acceso denegado.")
        return redirect('/')

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT idMateria, nombreMateria FROM materias ORDER BY nombreMateria ASC")
    materias = cursor.fetchall()
    conexion.close()
    return render_template('crudMaterias.html', materias=materias)

@app.route('/admin/materias/agregar', methods=['POST'])
def agregar_materia():
    if 'rol' not in session or session['rol'] != 'Administrador':
        flash("Acceso denegado.")
        return redirect('/')

    nombre = request.form['nombreMateria']
    if not nombre.strip():
        flash("El nombre de la materia no puede estar vacío.")
        return redirect('/admin/materias')

    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("INSERT INTO materias (nombreMateria) VALUES (%s)", (nombre,))
    conexion.commit()
    conexion.close()
    flash("Materia agregada correctamente.")
    return redirect('/admin/materias')

@app.route('/admin/materias/eliminar/<int:idMateria>', methods=['POST'])
def eliminar_materia(idMateria):
    if 'rol' not in session or session['rol'] != 'Administrador':
        flash("Acceso denegado.")
        return redirect('/')

    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM materias WHERE idMateria = %s", (idMateria,))
    conexion.commit()
    conexion.close()
    flash("Materia eliminada correctamente.")
    return redirect('/admin/materias')

@app.route('/admin/materias/editar/<int:idMateria>', methods=['POST'])
def editar_materia(idMateria):
    if 'rol' not in session or session['rol'] != 'Administrador':
        flash("Acceso denegado.")
        return redirect('/')

    nuevo_nombre = request.form['nuevoNombre']
    if not nuevo_nombre.strip():
        flash("El nuevo nombre no puede estar vacío.")
        return redirect('/admin/materias')

    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("UPDATE materias SET nombreMateria = %s WHERE idMateria = %s", (nuevo_nombre, idMateria))
    conexion.commit()
    conexion.close()
    flash("Nombre de la materia actualizado.")
    return redirect('/admin/materias')

@app.route('/like/<int:id>', methods=['POST'])
def like(id):
    if 'idUsuario' not in session:
        return jsonify({'error': 'no autorizado'}), 403

    user_id = session['idUsuario']

    # Verifica si ya reaccionó
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT * FROM reacciones WHERE idUsuario=%s AND idReseña=%s",
        (user_id, id)
    )
    reaccion = cursor.fetchone()

    if reaccion:
        conexion.close()
        return jsonify({'message': 'ya reaccionaste'}), 400

    # Insertar like
    cursor.execute(
        "INSERT INTO reacciones (idUsuario, idReseña, idTipo) VALUES (%s, %s, 1)",
        (user_id, id)
    )
    conexion.commit()
    conexion.close()
    return jsonify({'message': 'like registrado'})

conexion = mysql.connector.connect(
    host='localhost',
    user='root',
    password='f7t4m7DAR_',
    database='PagWeb'
)
cursor = conexion.cursor()

@app.route('/agregar_admin', methods=['GET', 'POST'])
def agregar_admin():
    if request.method == 'POST':
        usuario = request.form['usuario']
        password = request.form['password']
        confirm = request.form['confirm_password']

        if password != confirm:
            flash('Las contraseñas no coinciden.')
            return redirect('/agregar_admin')

        hashed_password = generate_password_hash(password)

        try:
            cursor.execute("INSERT INTO usuarios (NomUsuario, contraseña, idRol) VALUES (%s, %s, %s)",
            (usuario, hashed_password, 2))  # idRol 2 = administrador
            conexion.commit()
            flash('Administrador agregado exitosamente.')
        except Exception as e:
            flash(f'Error: {e}')
        return redirect('/agregar_admin')

    return render_template('agregarAdmi.html')


usuario = 'Angel'
contraseña = 'rivera06'
hash = generate_password_hash(contraseña)

print(f"INSERT INTO usuarios (NomUsuario, contraseña, idRol) VALUES ('{usuario}', '{hash}', 2);")

@app.route('/ver_peticiones')
def ver_peticiones():
    cursor = db.cursor(dictionary=True)
    query = """
        SELECT p.idPeticion, p.peticion, u.NomUsuario, t.Nom_Peticion 
        FROM peticiones p
        JOIN usuarios u ON p.idUsuario = u.idUsuario
        JOIN Tipo_Peticion t ON p.idRol_Peticion = t.idRol_Peticion;
    """
    cursor.execute(query)
    peticiones = cursor.fetchall()
    return render_template('ver_peticiones.html', peticiones=peticiones)

@app.route('/aceptar_peticion/<int:id>', methods=['POST'])
def aceptar_peticion(id):
    cursor = db.cursor(dictionary=True)

    # Obtener contenido de la petición
    cursor.execute("""
        SELECT peticion, idRol_Peticion FROM peticiones WHERE idPeticion = %s
    """, (id,))
    peticion = cursor.fetchone()

    if peticion:
        texto = peticion['peticion']
        tipo = peticion['idRol_Peticion']

        if tipo == 1:  # Materia
            cursor.execute("INSERT INTO materias (nombreMateria) VALUES (%s)", (texto,))
        elif tipo == 2:  # Maestro
            cursor.execute("INSERT INTO maestros (nombreMaestro) VALUES (%s)", (texto,))

        cursor.execute("DELETE FROM peticiones WHERE idPeticion = %s", (id,))
        db.commit()

    return redirect(url_for('ver_peticiones'))


@app.route('/denegar_peticion/<int:id>', methods=['POST'])
def denegar_peticion(id):
    cursor = db.cursor()
    cursor.execute("DELETE FROM peticiones WHERE idPeticion = %s", (id,))
    db.commit()
    return redirect(url_for('ver_peticiones'))

@app.route('/reportar/<int:id_resena>', methods=['POST'])
def reportar_resena(id_resena):
    try:
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="TU_PASSWORD",
            database="PagWeb"
        )
        cursor = conexion.cursor()
        cursor.execute("UPDATE resenas SET reportada = 1 WHERE idResena = %s", (id_resena,))
        conexion.commit()
        conexion.close()
        return '', 204  # No Content
    except Exception as e:
        print("Error al reportar reseña:", e)
        return 'Error interno del servidor', 500

# ------------------ INICIO DEL SERVIDOR ------------------

if __name__ == '__main__':
    app.run(debug=True, port=5001)
