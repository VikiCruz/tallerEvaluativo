from controllers import RegisterControllers
from controllers import LoginControllers
from controllers import CrearproductosControllers
from controllers import ProductosControllers

routes = {"register": "/register", "register_controllers":RegisterControllers.as_view("register_api"),
"login": "/login", "login_controllers":LoginControllers.as_view("login_api"),
"crearproducto": "/crearproducto", "crearproducto_controllers":CrearproductosControllers.as_view("crearproducto_api"),
"productos": "/productos", "productos_controllers":ProductosControllers.as_view("productos_api"),

}
