"""
Script ETL para procesar datos de criminalidad
Extrae, transforma y carga datos en MongoDB
"""

import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.database.mongodb_connection import MongoDBConnection
from config import RAW_DATA_DIR, PROCESSED_DATA_DIR, TIPOS_DELITOS

class CriminalityETL:
    def __init__(self):
        self.db_connection = MongoDBConnection()
        self.raw_data_path = os.path.join(RAW_DATA_DIR, 'criminalidad_municipios_2023.csv')
        self.processed_data_path = os.path.join(PROCESSED_DATA_DIR, 'criminalidad_procesada.csv')
        
    def extract_data(self):
        """Extrae datos del archivo CSV"""
        try:
            print("📥 Extrayendo datos del archivo CSV...")
            df = pd.read_csv(self.raw_data_path, encoding='utf-8')
            print(f"✅ Datos extraídos exitosamente: {len(df)} registros")
            return df
        except Exception as e:
            print(f"❌ Error al extraer datos: {e}")
            return None
    
    def transform_data(self, df):
        """Transforma y limpia los datos"""
        try:
            print("🔄 Transformando datos...")
            
            # Crear copia para transformación
            df_transformed = df.copy()
            
            # Limpiar nombres de columnas
            df_transformed.columns = df_transformed.columns.str.strip().str.lower()
            
            # Convertir tipos de datos
            numeric_columns = [
                'poblacion', 'homicidio_doloso', 'feminicidio', 'lesiones_dolosas',
                'robo_casa_habitacion', 'robo_vehiculo', 'robo_transeunte',
                'robo_negocio', 'violacion', 'secuestro', 'extorsion'
            ]
            
            for col in numeric_columns:
                df_transformed[col] = pd.to_numeric(df_transformed[col], errors='coerce')
            
            # Crear fecha
            df_transformed['fecha'] = pd.to_datetime(
                df_transformed[['año', 'mes']].assign(day=1)
            )
            
            # Calcular totales y tasas
            delitos_columns = [col for col in numeric_columns if col != 'poblacion']
            df_transformed['total_delitos'] = df_transformed[delitos_columns].sum(axis=1)
            df_transformed['tasa_delitos_100k'] = (
                df_transformed['total_delitos'] / df_transformed['poblacion'] * 100000
            ).round(2)
            
            # Calcular categorías de riesgo
            df_transformed['categoria_riesgo'] = pd.cut(
                df_transformed['tasa_delitos_100k'],
                bins=[0, 1000, 2000, 5000, float('inf')],
                labels=['Bajo', 'Medio', 'Alto', 'Muy Alto']
            )
            
            # Agregar coordenadas aproximadas (simuladas para el ejemplo)
            coordenadas = {
                'Ciudad de México': {'lat': 19.4326, 'lon': -99.1332},
                'Estado de México': {'lat': 19.3467, 'lon': -99.6350},
                'Jalisco': {'lat': 20.6597, 'lon': -103.3496},
                'Nuevo León': {'lat': 25.6866, 'lon': -100.3161},
                'Puebla': {'lat': 19.0414, 'lon': -98.2063},
                'Veracruz': {'lat': 19.1738, 'lon': -96.1342},
                'Guanajuato': {'lat': 21.0190, 'lon': -101.2574},
                'Chihuahua': {'lat': 28.6353, 'lon': -106.0889},
                'Baja California': {'lat': 32.6245, 'lon': -115.4523},
                'Sonora': {'lat': 29.0729, 'lon': -110.9559},
                'Coahuila': {'lat': 25.4232, 'lon': -101.0053},
                'Tamaulipas': {'lat': 24.2669, 'lon': -98.8363},
                'Sinaloa': {'lat': 24.8048, 'lon': -107.3943},
                'Michoacán': {'lat': 19.5665, 'lon': -101.7068},
                'Guerrero': {'lat': 17.4392, 'lon': -99.5451},
                'Oaxaca': {'lat': 17.0732, 'lon': -96.7266}
            }
            
            df_transformed['latitud'] = df_transformed['estado'].map(
                lambda x: coordenadas.get(x, {}).get('lat', 19.4326)
            )
            df_transformed['longitud'] = df_transformed['estado'].map(
                lambda x: coordenadas.get(x, {}).get('lon', -99.1332)
            )
            
            # Eliminar filas con valores nulos críticos
            df_transformed = df_transformed.dropna(subset=['poblacion', 'total_delitos'])
            
            print(f"✅ Datos transformados exitosamente: {len(df_transformed)} registros")
            return df_transformed
            
        except Exception as e:
            print(f"❌ Error al transformar datos: {e}")
            return None
    
    def load_to_mongodb(self, df):
        """Carga datos transformados a MongoDB"""
        try:
            print("📤 Cargando datos a MongoDB...")
            
            # Convertir DataFrame a diccionarios
            records = df.to_dict('records')
            
            # Convertir fechas a formato MongoDB
            for record in records:
                if 'fecha' in record:
                    record['fecha'] = record['fecha'].to_pydatetime()
            
            # Insertar en MongoDB
            collection = self.db_connection.get_collection('delitos')
            
            # Limpiar colección existente
            collection.delete_many({})
            
            # Insertar nuevos datos
            result = collection.insert_many(records)
            
            print(f"✅ Datos cargados exitosamente: {len(result.inserted_ids)} documentos")
            return True
            
        except Exception as e:
            print(f"❌ Error al cargar datos a MongoDB: {e}")
            return False
    
    def save_processed_data(self, df):
        """Guarda datos procesados en CSV"""
        try:
            # Crear directorio si no existe
            os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
            
            df.to_csv(self.processed_data_path, index=False, encoding='utf-8')
            print(f"✅ Datos procesados guardados en: {self.processed_data_path}")
            return True
        except Exception as e:
            print(f"❌ Error al guardar datos procesados: {e}")
            return False
    
    def run_etl(self):
        """Ejecuta el proceso ETL completo"""
        print("🚀 Iniciando proceso ETL...")
        print("=" * 50)
        
        # Extraer
        df_raw = self.extract_data()
        if df_raw is None:
            return False
        
        # Transformar
        df_transformed = self.transform_data(df_raw)
        if df_transformed is None:
            return False
        
        # Cargar a MongoDB
        mongodb_success = self.load_to_mongodb(df_transformed)
        
        # Guardar datos procesados
        csv_success = self.save_processed_data(df_transformed)
        
        if mongodb_success and csv_success:
            print("=" * 50)
            print("🎉 Proceso ETL completado exitosamente!")
            print(f"📊 Resumen:")
            print(f"   - Registros procesados: {len(df_transformed)}")
            print(f"   - Estados incluidos: {df_transformed['estado'].nunique()}")
            print(f"   - Municipios incluidos: {df_transformed['municipio'].nunique()}")
            print(f"   - Total de delitos: {df_transformed['total_delitos'].sum():,}")
            return True
        else:
            print("❌ El proceso ETL falló")
            return False

def main():
    """Función principal"""
    etl = CriminalityETL()
    success = etl.run_etl()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
