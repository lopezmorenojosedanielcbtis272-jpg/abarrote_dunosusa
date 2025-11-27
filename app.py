from flask import Flask, render_template, request, redirect, url_for, session
from flask_pymongo import PyMongo
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'nueva_clave_secreta_123'

# CONFIGURACIÓN MONGODB ATLAS
app.config["MONGO_URI"] = "mongodb+srv://lopezmorenojosedanielcbtis272_db_user:admin123@cluster0.ajwpjn1.mongodb.net/abarrote_dunososa?retryWrites=true&w=majority"

# Configuración para imágenes
app.config['UPLOAD_FOLDER'] = 'static/img'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

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

@app.route('/')
def index():
    return render_template('index.html', productos=productos, usuario=session.get('usuario'))

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        password = request.form['password']
        
        if mongo.db.usuarios.find_one({'email': email}):
            return render_template('registro.html', error="El usuario ya existe")
        
        mongo.db.usuarios.insert_one({
            'nombre': nombre,
            'email': email,
            'password': password,
            'fecha_registro': datetime.now()
        })
        
        session['usuario'] = email
        session['carrito'] = []
        return redirect(url_for('index'))
    
    return render_template('registro.html')

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
        return render_template('index.html', productos=productos, error="Credenciales incorrectas")

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
    
    return redirect(url_for('ver_carrito'))

@app.route('/carrito')
def ver_carrito():
    if 'usuario' not in session:
        return redirect(url_for('registro'))
    
    carrito = session.get('carrito', [])
    total = sum(item['precio'] * item['cantidad'] for item in carrito)
    return render_template('carrito.html', carrito=carrito, total=total)

@app.route('/actualizar_carrito', methods=['POST'])
def actualizar_carrito():
    producto_id = int(request.form['producto_id'])
    nueva_cantidad = int(request.form['cantidad'])
    
    carrito = session.get('carrito', [])
    
    if nueva_cantidad <= 0:
        carrito = [item for item in carrito if item['id'] != producto_id]
    else:
        for item in carrito:
            if item['id'] == producto_id:
                item['cantidad'] = nueva_cantidad
                break
    
    session['carrito'] = carrito
    session.modified = True
    return redirect(url_for('ver_carrito'))

@app.route('/vaciar_carrito')
def vaciar_carrito():
    session['carrito'] = []
    session.modified = True
    return redirect(url_for('ver_carrito'))

@app.route('/procesar_pago', methods=['POST'])
def procesar_pago():
    if 'usuario' not in session:
        return redirect(url_for('registro'))
    
    carrito = session.get('carrito', [])
    
    if not carrito:
        return redirect(url_for('ver_carrito'))
    
    total = sum(item['precio'] * item['cantidad'] for item in carrito)
    
    pedido = {
        'usuario': session['usuario'],
        'productos': carrito,
        'total': total,
        'fecha_pedido': datetime.now(),
        'estado': 'completado',
        'numero_pedido': f"PED-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    }
    
    try:
        resultado = mongo.db.pedidos.insert_one(pedido)
        pedido_id = str(resultado.inserted_id)
        
        session['carrito'] = []
        session.modified = True
        
        session['ultimo_pedido_id'] = pedido_id
        session['ultimo_pedido_numero'] = pedido['numero_pedido']
        session['ultimo_pedido_total'] = total
        
        return redirect(url_for('confirmacion_pago'))
        
    except Exception as e:
        return redirect(url_for('ver_carrito'))

@app.route('/confirmacion_pago')
def confirmacion_pago():
    if 'usuario' not in session:
        return redirect(url_for('registro'))
    
    pedido_id = session.get('ultimo_pedido_id')
    pedido_numero = session.get('ultimo_pedido_numero')
    pedido_total = session.get('ultimo_pedido_total')
    
    return render_template('confirmacion_pago.html', 
                         pedido_id=pedido_id,
                         pedido_numero=pedido_numero,
                         pedido_total=pedido_total,
                         now=datetime.now())

@app.route('/buscar', methods=['POST'])
def buscar():
    busqueda = request.form['busqueda'].lower()
    productos_filtrados = {
        "bebidas": [],
        "detergentes": [], 
        "sabritas": []
    }
    
    for categoria, productos_cat in productos.items():
        for producto in productos_cat:
            if busqueda in producto['nombre'].lower():
                productos_filtrados[categoria].append(producto)
    
    return render_template('index.html', productos=productos_filtrados, busqueda=busqueda)

if __name__ == '__main__':
    init_database()
    app.run(debug=True)
