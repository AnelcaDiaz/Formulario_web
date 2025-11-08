# Importación de librerías necesarias
from flask import Flask, request, jsonify, render_template
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime
import traceback

# -------------------------------
# Configuración de la aplicación
# -------------------------------
app = Flask(__name__)

DB_CONFIG = {
    "host": "localhost",
    "database": "Registros",  # Nombre de la base de datos
    "user": "postgres",
    "password": "123456",
    "port": 5432
}

# ---------------------------------------------------------
# Función para conectar la base de datos PostgreSQL
# ---------------------------------------------------------
def conectar_bd():
    try:
        return psycopg2.connect(**DB_CONFIG)
    except psycopg2.Error as e:
        print(f"Error al conectarse con la base de datos: {e}")
        return None

# ---------------------------------------------------------
# Página principal - Carga el archivo index.html
# ---------------------------------------------------------
@app.route('/')
def inicio():
    return render_template('index.html')

# ---------------------------------------------------------
# Ruta para guardar los datos del formulario de contacto
# ---------------------------------------------------------
@app.route('/Formulario', methods=['POST'])
def guardar_contacto():
    try: 
        # Acepta tanto JSON como datos enviados desde formulario HTML
        datos = request.get_json(silent=True) or request.form  # Cambiado: silent=True evita la excepción

        nombre = datos.get('nombre','').strip()
        apellido= datos.get('apellido','').strip()
        direccion= datos.get('direccion','').strip()
        telefono= datos.get('telefono','').strip()
        correo = datos.get('correo', '').strip()
        mensaje = datos.get('mensaje', '').strip()
        
        # Validación de campos obligatorios
        if not nombre or not correo:
            return jsonify({
                'error': 'Nombre y correo son obligatorios'
            }), 400  
        if not apellido or not direccion:
            return jsonify({
                'error': 'Apellido y dirección son obligatorios'
            }), 400  
        conexion = conectar_bd()
        if conexion is None:
            return jsonify({'error': 'Error al conectar con la base de datos'}), 500

        cursor = conexion.cursor()
        
        # Sentencia SQL para insertar los datos (agregado 'creado' si es necesario)
        sql_insert = """
        INSERT INTO "Formulario" (nombre, apellido, direccion, telefono, correo, mensaje, creado)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
        """  
        
        cursor.execute(sql_insert, (nombre, apellido, direccion, telefono, correo, mensaje, datetime.now()))
        contacto_id = cursor.fetchone()[0]
        
        conexion.commit()
        cursor.close()
        conexion.close()
        
        # Respuesta exitosa al usuario
        return jsonify({
            "mensaje": "Contacto guardado exitosamente",
            "id": contacto_id
        }), 201

    except Exception as e:
        print(f"Error al guardar el contacto: {e}")
        traceback.print_exc()
        return jsonify({
            'error': 'Error interno al guardar el contacto'
        }), 500

# ---------------------------------------------------------
# Ruta para ver todos los contactos registrados
# ---------------------------------------------------------
@app.route('/Formulario', methods=['GET'])
def ver_contacto():
    try:
        conexion = conectar_bd()
        if conexion is None:
            return jsonify({
                'error': 'No se pudo conectar a la base de datos'
            }), 500
            
        cursor = conexion.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM "Formulario" ORDER BY creado DESC;')  
        Formulario = cursor.fetchall()
        cursor.close()
        conexion.close()
        
        # Formato de fecha legible
        for contacto in Formulario:
            if contacto['creado']: 
                contacto['creado'] = contacto['creado'].strftime('%Y-%m-%d %H:%M:%S') 
        
        return jsonify(Formulario), 200
    
    except Exception as e:
        print(f"Error al obtener los contactos: {e}") 
        traceback.print_exc()
        return jsonify({
            'error': 'Error interno al obtener los contactos'  
        }), 500

# ---------------------------------------------------------
# Inicio del servidor Flask
# ---------------------------------------------------------
if __name__ == '__main__':
    print("Iniciando el servidor...")
    app.run(debug=True)