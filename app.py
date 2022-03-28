from flask import Flask
from routes import *
from flask_cors import CORS

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})


app.add_url_rule(routes["register"], view_func=routes["register_controllers"])
app.add_url_rule(routes["login"], view_func=routes["login_controllers"])
app.add_url_rule(routes["crearproducto"], view_func=routes["crearproducto_controllers"])
app.add_url_rule(routes["productos"], view_func=routes["productos_controllers"])

