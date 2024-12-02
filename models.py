from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    es_admin = db.Column(db.Boolean, nullable=False)

class Evento(db.Model):
    __tablename__ = 'eventos'
    
    id_evento = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_evento = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    entradas_totales = db.Column(db.Integer, nullable=False)
    entradas_disponibles = db.Column(db.Integer, nullable=False)
    fecha_hora = db.Column(db.String(50), nullable=False)
    localizacion = db.Column(db.String(200), nullable=False)
    es_recomendacion = db.Column(db.Boolean)
    precio_entrada = db.Column(db.Integer, nullable=False)
    imagen_url = db.Column(db.String(200))

class Reserva(db.Model):
    __tablename__ = 'reservas'
    
    id_reserva = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    id_evento = db.Column(db.Integer, db.ForeignKey('eventos.id_evento'), nullable=False)
    cant_tickets = db.Column(db.Integer, nullable=False)
    
    # Relación con el modelo Usuario
    usuario = db.relationship('Usuario', backref=db.backref('reservas', lazy=True))
    # Relación con el modelo Evento
    evento = db.relationship('Evento', backref=db.backref('reservas', lazy=True))