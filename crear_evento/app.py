from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

# Queries SQL
QUERY_CREAR_EVENTO = """
    INSERT INTO eventos (nombre_evento, categoria, descripcion, entradas_disponibles, localizacion, precio_entrada)
    VALUES (:nombre_evento, :categoria, :descripcion, :entradas_disponibles, :localizacion, :precio_entrada)
"""

""" app = Flask(__name__) """
app = Flask(__name__, template_folder='../FRONT/templates', static_folder='../FRONT/static')

app.secret_key = 'coqui2529'    
""" db.init_app(app) """

engine = create_engine("mysql+mysqlconnector://root:coqui2529@localhost:3306/universe")


def run_query(query, parameters=None):
    with engine.connect() as conn:
        print(f"Ejecutando consulta: {query} con parámetros: {parameters}")
        result = conn.execute(text(query), parameters)
        conn.commit()

    return result

""" with app.app_context():
    db.create_all() """

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/reserva')
def Reserva():
    return render_template('reserva.html')  

@app.route('/login')
def login():
    return render_template('login.html') 
@app.route('/Fiesta')
def fiesta():
    return redirect(url_for('eventos', categoria='Fiesta'))


# ---------------------- FUNCIONES PARA EVENTOS ----------------------

@app.route('/crear_evento', methods=['GET'])
def crear_evento_form():
    return render_template('crear_evento.html')

@app.route('/crear_evento', methods=['POST'])
def crear_evento():
    # Obtener los datos del formulario
    data = {
        'nombre_evento': request.form['nombre_evento'],
        'categoria': request.form['categoria'],
        'descripcion': request.form['descripcion'],
        'entradas_disponibles': request.form['entradas_disponibles'],
        'localizacion': request.form['localizacion'],
        'precio_entrada': request.form['precio_entrada']
    }

    # Validacion de datos
    required_keys = ('nombre_evento', 'categoria', 'descripcion', 'entradas_disponibles', 'localizacion', 'precio_entrada')
    for key in required_keys:
        if not data.get(key):
            flash(f'El campo {key} es obligatorio.', 'danger')
            return redirect(url_for('crear_evento_form'))

    try:
        # Insertar el evento en la base de datos
        run_query(QUERY_CREAR_EVENTO, data)
        flash('Evento creado con éxito.', 'success')
    except SQLAlchemyError as e:
        flash(f'Error al crear el evento: {e}', 'danger')

    return redirect(url_for('crear_evento_form'))

#- -- -- -- -- - -- - - -- - --- -- -- - -- --  -- -- - -- -----

if __name__ == '__main__':
    app.run(debug=True)