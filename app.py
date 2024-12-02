from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from config import Config
from models import db, Usuario, Evento, Reserva
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from flask_cors import CORS

PORT = 5001

QUERY_CREAR_EVENTO = """
    INSERT INTO eventos (nombre_evento, categoria, descripcion, entradas_totales, entradas_disponibles, 
        fecha_hora, localizacion, es_recomendacion, precio_entrada, imagen_url
    )
    VALUES (
        :nombre_evento, :categoria, :descripcion, :entradas_totales, :entradas_disponibles, 
        :fecha_hora, :localizacion, :es_recomendacion, :precio_entrada, :imagen_url
        )
"""


QUERY_INGRESAR_RESERVA = "INSERT INTO reservas (id_usuario, id_evento, id_reserva, cant_tickets) VALUES (:id_usuario, :id_evento,  :id_reserva, :cant_tickets)"
QUERY_ELIMINAR_RESERVA = "DELETE FROM reservas WHERE id_reserva = :id_reserva"
QUERY_RESERVAS_EVENTO = "SELECT COUNT(*) FROM eventos WHERE id_evento = :id_evento"
QUERY_ELIMINAR_EVENTO = "DELETE FROM eventos WHERE id_evento = :id_evento"
QUERY_RESERVA_POR_ID = """SELECT R.id_reserva, R.cant_tickets, U.nombre, E.nombre_evento, E.precio_entrada FROM reservas R
INNER JOIN usuarios U on U.id_usuario = R.id_usuario
INNER JOIN eventos E on E.id_evento = R.id_evento
WHERE id_reserva = :id_reserva"""
QUERY_TODOS_LOS_EVENTOS = " SELECT id_evento, nombre_evento, categoria, descripcion, entradas_disponibles, localizacion, precio_entrada, imagen_url from eventos "
QUERY_EVENTOS_POR_CATEGORIA = "SELECT id_evento, nombre_evento, categoria, descripcion, entradas_totales, entradas_disponibles, fecha_hora, localizacion, es_recomendacion, precio_entrada, imagen_url FROM eventos WHERE categoria = :categoria"
QUERY_EVENTOS_POR_ID = "SELECT id_evento, nombre_evento, categoria, descripcion, entradas_totales, entradas_disponibles, fecha_hora, localizacion, es_recomendacion, precio_entrada, imagen_url  FROM eventos WHERE id_evento = :id_evento"
QUERY_EVENTOS_RECOMENDADOS = "SELECT id_evento, nombre_evento, categoria, descripcion, entradas_totales, entradas_disponibles, fecha_hora, localizacion, es_recomendacion, precio_entrada, imagen_url FROM eventos WHERE es_recomendacion = 1"


app = Flask(__name__)
CORS(app)
app.config.from_object(Config)
db.init_app(app)
app.secret_key = 'coqui2529'
# Recordar que los datos de la db en cuanto a nombre, usuario y contraseña varian.
engine = create_engine("mysql+mysqlconnector://Ruy:universe1234@Ruy.mysql.pythonanywhere-services.com/Ruy$universe")


def run_query(query, parameters=None):
    try:
        with engine.connect() as conn:
            with conn.begin():
                result = conn.execute(text(query), parameters)
                return result
    except Exception as e:
        print(f"Error ejecutando la consulta: {e}")
        return None

@app.route('/')
def index():
    return jsonify({"message": "Bienvenido al backend"})

#------------------------------------------------------------------------------------- TABLA USUARIOS | LOGIN

@app.route('/usuarios-password', methods=['POST'])
def tabla_usuarios():
    
    data = request.json
    nombre_usuario = data['nombre']
    password = data['password']


    usuario = Usuario.query.filter_by(nombre=nombre_usuario).first()

    if usuario and usuario.password == password:
        return jsonify({'success': True, 'es_admin': usuario.es_admin, 'id_usuario': usuario.id_usuario}), 200
    else:
        return jsonify({'success': False, 'message': 'Usuario no autenticado'}), 401

#------------------------------------------------------------------------------------- TABLA RESERVAS | PAGO
@app.route('/crear-reserva', methods=['POST'])
def tabla_reservas():
    data = request.json
    nombre = data['nombre']
    id_evento = data['id_evento']
    cant_tickets = data['cant_tickets']

    if not nombre or not id_evento or not cant_tickets:
        return jsonify({'success': False, 'message': 'Faltan datos'}), 400

    try:
        usuario = Usuario.query.filter_by(nombre=nombre).first()
        evento = Evento.query.filter_by(id_evento=id_evento).first()

        if not usuario:
            return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

        if not evento:
            return jsonify({'success': False, 'message': 'Evento no encontrado'}), 404

        nueva_reserva = Reserva(id_usuario=usuario.id_usuario, id_evento=evento.id_evento, cant_tickets=cant_tickets)
        db.session.add(nueva_reserva)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Reserva creada'}), 201

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    
#-------------------------------------------------------------------------------------


#----METODO GET, CONSULTAR RESERVA POR ID DE RESERVA -----#
def reserva_by_id(id_reserva):
    return run_query(QUERY_RESERVA_POR_ID, {'id_reserva': id_reserva}).fetchone()




@app.route('/consultar-reserva/<int:id_reserva>', methods=['GET'])
def consultar_reserva(id_reserva):
    try:
        result = reserva_by_id(id_reserva)
        
        if result is None:
            return jsonify({'error': 'No se encontró la reserva'}), 404  # Not found
            
        return jsonify({
            'id_reserva': result[0],
            'cant_tickets': result[1],
            'nombre_usuario': result[2],
            'nombre_evento': result[3],
            'precio_entrada': float(result[4])  # Convertimos a float el precio
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500






#---METODO POST, INSERTAR RESERVAS ----#


def insertar_reserva(data):
    run_query(QUERY_INGRESAR_RESERVA, data)

@app.route('/crear-reserva', methods=['POST'])
def add_reserva():
    data = request.get_json()

    keys = ('id_usuarios', 'id_evento', 'id_reserva', 'cant_tickets')
    for key in keys:
        if key not in data:
            return jsonify({'error': f'Falta el dato {key}'}), 400

    try:
        result = reserva_by_id(data['id_reserva'])
        if len(result) > 0:
            return jsonify({'error': 'La reserva ya existe'}), 400

        insertar_reserva(data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify(data), 201

#---METODO DELETE, ELIMINAR RESERVA ----#


@app.route('/eliminar-reserva/<int:id_reserva>', methods=['DELETE'])
def eliminar_reserva(id_reserva):
    try:
        result = run_query(QUERY_ELIMINAR_RESERVA, {'id_reserva': id_reserva})
        
        if result.rowcount == 0:
            return jsonify({'error': 'No se encontró una reserva con este ID'}), 404

        return jsonify({'mensaje': f'La reserva ID {id_reserva} fue eliminada'}), 200

    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500


#--------------------------------------------------------TABLA EVENTOS-----------------------------------#

#----METODO GET, CONSULTAR EVENTO POR NOMBRE DE CATEGORIA -----#

def eventos_por_categoria(categoria):
    return run_query(QUERY_EVENTOS_POR_CATEGORIA, {'categoria': categoria}).fetchall()

@app.route('/consultar-eventos/<string:categoria>', methods=['GET'])
def consultar_eventos_por_categoria(categoria):
    try:
        result = eventos_por_categoria(categoria)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    if len(result) == 0:
        return jsonify({'error': 'No se encontró eventos'}), 404 # Not found

    response = []
    for row in result:
        response.append({'id_evento': row[0],
                        'nombre_evento': row[1],
                        'categoria': row[2],
                        'descripcion': row[3], 
                        'entradas_totales':row[4],
                        'entradas_disponibles':row[5],
                        'fecha_hora':row[6],
                        'localizacion':row[7],
                        'es_recomendacion':row[8],
                        'precio_entrada':row[9],
                        'imagen_url': row[10]})
    return jsonify(response), 200

#----METODO GET, CONSULTAR EVENTO POR ID DE EVENTO -----#

def eventos_por_id(id_evento):
    return run_query(QUERY_EVENTOS_POR_ID, {'id_evento': id_evento}).fetchall()

@app.route('/consultar-eventos/<int:id_evento>', methods=['GET'])
def consultar_eventos_por_id(id_evento):
    try:
        result = eventos_por_id(id_evento)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    if len(result) == 0:
        return jsonify({'error': 'No se encontró evento'}), 404 # Not found

    result=result[0]
    response = {'id_evento': result[0],
                        'nombre_evento': result[1],
                        'categoria': result[2],
                        'descripcion': result[3], 
                        'entradas_totales':result[4],
                        'entradas_disponibles':result[5],
                        'fecha_hora':result[6],
                        'localizacion':result[7],
                        'es_recomendacion':result[8],
                        'precio_entrada':result[9],
                        'imagen_url': result[10]}
    return jsonify(response), 200

def eventos_recomendados():
    return run_query(QUERY_EVENTOS_RECOMENDADOS).fetchall()
@app.route('/consultar-eventos-recomendados', methods=['GET'])
def consultar_eventos_recomendados():
    try:
        result = eventos_recomendados()
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    if len(result) == 0:
        return jsonify({'error': 'No se encontró eventos'}), 404 # Not found
    response = []
    for row in result:
        if row[8] == 1:
            response.append({'id_evento': row[0],
                            'nombre_evento': row[1],
                            'categoria': row[2],
                            'descripcion': row[3], 
                            'entradas_totales':row[4],
                            'entradas_disponibles':row[5],
                            'fecha_hora':row[6],
                            'localizacion':row[7],
                            'es_recomendacion':row[8],
                            'precio_entrada':row[9],
                            'imagen_url': row[10]})
    return jsonify(response), 200

def eventos():
    return run_query(QUERY_TODOS_LOS_EVENTOS).fetchall()

@app.route('/consultar-eventos', methods=['GET'])
def obtener_eventos():
    try:
        result = eventos()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    response = []
    for row in result:
        response.append({'id_evento': row[0], 'nombre_evento': row[1], 'categoria': row[2], 'descripcion': row[3], 'entradas_disponibles':row[4], 'localizacion':row[5], 'precio_entrada':row[6]})

    return jsonify(response), 200


@app.route('/eliminar-reserva/<int:id_reserva>', methods=['DELETE'])
def eliminar_evento(id_evento):
    try:      
        result_reservas = run_query(QUERY_RESERVAS_EVENTO, {'id_evento': id_evento}).fetchone()

        if result_reservas[0] > 0:
        
            run_query(QUERY_ELIMINAR_RESERVA, {'id_evento': id_evento})
        
        result = run_query(QUERY_ELIMINAR_EVENTO, {'id_evento': id_evento})

        if result.rowcount == 0:
            return jsonify({'error': 'No se encontró un evento con este ID'}), 404

        return jsonify({'mensaje': f'El evento ID {id_evento} fue eliminado junto con sus reservas'}), 200
    
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500
    
#- --- - -- - -crear evento---


@app.route('/crear_evento', methods=['GET'])
def crear_evento_form():
    return render_template('crear_evento.html')

@app.route('/api/crear_evento', methods=['POST'])
def api_crear_evento():
    """
    Maneja la creación de un nuevo evento desde el formulario HTML.
    """
    try:
        data = request.form

        campos_requeridos = ['nombre_evento', 
            'categoria', 
            'descripcion', 
            'entradas_totales',
            'entradas_disponibles', 
            'fecha_hora', 
            'localizacion', 
            'precio_entrada',
            'imagen_url']
        if not all(campo in data for campo in campos_requeridos):
            return jsonify({"error": "Faltan campos requeridos."}), 400

        run_query(QUERY_CREAR_EVENTO, {
            'nombre_evento': data['nombre_evento'],
            'categoria': data['categoria'],
            'descripcion': data['descripcion'],
            'entradas_totales': data['entradas_totales'],
            'entradas_disponibles': data['entradas_disponibles'],
            'fecha_hora': data['fecha_hora'],
            'localizacion': data['localizacion'],
            'precio_entrada': data['precio_entrada'],'imagen_url': data['imagen_url'],
            'es_recomendacion': 0 
        })
        
        return redirect('https://ruy.pythonanywhere.com/')

    except SQLAlchemyError as e:
        return jsonify({"error": f"Error al crear el evento: {str(e)}"}), 400
    
    