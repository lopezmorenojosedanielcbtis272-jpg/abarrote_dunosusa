from flask import Flask, request, redirect, url_for, session
from flask_pymongo import PyMongo
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'clave_secreta_muy_segura_123'

# CONFIGURACIÓN MONGODB ATLAS
app.config["MONGO_URI"] = "mongodb+srv://lopezmorenojosedanielcbtis272_db_user:admin123@cluster0.ajwpjn1.mongodb.net/abarrote_dunososa?retryWrites=true&w=majority"

# Inicializar MongoDB
try:
    mongo = PyMongo(app)
    mongo.db.command('ping')
    print("✅ Conectado a MongoDB Atlas exitosamente")
except Exception as e:
    print(f"❌ Error conectando a MongoDB Atlas: {e}")

# Datos de productos
productos = {
    "bebidas": [
        {"id": 1, "nombre": "JUGOS", "precio": 15.50, "imagen": "https://chefmart.com.mx/cdn/shop/files/DURAZNO250ML_1600x.png?v=1721775215", "categoria": "bebidas"},
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

def html_header(title):
    return f'''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: Arial, sans-serif; }}
            body {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            header {{ background: rgba(255,255,255,0.95); padding: 20px; border-radius: 15px; margin-bottom: 20px; }}
            h1 {{ color: #2c3e50; margin-bottom: 10px; }}
            .slogan {{ color: #7f8c8d; font-style: italic; }}
            .user-actions {{ margin-top: 15px; }}
            .btn {{ display: inline-block; padding: 10px 20px; background: #e74c3c; color: white; 
                   text-decoration: none; border-radius: 25px; margin-right: 10px; border: none; cursor: pointer; }}
            .btn-success {{ background: #27ae60; }}
            .btn-info {{ background: #3498db; }}
            .categoria {{ background: white; padding: 20px; border-radius: 15px; margin-bottom: 20px; }}
            .categoria-titulo {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                               color: white; padding: 15px; border-radius: 10px; margin-bottom: 15px; }}
            .productos-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; }}
            .producto {{ background: #f8f9fa; padding: 15px; border-radius: 10px; text-align: center; }}
            .producto-nombre {{ font-weight: bold; margin: 10px 0; }}
            .producto-precio {{ color: #e74c3c; font-size: 1.2em; font-weight: bold; }}
            .success {{ background: #27ae60; color: white; padding: 20px; border-radius: 10px; margin: 20px 0; }}
            .form-container {{ max-width: 500px; margin: 50px auto; padding: 30px; background: white; border-radius: 15px; }}
            .form-group {{ margin: 15px 0; }}
            .form-group label {{ display: block; margin-bottom: 5px; font-weight: bold; }}
            .form-group input {{ width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 10px; }}
            .carrito-container {{ max-width: 800px; margin: 20px auto; padding: 20px; background: white; border-radius: 15px; }}
            .tabla-carrito {{ width: 100%; border-collapse: collapse; }}
            .tabla-carrito th, .tabla-carrito td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            .confirmacion {{ text-align: center; padding: 50px 20px; background: white; border-radius: 15px; margin: 20px auto; max-width: 600px; }}
            .checkmark {{ font-size: 4em; color: #27ae60; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>🛒 Abarrote Dunososa</h1>
                <p class="slogan">Todo a un buen precio</p>
                <div class="user-actions">
    '''

def html_footer():
    return '''
                </div>
            </header>
        </div>
    </body>
    </html>
    '''

def user_actions():
    if 'usuario' in session:
        return f'''
            <span style="margin-right: 15px;">Bienvenido, {session['usuario']}</span>
            <a href="/logout" class="btn">Cerrar Sesión</a>
            <a href="/carrito" class="btn">Carrito 🛒</a>
        '''
    else:
        return '''
            <a href="/registro" class="btn">REGISTRATE</a>
            <a href="/carrito" class="btn">Carrito 🛒</a>
        '''

@app.route('/')
def index():
    return html_header('Abarrote Dunososa - Inicio') + user_actions() + f'''
            

            <div class="categoria">
                <h2 class="categoria-titulo">🥤 BEBIDAS</h2>
                <div class="productos-grid">
    ''' + ''.join([f'''
                    <div class="producto">
                        <h3 class="producto-nombre">{p['nombre']}</h3>
                        <p class="producto-precio">${p['precio']:.2f}</p>
                        <form action="/agregar_carrito" method="post" style="margin-top: 10px;">
                            <input type="hidden" name="producto_id" value="{p['id']}">
                            <input type="number" name="cantidad" value="1" min="1" style="width: 60px; padding: 5px; margin: 5px;">
                            <button type="submit" class="btn">Agregar al Carrito</button>
                        </form>
                    </div>
    ''' for p in productos['bebidas']]) + '''
                </div>
            </div>

            <div class="categoria">
                <h2 class="categoria-titulo">🧼 DETERGENTES</h2>
                <div class="productos-grid">
    ''' + ''.join([f'''
                    <div class="producto">
                        <h3 class="producto-nombre">{p['nombre']}</h3>
                        <p class="producto-precio">${p['precio']:.2f}</p>
                        <form action="/agregar_carrito" method="post" style="margin-top: 10px;">
                            <input type="hidden" name="producto_id" value="{p['id']}">
                            <input type="number" name="cantidad" value="1" min="1" style="width: 60px; padding: 5px; margin: 5px;">
                            <button type="submit" class="btn">Agregar al Carrito</button>
                        </form>
                    </div>
    ''' for p in productos['detergentes']]) + '''
                </div>
            </div>

            <div class="categoria">
                <h2 class="categoria-titulo">🍿 SABRITAS</h2>
                <div class="productos-grid">
    ''' + ''.join([f'''
                    <div class="producto">
                        <h3 class="producto-nombre">{p['nombre']}</h3>
                        <p class="producto-precio">${p['precio']:.2f}</p>
                        <form action="/agregar_carrito" method="post" style="margin-top: 10px;">
                            <input type="hidden" name="producto_id" value="{p['id']}">
                            <input type="number" name="cantidad" value="1" min="1" style="width: 60px; padding: 5px; margin: 5px;">
                            <button type="submit" class="btn">Agregar al Carrito</button>
                        </form>
                    </div>
    ''' for p in productos['sabritas']]) + '''
                </div>
            </div>
    ''' + html_footer()

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        password = request.form['password']
        
        # Verificar si el usuario ya existe
        if mongo.db.usuarios.find_one({'email': email}):
            return html_header('Registro - Error') + user_actions() + '''
                <div class="form-container">
                    <h2>REGISTRATE</h2>
                    <p style="color: #e74c3c; background: #ffeaa7; padding: 10px; border-radius: 5px;">
                        ❌ El usuario ya existe
                    </p>
                    <form method="post">
                        <div class="form-group">
                            <label for="nombre">Nombre y apellido</label>
                            <input type="text" id="nombre" name="nombre" required value="''' + nombre + '''">
                        </div>
                        <div class="form-group">
                            <label for="email">Correo electrónico</label>
                            <input type="email" id="email" name="email" required value="''' + email + '''">
                        </div>
                        <div class="form-group">
                            <label for="password">Contraseña</label>
                            <input type="password" id="password" name="password" required>
                        </div>
                        <button type="submit" class="btn" style="width: 100%; padding: 15px;">Confirmar registro</button>
                    </form>
                    <p style="text-align: center; margin-top: 20px;">
                        <a href="/">← Volver al inicio</a>
                    </p>
                </div>
            ''' + html_footer()
        
        # Insertar nuevo usuario
        mongo.db.usuarios.insert_one({
            'nombre': nombre,
            'email': email,
            'password': password,
            'fecha_registro': datetime.now()
        })
        
        session['usuario'] = email
        session['carrito'] = []
        return redirect('/')
    
    return html_header('Registro') + user_actions() + '''
        <div class="form-container">
            <h2>REGISTRATE</h2>
            <p class="slogan">Para ver nuestros precios especiales, regístrate aquí!</p>
            <form method="post">
                <div class="form-group">
                    <label for="nombre">Nombre y apellido</label>
                    <input type="text" id="nombre" name="nombre" required>
                </div>
                <div class="form-group">
                    <label for="email">Correo electrónico</label>
                    <input type="email" id="email" name="email" required>
                </div>
                <div class="form-group">
                    <label for="password">Contraseña</label>
                    <input type="password" id="password" name="password" required>
                </div>
                <button type="submit" class="btn" style="width: 100%; padding: 15px;">Confirmar registro</button>
            </form>
            <p style="text-align: center; margin-top: 20px;">
                <a href="/">← Volver al inicio</a>
            </p>
        </div>
    ''' + html_footer()

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    
    usuario = mongo.db.usuarios.find_one({'email': email, 'password': password})
    
    if usuario:
        session['usuario'] = email
        session['carrito'] = session.get('carrito', [])
        return redirect('/')
    else:
        return redirect('/')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/agregar_carrito', methods=['POST'])
def agregar_carrito():
    if 'usuario' not in session:
        return redirect('/registro')
    
    producto_id = int(request.form['producto_id'])
    cantidad = int(request.form['cantidad'])
    
    # Buscar el producto
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
        
        # Verificar si el producto ya está en el carrito
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
    
    return redirect('/carrito')

@app.route('/carrito')
def ver_carrito():
    if 'usuario' not in session:
        return redirect('/registro')
    
    carrito = session.get('carrito', [])
    total = sum(item['precio'] * item['cantidad'] for item in carrito)
    
    carrito_html = ''
    if carrito:
        carrito_html = '''
            <table class="tabla-carrito">
                <thead>
                    <tr>
                        <th>Producto</th>
                        <th>Precio</th>
                        <th>Cantidad</th>
                        <th>Subtotal</th>
                        <th>Acciones</th>
                    </tr>
                </thead>
                <tbody>
        ''' + ''.join([f'''
                    <tr>
                        <td>{item['nombre']}</td>
                        <td>${item['precio']:.2f}</td>
                        <td>
                            <form action="/actualizar_carrito" method="post" style="display: inline;">
                                <input type="hidden" name="producto_id" value="{item['id']}">
                                <input type="number" name="cantidad" value="{item['cantidad']}" min="1" style="width: 60px; padding: 5px;">
                                <button type="submit" class="btn btn-info">Actualizar</button>
                            </form>
                        </td>
                        <td>${item['precio'] * item['cantidad']:.2f}</td>
                        <td>
                            <form action="/actualizar_carrito" method="post" style="display: inline;">
                                <input type="hidden" name="producto_id" value="{item['id']}">
                                <input type="hidden" name="cantidad" value="0">
                                <button type="submit" class="btn">Eliminar</button>
                            </form>
                        </td>
                    </tr>
        ''' for item in carrito]) + f'''
                </tbody>
                <tfoot>
                    <tr>
                        <td colspan="3" style="text-align: right; font-weight: bold;">Total:</td>
                        <td colspan="2" style="font-weight: bold; color: #e74c3c;">${total:.2f}</td>
                    </tr>
                </tfoot>
            </table>
            <div style="margin-top: 20px; text-align: center;">
                <a href="/" class="btn btn-info">← Seguir Comprando</a>
                <a href="/vaciar_carrito" class="btn">Vaciar Carrito</a>
                <form action="/procesar_pago" method="post" style="display: inline;">
                    <button type="submit" class="btn btn-success">Proceder al Pago</button>
                </form>
            </div>
        '''
    else:
        carrito_html = '''
            <div style="text-align: center; padding: 40px;">
                <div style="font-size: 4em;">🛒</div>
                <h3>Tu carrito está vacío</h3>
                <p>¡Agrega algunos productos increíbles!</p>
                <a href="/" class="btn btn-info">Ir a Comprar</a>
            </div>
        '''
    
    return html_header('Carrito de Compras') + user_actions() + f'''
        <div class="carrito-container">
            <h2>🛒 Tu Carrito de Compras</h2>
            {carrito_html}
        </div>
    ''' + html_footer()

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
    return redirect('/carrito')

@app.route('/vaciar_carrito')
def vaciar_carrito():
    session['carrito'] = []
    session.modified = True
    return redirect('/carrito')

@app.route('/procesar_pago', methods=['POST'])
def procesar_pago():
    if 'usuario' not in session:
        return redirect('/registro')
    
    carrito = session.get('carrito', [])
    
    if not carrito:
        return redirect('/carrito')
    
    total = sum(item['precio'] * item['cantidad'] for item in carrito)
    
    # Guardar el pedido en MongoDB Atlas
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
        
        # Vaciar el carrito después del pago
        session['carrito'] = []
        session.modified = True
        
        return html_header('Confirmación de Pago') + user_actions() + f'''
            <div class="confirmacion">
                <div class="checkmark">✓</div>
                <h2>¡Pago Realizado Exitosamente!</h2>
                <p>Tu pedido ha sido procesado correctamente y está siendo preparado.</p>
                <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0;">
                    <p><strong>📦 Número de Pedido:</strong> {pedido['numero_pedido']}</p>
                    <p><strong>💰 Total Pagado:</strong> ${total:.2f}</p>
                    <p><strong>👤 Cliente:</strong> {session['usuario']}</p>
                </div>
                <div style="margin-top: 30px;">
                    <a href="/" class="btn btn-success">🛍️ Seguir Comprando</a>
                </div>
                <div style="background: #667eea; color: white; padding: 15px; border-radius: 10px; margin-top: 20px;">
                    <h3>📊 Información almacenada en MongoDB Atlas</h3>
                    <p>✅ Los datos de tu pedido han sido guardados exitosamente</p>
                </div>
            </div>
        ''' + html_footer()
        
    except Exception as e:
        return redirect('/carrito')

if __name__ == '__main__':
    app.run(debug=True)


