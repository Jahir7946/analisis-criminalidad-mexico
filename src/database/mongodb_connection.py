"""
Conexión y operaciones con MongoDB
"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from config import MONGODB_URI, DATABASE_NAME, COLLECTIONS

class MongoDBConnection:
    def __init__(self):
        self.client = None
        self.database = None
        self.connect()
    
    def connect(self):
        """Establece conexión con MongoDB"""
        try:
            print("🔌 Conectando a MongoDB...")
            self.client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
            
            # Verificar conexión
            self.client.admin.command('ping')
            
            self.database = self.client[DATABASE_NAME]
            print("✅ Conexión a MongoDB establecida exitosamente")
            
        except ConnectionFailure:
            print("❌ Error: No se pudo conectar a MongoDB")
            print("💡 Verifica tu string de conexión y conectividad a internet")
            self.client = None
            self.database = None
            
        except ServerSelectionTimeoutError:
            print("❌ Error: Timeout al conectar con MongoDB")
            print("💡 Verifica que MongoDB esté ejecutándose")
            self.client = None
            self.database = None
            
        except Exception as e:
            print(f"❌ Error inesperado al conectar: {e}")
            self.client = None
            self.database = None
    
    def get_collection(self, collection_name):
        """Obtiene una colección específica"""
        if self.database is None:
            print("❌ No hay conexión a la base de datos")
            return None
        
        # Usar nombre de colección del config si existe
        actual_name = COLLECTIONS.get(collection_name, collection_name)
        return self.database[actual_name]
    
    def create_indexes(self):
        """Crea índices para optimizar consultas"""
        try:
            print("📊 Creando índices...")
            
            delitos_collection = self.get_collection('delitos')
            if delitos_collection is not None:
                # Índices para consultas comunes
                delitos_collection.create_index("estado")
                delitos_collection.create_index("municipio")
                delitos_collection.create_index("fecha")
                delitos_collection.create_index([("estado", 1), ("municipio", 1)])
                delitos_collection.create_index([("latitud", 1), ("longitud", 1)])
                delitos_collection.create_index("tasa_delitos_100k")
                
                print("✅ Índices creados exitosamente")
            
        except Exception as e:
            print(f"❌ Error al crear índices: {e}")
    
    def get_database_stats(self):
        """Obtiene estadísticas de la base de datos"""
        if self.database is None:
            return None
        
        try:
            stats = {}
            
            # Estadísticas generales
            db_stats = self.database.command("dbStats")
            stats['database_size'] = db_stats.get('dataSize', 0)
            stats['collections_count'] = len(self.database.list_collection_names())
            
            # Estadísticas por colección
            for collection_name in COLLECTIONS.values():
                if collection_name in self.database.list_collection_names():
                    collection = self.database[collection_name]
                    stats[collection_name] = collection.count_documents({})
            
            return stats
            
        except Exception as e:
            print(f"❌ Error al obtener estadísticas: {e}")
            return None
    
    def test_connection(self):
        """Prueba la conexión y operaciones básicas"""
        if self.client is None:
            return False
        
        try:
            # Ping al servidor
            self.client.admin.command('ping')
            
            # Probar operación de escritura/lectura
            test_collection = self.database['test']
            test_doc = {'test': True, 'timestamp': '2023-01-01'}
            
            # Insertar documento de prueba
            result = test_collection.insert_one(test_doc)
            
            # Leer documento de prueba
            found_doc = test_collection.find_one({'_id': result.inserted_id})
            
            # Eliminar documento de prueba
            test_collection.delete_one({'_id': result.inserted_id})
            
            if found_doc:
                print("✅ Prueba de conexión exitosa")
                return True
            else:
                print("❌ Prueba de conexión falló")
                return False
                
        except Exception as e:
            print(f"❌ Error en prueba de conexión: {e}")
            return False
    
    def close_connection(self):
        """Cierra la conexión a MongoDB"""
        if self.client:
            self.client.close()
            print("🔌 Conexión a MongoDB cerrada")

class CriminalityQueries:
    """Clase para consultas específicas de criminalidad"""
    
    def __init__(self):
        self.db_connection = MongoDBConnection()
        self.collection = self.db_connection.get_collection('delitos')
    
    def get_delitos_by_estado(self, estado):
        """Obtiene delitos por estado"""
        if self.collection is None:
            return []
        
        try:
            cursor = self.collection.find({'estado': estado})
            return list(cursor)
        except Exception as e:
            print(f"❌ Error al consultar delitos por estado: {e}")
            return []
    
    def get_top_municipios_peligrosos(self, limit=10):
        """Obtiene los municipios más peligrosos"""
        if self.collection is None:
            return []
        
        try:
            pipeline = [
                {'$sort': {'tasa_delitos_100k': -1}},
                {'$limit': limit},
                {'$project': {
                    'estado': 1,
                    'municipio': 1,
                    'tasa_delitos_100k': 1,
                    'total_delitos': 1,
                    'poblacion': 1
                }}
            ]
            
            cursor = self.collection.aggregate(pipeline)
            return list(cursor)
            
        except Exception as e:
            print(f"❌ Error al consultar municipios peligrosos: {e}")
            return []
    
    def get_delitos_by_tipo(self):
        """Obtiene estadísticas por tipo de delito"""
        if self.collection is None:
            return {}
        
        try:
            pipeline = [
                {'$group': {
                    '_id': None,
                    'homicidio_doloso': {'$sum': '$homicidio_doloso'},
                    'feminicidio': {'$sum': '$feminicidio'},
                    'lesiones_dolosas': {'$sum': '$lesiones_dolosas'},
                    'robo_casa_habitacion': {'$sum': '$robo_casa_habitacion'},
                    'robo_vehiculo': {'$sum': '$robo_vehiculo'},
                    'robo_transeunte': {'$sum': '$robo_transeunte'},
                    'robo_negocio': {'$sum': '$robo_negocio'},
                    'violacion': {'$sum': '$violacion'},
                    'secuestro': {'$sum': '$secuestro'},
                    'extorsion': {'$sum': '$extorsion'}
                }}
            ]
            
            result = list(self.collection.aggregate(pipeline))
            return result[0] if result else {}
            
        except Exception as e:
            print(f"❌ Error al consultar delitos por tipo: {e}")
            return {}
    
    def get_estados_stats(self):
        """Obtiene estadísticas por estado"""
        if self.collection is None:
            return []
        
        try:
            pipeline = [
                {'$group': {
                    '_id': '$estado',
                    'total_delitos': {'$sum': '$total_delitos'},
                    'poblacion_total': {'$sum': '$poblacion'},
                    'municipios_count': {'$sum': 1},
                    'tasa_promedio': {'$avg': '$tasa_delitos_100k'}
                }},
                {'$sort': {'total_delitos': -1}}
            ]
            
            cursor = self.collection.aggregate(pipeline)
            return list(cursor)
            
        except Exception as e:
            print(f"❌ Error al consultar estadísticas por estado: {e}")
            return []

def main():
    """Función de prueba"""
    print("🧪 Probando conexión a MongoDB...")
    
    # Probar conexión básica
    db = MongoDBConnection()
    if db.test_connection():
        print("✅ Conexión exitosa")
        
        # Crear índices
        db.create_indexes()
        
        # Mostrar estadísticas
        stats = db.get_database_stats()
        if stats:
            print(f"📊 Estadísticas de la base de datos:")
            for key, value in stats.items():
                print(f"   {key}: {value}")
    
    # Cerrar conexión
    db.close_connection()

if __name__ == "__main__":
    main()
