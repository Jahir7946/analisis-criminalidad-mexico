"""
Script ETL actualizado para procesar datos de criminalidad del INEGI
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
from config import RAW_DATA_DIR, PROCESSED_DATA_DIR

class CriminalityETLUpdated:
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
            print(f"📋 Columnas disponibles: {df.columns.tolist()}")
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
            
            # Renombrar columnas para consistencia
            column_mapping = {
                'delitos_totales': 'total_delitos',
                'tasa_criminalidad': 'tasa_delitos_100k'
            }
            df_transformed = df_transformed.rename(columns=column_mapping)
            
            # Convertir tipos de datos
            numeric_columns = ['poblacion', 'total_delitos', 'tasa_delitos_100k']
            for col in numeric_columns:
                if col in df_transformed.columns:
                    df_transformed[col] = pd.to_numeric(df_transformed[col], errors='coerce')
            
            # Crear fecha actual
            df_transformed['fecha'] = datetime.now()
            df_transformed['mes'] = datetime.now().month
            
            # Crear categorías de riesgo basadas en tasa de criminalidad
            if 'tasa_delitos_100k' in df_transformed.columns:
                df_transformed['categoria_riesgo'] = pd.cut(
                    df_transformed['tasa_delitos_100k'],
                    bins=[0, 10000, 20000, 30000, float('inf')],
                    labels=['Bajo', 'Medio', 'Alto', 'Muy Alto']
                )
            
            # Crear delitos específicos basados en la tasa total (simulados)
            np.random.seed(42)  # Para reproducibilidad
            if 'tasa_delitos_100k' in df_transformed.columns:
                df_transformed['homicidio_doloso'] = (df_transformed['tasa_delitos_100k'] * np.random.uniform(0.02, 0.05, len(df_transformed))).round(2)
                df_transformed['feminicidio'] = (df_transformed['tasa_delitos_100k'] * np.random.uniform(0.001, 0.003, len(df_transformed))).round(2)
                df_transformed['lesiones_dolosas'] = (df_transformed['tasa_delitos_100k'] * np.random.uniform(0.20, 0.30, len(df_transformed))).round(2)
                df_transformed['robo_casa_habitacion'] = (df_transformed['tasa_delitos_100k'] * np.random.uniform(0.10, 0.20, len(df_transformed))).round(2)
                df_transformed['robo_vehiculo'] = (df_transformed['tasa_delitos_100k'] * np.random.uniform(0.15, 0.25, len(df_transformed))).round(2)
                df_transformed['robo_transeunte'] = (df_transformed['tasa_delitos_100k'] * np.random.uniform(0.25, 0.35, len(df_transformed))).round(2)
                df_transformed['robo_negocio'] = (df_transformed['tasa_delitos_100k'] * np.random.uniform(0.08, 0.15, len(df_transformed))).round(2)
                df_transformed['violacion'] = (df_transformed['tasa_delitos_100k'] * np.random.uniform(0.03, 0.08, len(df_transformed))).round(2)
                df_transformed['secuestro'] = (df_transformed['tasa_delitos_100k'] * np.random.uniform(0.001, 0.005, len(df_transformed))).round(2)
                df_transformed['extorsion'] = (df_transformed['tasa_delitos_100k'] * np.random.uniform(0.05, 0.12, len(df_transformed))).round(2)
            
            # Agregar coordenadas aproximadas por estado
            coordenadas = {
                'baja california': {'lat': 32.6245, 'lon': -115.4523},
                'estado de méxico': {'lat': 19.3467, 'lon': -99.6350},
                'jalisco': {'lat': 20.6597, 'lon': -103.3496},
                'puebla': {'lat': 19.0414, 'lon': -98.2063},
                'chihuahua': {'lat': 28.6353, 'lon': -106.0889},
                'guanajuato': {'lat': 21.0190, 'lon': -101.2574},
                'nuevo león': {'lat': 25.6866, 'lon': -100.3161},
                'ciudad de méxico': {'lat': 19.4326, 'lon': -99.1332},
                'yucatán': {'lat': 20.7099, 'lon': -89.0943},
                'san luis potosí': {'lat': 22.1565, 'lon': -100.9855},
                'guerrero': {'lat': 17.4392, 'lon': -99.5451},
                'quintana roo': {'lat': 19.1817, 'lon': -88.4791},
                'morelos': {'lat': 18.6813, 'lon': -99.1013}
            }
            
            df_transformed['estado_lower'] = df_transformed['estado'].str.lower()
            df_transformed['latitud'] = df_transformed['estado_lower'].map(
                lambda x: coordenadas.get(x, {}).get('lat', 19.4326)
            )
            df_transformed['longitud'] = df_transformed['estado_lower'].map(
                lambda x: coordenadas.get(x, {}).get('lon', -99.1332)
            )
            
            # Eliminar columna temporal
            df_transformed = df_transformed.drop('estado_lower', axis=1)
            
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
                if 'fecha' in record and hasattr(record['fecha'], 'to_pydatetime'):
                    record['fecha'] = record['fecha'].to_pydatetime()
                elif 'fecha' in record and isinstance(record['fecha'], datetime):
                    record['fecha'] = record['fecha']
            
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
        print("🚀 Iniciando proceso ETL actualizado...")
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
            if 'total_delitos' in df_transformed.columns:
                print(f"   - Total de delitos: {df_transformed['total_delitos'].sum():,}")
            return True
        else:
            print("❌ El proceso ETL falló")
            return False

def main():
    """Función principal"""
    etl = CriminalityETLUpdated()
    success = etl.run_etl()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
