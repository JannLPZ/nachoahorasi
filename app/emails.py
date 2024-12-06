from threading import Thread
from flask_mail import Message
from flask import current_app, render_template

def confirmacion_compra(app, mail,usuario,libro):
    try:
        message=Message('Confirmacion de compra de libro', 
                        sender=current_app.config['MAIL_USERNAME'],
                        recipients=['20213tn147@utez.edu.mx'])
        message.html=render_template('emails/confirmacion_compra.html', usuario=usuario, libro=libro)
        thread=Thread(target=envio_email_async,args=[app,mail,message])
        thread.start()
    except Exception as ex:
        raise Exception(ex)
    
def enviar_correo_registro_administrador(app, mail, usuario, correo):
    try:
        """admin_email = current_app.config['ADMIN_EMAIL']
        subject = "Nuevo usuario registrado: {}".format(usuario.usuario)"""
        message=Message('Confirmacion de registro de usuario', 
                        sender=current_app.config['MAIL_USERNAME'],
                        recipients=[correo])
        message.html = render_template('emails/nuevo_usuario.html', usuario=usuario)
        thread = Thread(target=envio_email_async, args=[app, mail, message])
        thread.start()
    except Exception as ex:
        app.logger.error("Error al enviar correo de registro de administrador: %s", ex)
    
def envio_email_async(app, mail, message):
    with app.app_context():
        mail.send(message)
