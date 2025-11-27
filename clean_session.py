from flask import Flask

app = Flask(__name__)
app.secret_key = 'temp_clean_key'

with app.test_request_context():
    # Esto limpia toda la sesión
    from flask import session
    session.clear()
    print("✅ Sesión limpiada completamente")

print("Ejecuta: python app.py")