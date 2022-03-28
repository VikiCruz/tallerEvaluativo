import email
from email.header import Header
import re
from flask.views import MethodView
from flask import jsonify, request, session
import hashlib
import pymysql
import bcrypt 
import jwt 
from config import KEY_TOKEN_AUTH
import datetime
from validators import CreateRegisterSchema
from validators import CreateLoginSchema
from validators import CreateCrearproductosSchema

def crear_conexion():
    try:
        #conexion a la db
        conexion = pymysql.connect(host='localhost',user='root',passwd='9424',db="taller2")
        return conexion
    except pymysql.Error as error:
        print('Se ha producido un error al crear la conexión:', error)


create_register_schema = CreateRegisterSchema()
create_login_schema = CreateLoginSchema()
create_crearproducto_schema = CreateCrearproductosSchema()

#http://127.0.0.1:5000/register
class RegisterControllers(MethodView):
    """
        register
    """
    def post(self):
        content = request.get_json()

        if not content:
            print("Headers", request.headers)
            return jsonify({"msg":"No hay contenido enviado desde JSON"}), 400

        email = content.get("email")
        nombres = content.get("nombres")
        apellidos = content.get("apellidos")
        password = content.get("password")
        print("--------", email, nombres, apellidos,password)

        salt = bcrypt.gensalt() ## son para hacer hash
        hash_password = bcrypt.hashpw(bytes(str(password), encoding= 'utf-8'), salt)## son para hacer hash
        errors = create_register_schema.validate(content)
        if errors:
            return errors, 400
        conexion=crear_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT password,email FROM usuarios WHERE email=%s", (email, ))
        auto=cursor.fetchone()
        if auto==None:
            cursor.execute(
                 "INSERT INTO usuarios (email,nombres,apellidos,password) VALUES(%s,%s,%s,%s)", (email,nombres,apellidos,hash_password,))
            conexion.commit()
            conexion.close()
            return ("Bienvenido! registro exitoso")
        else :    
            conexion.commit()
            conexion.close()
            return ("El usuario ya esta registrado")

#http://127.0.0.1:5000/login?email=biki@gmail.com&password=Viki9424
class LoginControllers(MethodView):
    """
        Login
    """
    def post(self):
        password = bytes(str(request.args.get("password")), encoding= 'utf-8')
        email = request.args.get("email")
        create_login_schema = CreateLoginSchema()
        errors = create_login_schema.validate(request.args)
        if errors:
            return errors, 400
        salt = bcrypt.gensalt()
        user_password= bcrypt.hashpw(bytes(str(password), encoding= 'utf-8'), salt)
        conexion=crear_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT password,email,nombres FROM usuarios WHERE email=%s", (email, )
        )
        auto = cursor.fetchone()
        conexion.close()

        if auto==None:
            return jsonify({"msg": "usuario no registrado 22"}), 400

        db_password = bytes(auto[0], encoding="utf-8")

        if (auto[1]==email):
            if not bcrypt.checkpw(user_password, db_password):
                encoded_jwt = jwt.encode({'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=100), 'email': email}, KEY_TOKEN_AUTH , algorithm='HS256')
                return jsonify({"msg": "login exitoso","usuario":auto[2], "token ": encoded_jwt}), 200
        else:
            return jsonify({"msg": "Correo o clave incorrecta"}), 400


#http://127.0.0.1:5000/crearproducto

# json:
# {
# "nombre": "sal",
# "precio": 800
#}

# header:
# Authorization : Bearer <<token>>>
# 

class CrearproductosControllers(MethodView):
    def post(self):
        content = request.get_json()
        errors=create_crearproducto_schema.validate(content)

        if errors:
            return errors,400

        authHeader = request.headers.get("Authorization")
        partes_auth = authHeader.split(" ")
        if len(partes_auth) != 2:
            return jsonify({"msg": "No se ha proporcionado un token válido"}), 400
        token = partes_auth[1]

        try:
            decoded_token = jwt.decode(token, KEY_TOKEN_AUTH, algorithms=['HS256'])
        except Exception as e:
            print(e)
            return jsonify({"msg":"Token inválido"}), 400
        
        conexion=crear_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT * FROM productos WHERE nombre=%s and precio=%s",
            (content.get("nombre"), content.get("precio"))
        )
        auto=cursor.fetchone()
        if auto==None:
            cursor.execute(
            "INSERT INTO productos(nombre,precio) VALUES(%s,%s)", (content.get("nombre"),content.get("precio"),))
            conexion.commit()
            conexion.close()
            return jsonify({"Producto creado":content}),200
            
        else:
            conexion.commit()
            conexion.close()
            return ("El producto ya esta registrado"),400
 
    


       
#http://127.0.0.1:5000/productos
class ProductosControllers(MethodView):
    """
        json
    """
    def get(self):
        try:

            conexion=crear_conexion()
            cursor = conexion.cursor(pymysql.cursors.DictCursor)

            cursor.execute("SELECT * FROM productos")
            productos = cursor.fetchall()
            return jsonify({"productos":productos}), 200
        except Exception as e:
            print(e)
            return jsonify({"msg":"Se encontro un error en la solicitud"}), 500
        finally:
            conexion.close()
