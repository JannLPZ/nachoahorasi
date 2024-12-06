
from .entities.Usuario import Usuario
from .entities.TipoUsuario import TipoUsuario

class ModeloUsuario():
    @classmethod
    def login(self,db,usuario):
        try:
            cursor=db.connection.cursor()
            sql="""SELECT id, usuario, password FROM usuario 
            WHERE usuario = '{0}'""".format(usuario.usuario)
            cursor.execute(sql)
            data=cursor.fetchone()
            if data != None:
                coincide=Usuario.verificar_password(data[2], usuario.password)
                if coincide:
                    usuario_logeado=Usuario(data[0], data[1], None, None)
                    return usuario_logeado
                else:
                    return None
            else:
                return None
        except Exception as ex:
            raise Exception(ex)
        
    @classmethod    
    def obtener_por_id(self,db,id):
        try:
            cursor = db.connection.cursor()
            sql = """SELECT USU.id, USU.usuario, TIP.id, TIP.nombre
            FROM usuario USU JOIN tipousuario TIP ON USU.tipousuario_id = TIP.id 
            WHERE USU.id = {0}""".format(id)
            cursor.execute(sql)
            data = cursor.fetchone()
            if data is not None:
                tipousuario = TipoUsuario(data[2], data[3])
                usuario_logeado = Usuario(data[0], data[1], None, tipousuario)
                return usuario_logeado
            else:
                return None  # No se encontró ningún usuario con el ID proporcionado
        except Exception as ex:
            raise Exception(ex)
        
    @classmethod
    def insertar_usuario(self, db, nombre_usuario, contrasena,domicilio,correo,telefono):
        try:
            cursor = db.connection.cursor()
            
            sql = """ INSERT INTO usuario (id, usuario, password, nombre, 
                        domicilio, correo, telefono, tipousuario_id) 
                        VALUES (NULL, '{0}', '{1}', '{2}', '{3}', '{4}', {5}, 2);""".format(
                        nombre_usuario, contrasena, nombre_usuario, domicilio, 
                        correo, telefono)
            

            cursor.execute(sql)
            db.connection.commit()
        except Exception as ex:
            raise Exception(ex)