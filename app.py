from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_pymongo import PyMongo
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "dev-secret")

MONGO_URI = os.environ.get("MONGO_URI", "mongodb+srv://lopezmorenojosedanielcbtis272_db_user:admin123@cluster0.ajwpjn1.mongodb.net/abarrote_dunososa?retryWrites=true&w=majority")

# Configurar MongoDB URI para Flask-PyMongo
app.config["MONGO_URI"] = MONGO_URI

# Inicializar MongoDB
try:
    mongo = PyMongo(app)
    mongo.db.command('ping')
    print("✅ Conectado a MongoDB Atlas exitosamente")
except Exception as e:
    print(f"❌ Error conectando a MongoDB Atlas: {e}")
    app.config["MONGO_URI"] = "mongodb://localhost:27017/abarrote_dunososa"
    mongo = PyMongo(app)

# Datos de productos
productos = {
    "bebidas": [
        {"id": 1, "nombre": "JUGOS", "precio": 15.50, "imagen": "jugos.webp", "categoria": "bebidas"},
        {"id": 2, "nombre": "COCACOLA", "precio": 18.00, "imagen": "coca.jpg", "categoria": "bebidas"},
        {"id": 3, "nombre": "FANTA", "precio": 16.50, "imagen": "fanta.jpg", "categoria": "bebidas"}
    ],
    "detergentes": [
        {"id": 4, "nombre": "FABULOSO", "precio": 25.00, "imagen": "fabuloso.webp", "categoria": "detergentes"},
        {"id": 5, "nombre": "CLORO", "precio": 12.00, "imagen": "cloro.webp", "categoria": "detergentes"},
        {"id": 6, "nombre": "SUAVITEL", "precio": 35.00, "imagen": "suavitel.webp", "categoria": "detergentes"}
    ],
    "sabritas": [
        {"id": 7, "nombre": "Takis", "precio": 22.00, "imagen": "takis.webp", "categoria": "sabritas"},
        {"id": 8, "nombre": "Doritos", "precio": 20.00, "imagen": "doritos.jpeg", "categoria": "sabritas"},
        {"id": 9, "nombre": "Cheetos", "precio": 18.00, "imagen": "cheetos.jpg", "categoria": "sabritas"}
    ]
}

def init_database():
    try:
        mongo.db.usuarios.create_index("email", unique=True)
        mongo.db.pedidos.create_index("usuario")
        mongo.db.pedidos.create_index("fecha_pedido")
        print("✅ Índices creados correctamente")
    except Exception as e:
        print(f"⚠️  Error creando índices: {e}")

# Página principal temporal sin plantillas
@app.route('/')
def index():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Abarrote Duñosusa</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <nav class="navbar navbar-dark bg-primary">
            <div class="container">
                <a class="navbar-brand" href="/">🏪 Abarrote Duñosusa</a>
            </div>
        </nav>
        
        <div class="container mt-4">
            <h1>Bienvenido a Abarrote Duñosusa</h1>
            <p>La aplicación está funcionando correctamente.</p>
            <p><strong>Estado de MongoDB:</strong> ✅ Conectado</p>
            
            <div class="mt-4">
                <a href="/registro" class="btn btn-primary">Registrarse</a>
                <a href="/api/productos" class="btn btn-outline-primary">Ver Productos (API)</a>
            </div>
        </div>
    </body>
    </html>
    """
    return html

# Página de registro temporal
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        password = request.form['password']
        
        if mongo.db.usuarios.find_one({'email': email}):
            return "El usuario ya existe. <a href='/registro'>Volver</a>"
        
        mongo.db.usuarios.insert_one({
            'nombre': nombre,
            'email': email,
            'password': password,
            'fecha_registro': datetime.now()
        })
        
        session['usuario'] = email
        session['carrito'] = []
        return redirect(url_for('index'))
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Registro - Abarrote Duñosusa</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <nav class="navbar navbar-dark bg-primary">
            <div class="container">
                <a class="navbar-brand" href="/">🏪 Abarrote Duñosusa</a>
            </div>
        </nav>
        
        <div class="container mt-4">
            <div class="row justify-content-center">
                <div class="col-md-6">
                    <h2>Registrarse</h2>
                    <form method="POST">
                        <div class="mb-3">
                            <label class="form-label">Nombre completo</label>
                            <input type="text" name="nombre" class="form-control" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Email</label>
                            <input type="email" name="email" class="form-control" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Contraseña</label>
                            <input type="password" name="password" class="form-control" required>
                        </div>
                        <button type="submit" class="btn btn-primary w-100">Registrarse</button>
                    </form>
                    <div class="text-center mt-3">
                        <a href="/">¿Ya tienes cuenta? Inicia sesión</a>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return html

# API para ver productos (temporal)
@app.route('/api/productos')
def api_productos():
    return jsonify(productos)

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    
    usuario = mongo.db.usuarios.find_one({'email': email, 'password': password})
    
    if usuario:
        session['usuario'] = email
        session['carrito'] = session.get('carrito', [])
        return redirect(url_for('index'))
    else:
        return "Credenciales incorrectas. <a href='/'>Volver</a>"

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/agregar_carrito', methods=['POST'])
def agregar_carrito():
    if 'usuario' not in session:
        return redirect(url_for('registro'))
    
    producto_id = int(request.form['producto_id'])
    cantidad = int(request.form['cantidad'])
    
    producto_encontrado = None
    for categoria in productos.values():
        for producto in categoria:
            if producto['id'] == producto_id:
                producto_encontrado = producto
                break
        if producto_encontrado:
            break
    
    if producto_encontrado:
        carrito = session.get('carrito', [])
        
        producto_en_carrito = None
        for item in carrito:
            if item['id'] == producto_id:
                producto_en_carrito = item
                break
        
        if producto_en_carrito:
            producto_en_carrito['cantidad'] += cantidad
        else:
            carrito.append({
                'id': producto_id,
                'nombre': producto_encontrado['nombre'],
                'precio': producto_encontrado['precio'],
                'imagen': producto_encontrado['imagen'],
                'cantidad': cantidad
            })
        
        session['carrito'] = carrito
        session.modified = True
    
    return "Producto agregado al carrito. <a href='/'>Volver</a>"

@app.route('/carrito')
def ver_carrito():
    if 'usuario' not in session:
        return redirect(url_for('registro'))
    
    carrito = session.get('carrito', [])
    total = sum(item['precio'] * item['cantidad'] for item in carrito)
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Carrito - Abarrote Duñosusa</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <nav class="navbar navbar-dark bg-primary">
            <div class="container">
                <a class="navbar-brand" href="/">🏪 Abarrote Duñosusa</a>
            </div>
        </nav>
        
        <div class="container mt-4">
            <h1>🛒 Tu Carrito</h1>
            {"".join([f"<p>{item['nombre']} - ${item['precio']} x {item['cantidad']}</p>" for item in carrito])}
            <h3>Total: ${total}</h3>
            <a href="/" class="btn btn-primary">Seguir comprando</a>
        </div>
    </body>
    </html>
    """
    return html

if __name__ == '__main__':
    init_database()
    app.run(debug=True)
