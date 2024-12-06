from flask import Flask, render_template, request, url_for, redirect, flash, jsonify
from flask_mysqldb import MySQL
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_mail import Mail
from werkzeug.utils import secure_filename
import mysql.connector
import os

from .models.ModeloCompra import ModeloCompra
from .models.ModeloLibro import ModeloLibro
from .models.ModeloUsuario import ModeloUsuario

from .models.entities.compra import Compra
from .models.entities.Libro import Libro
from .models.entities.Usuario import Usuario

from .consts import *
from .emails import confirmacion_compra, enviar_correo_registro_administrador

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

csrf=CSRFProtect()
db=MySQL(app)
login_manager_app=LoginManager(app)
mail=Mail()
    

@login_manager_app.user_loader
def load_user(id):
    return ModeloUsuario.obtener_por_id(db,id)



@app.route('/password/<password>')



@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
         usuario=Usuario(None, request.form['usuario'], request.form['password'], None)
         usuario_logeado=ModeloUsuario.login(db,usuario)
         if usuario_logeado != None:
             login_user(usuario_logeado)
             flash(MENSAJE_BIENVENIDA, 'success')
             return redirect(url_for('index'))
         else:
            flash(LOGIN_CREDENCIALESINVALIDAS, 'warning')
            return render_template('auth/login.html')
    else:
        return render_template('auth/login.html')
    
@app.route('/logout')
def logout():
    logout_user()
    flash(LOGOUT, 'success')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    if current_user.is_authenticated:
        if current_user.tipousuario.id == 1:
            try:
                libros_vendidos = ModeloLibro.listar_libros_vendidos(db)
                data = {
                    'titulo': 'Libros Vendidos',
                    'libros_vendidos': libros_vendidos
                }
                return render_template('index.html', data=data)
            except Exception as ex:
                return render_template('errores/error.html', mensaje=format(ex))
            try:
                conn = get_db_connection(db)
                cursor = conn.cursor(dictionary=True)
                cursor.callproc('obtener_libros')
                libros = cursor.fetchall()
                cursor.close()
                conn.close()
                data['libros'] = libros
                return render_template('index.html', data=data)
            except Exception as ex:
                return render_template('errores/error.html', mensaje=format(ex))

        else:
            # Mostrar compras del usuario (lógica original)
            try:
                compras = ModeloCompra.listar_compras_usuario(db, current_user)
                data = {
                    'titulo': 'Mis compras',
                    'compras': compras
                }
                return render_template('index.html', data=data)
            except Exception as ex:
                return render_template('errores/error.html', mensaje=format(ex))

    else:
        return redirect(url_for('login'))

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_book():
    if request.method == 'POST':
        if current_user.tipousuario.id == 1:
            print('Llevó a la función')
            titulo = request.form.get['titulo']
            autor = request.form.get['autor_id']
            descripcion = request.form.get['descripcion']
            precio = request.form.get['precio']
            anoedicion = request.form.get['anoedicion']
            imagen = request.files.get['imagen']

            # Validación de datos (puedes agregar más validaciones según tus necesidades)
            if not titulo or not autor or not descripcion or not precio:
                flash('Por favor, completa todos los campos.', 'danger')
                return render_template('addbook.html')
            if not imagen or not allowed_file(imagen.filename):
                flash('Por favor, selecciona una imagen válida.', 'danger')
                return render_template('addbook.html')
            try:
                precio = float(precio)  # Convertir precio a float para validaciones numéricas
                if precio <= 0:
                    raise ValueError("El precio debe ser mayor a cero.")
            except ValueError:
                flash('El precio debe ser un número positivo.', 'danger')
                return render_template('addbook.html')

            # Guardar la información en la base de datos
            filename = secure_filename(imagen.filename)
            imagen_path = os.path.join(app.config['UPLOADS_FOLDER'], filename)
            imagen.save(imagen_path)

            conn = get_db_connection()
            cursor = conn.cursor()

            # Ajusta la consulta SQL según tu estructura de base de datos
            cursor.execute("INSERT INTO libros (titulo, autor, descripcion, precio, imagen_portada) VALUES (%s, %s, %s, %s, %s)",
                           (titulo, autor, descripcion, precio, filename))

            conn.commit()
            cursor.close()
            conn.close()

            flash('Libro añadido exitosamente!', 'success')
            return redirect(url_for('index'))
        else:
            flash('No tienes permiso para agregar libros.', 'danger')
            return redirect(url_for('index'))
    return render_template('addbook.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def update_book(id):
    # Obtener el libro a editar desde la base de datos
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM libros WHERE id = %s', (id,))
    libro = cursor.fetchone()
    cursor.close()
    conn.close()

    if request.method == 'POST':
        if current_user.tipousuario.id == 1:
            # Obtener los datos del formulario
            titulo = request.form['titulo']
            autor = request.form['autor']
            descripcion = request.form['descripcion']
            precio = request.form['precio']
            imagen = request.files['imagen']

            # Validación de datos (puedes agregar más validaciones según tus necesidades)
            # ... (similar a la función add_book)

            # Actualizar la información en la base de datos
            conn = get_db_connection()
            cursor = conn.cursor()

            # Si se ha subido una nueva imagen, actualizar el nombre de la imagen en la base de datos
            if imagen and allowed_file(imagen.filename):
                filename = secure_filename(imagen.filename)
                imagen_path = os.path.join(app.config['UPLOADS_FOLDER'], filename)
                imagen.save(imagen_path)

                cursor.execute('UPDATE libros SET titulo = %s, autor = %s, descripcion = %s, precio = %s, imagen_portada = %s WHERE id = %s',
                               (titulo, autor, descripcion, precio, filename, id))
            else:
                # Si no se ha subido una nueva imagen, actualizar solo los demás campos
                cursor.execute('UPDATE libros SET titulo = %s, autor = %s, descripcion = %s, precio = %s WHERE id = %s',
                               (titulo, autor, descripcion, precio, id))

            conn.commit()
            cursor.close()
            conn.close()

            flash('Libro actualizado exitosamente!', 'success')
            return redirect(url_for('index'))
        else:
            flash('No tienes permiso para editar libros.', 'danger')
            return redirect(url_for('index'))

    return render_template('update_book.html', libro=libro)

@app.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_book(id):
    if current_user.tipousuario.id == 1:
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM libros WHERE id = %s', (id,))
            conn.commit()
            flash('Libro eliminado exitosamente!', 'success')
        except Exception as e:
            flash('Error al eliminar el libro: ' + str(e), 'danger')
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('index'))
    else:
        flash('No tienes permiso para eliminar libros.', 'danger')
        return redirect(url_for('index'))

@app.route('/libros')
@login_required
def listar_libros():
    try:
        libros = ModeloLibro.listar_libros(db)
        data={
            'titulo':'listado de libros',
            "libros":libros
        }
        return render_template('listado_libros.html', data=data)
    except Exception as ex:
        return render_template('errores/error.html', mensaje=format(ex))

from flask import request, render_template

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOADS_FOLDER'], filename))
            flash('File uploaded successfully')
            return redirect(url_for('uploaded_file', filename=filename))
    return render_template('upload.html')


@app.route('/comprarLibro', methods=['POST'])
@login_required
def comprar_libro():
    data_request = request.get_json()
    data={}
    try:
        # libro = Libro(data_request['isbn'],None, None, None, None)
        libro = ModeloLibro.leer_libro(db, data_request['isbn'])
        compra= Compra(None, libro, current_user)
        data['exito']= ModeloCompra.registrar_compra(db, compra)
        # confirmacion_compra(mail, current_user, libro)
        confirmacion_compra(app, mail, current_user, libro)
    except Exception as ex:
        data['mensaje']=format(ex)
        data['exito']= False
    return jsonify(data)

@app.route('/registrar')
def registrar():
    return render_template('auth/formulario.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre_usuario = request.form['nombre_usuario']
        contrasena = request.form['contrasena']
        correo = request.form['correo']
        domicilio = request.form['direccion']
        telefono = request.form['telefono']
        contrasena_encriptada = Usuario.generar_encriptacion(contrasena)
        try:
            nuevo_usuario_id = ModeloUsuario.insertar_usuario(db, nombre_usuario, contrasena_encriptada,domicilio,correo,telefono)
            enviar_correo_registro_administrador(app,mail, nombre_usuario, correo)
            return redirect(url_for('login'))
        except Exception as ex:
            return render_template('errores/error.html', mensaje=format(ex))
    else:
        return render_template('auth/formulario.html')

def pagina_no_encontrada(error):
    return render_template('errores/404.html') 

def pagina_no_autorizada(error):
    return redirect(url_for('login'))

def inicializar_app(config):
    app.config.from_object(config)
    csrf.init_app(app)
    mail.init_app(app)
    app.register_error_handler(401, pagina_no_autorizada)
    app.register_error_handler(404, pagina_no_encontrada)
    return app
