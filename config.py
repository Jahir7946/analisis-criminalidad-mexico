"""
Configuración del proyecto de análisis de criminalidad
"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de MongoDB
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
DATABASE_NAME = 'criminalidad_mexico'
COLLECTIONS = {
    'delitos': 'delitos_municipales',
    'municipios': 'municipios_info',
    'estados': 'estados_info'
}

# Configuración de la aplicación Dash
DASH_HOST = '127.0.0.1'
DASH_PORT = 8050
DASH_DEBUG = True

# Rutas de archivos
DATA_DIR = 'data'
RAW_DATA_DIR = os.path.join(DATA_DIR, 'raw')
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, 'processed')
NOTEBOOKS_DIR = 'notebooks'
DOCS_DIR = 'docs'

# Configuración de visualización
PLOTLY_THEME = 'plotly_white'
COLOR_PALETTE = [
    '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
    '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
]

# Tipos de delitos principales
TIPOS_DELITOS = [
    'Homicidio doloso',
    'Feminicidio',
    'Lesiones dolosas',
    'Robo a casa habitación',
    'Robo de vehículo',
    'Robo a transeúnte',
    'Robo a negocio',
    'Violación',
    'Secuestro',
    'Extorsión'
]

# Estados de México
ESTADOS_MEXICO = [
    'Aguascalientes', 'Baja California', 'Baja California Sur',
    'Campeche', 'Chiapas', 'Chihuahua', 'Ciudad de México',
    'Coahuila', 'Colima', 'Durango', 'Estado de México',
    'Guanajuato', 'Guerrero', 'Hidalgo', 'Jalisco',
    'Michoacán', 'Morelos', 'Nayarit', 'Nuevo León',
    'Oaxaca', 'Puebla', 'Querétaro', 'Quintana Roo',
    'San Luis Potosí', 'Sinaloa', 'Sonora', 'Tabasco',
    'Tamaulipas', 'Tlaxcala', 'Veracruz', 'Yucatán', 'Zacatecas'
]
