"""
Procesador para el archivo incidencias.xlsx - Datos de criminalidad por estado
Estructura simplificada: Estado, Número de Delitos, Porcentaje de Incidencia
"""

import pandas as pd
import pymongo
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def connect_to_mongodb():
    """Conecta a MongoDB Atlas"""
    try:
        MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb+srv://23202001:23202001@cluster0.vgypvgq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
        DATABASE_NAME = os.getenv('DATABASE_NAME', 'criminalidad_mexico')
        
        client = MongoClient(MONGODB_URI)
        db = client[DATABASE_NAME]
        
        # Verificar conexión
        client.admin.command('ping')
        print("✅ Conexión exitosa a MongoDB Atlas")
        return db
    except Exception as e:
        print(f"❌ Error conectando a MongoDB: {e}")
        return None

def process_incidencias():
    """Procesa el archivo incidencias.xlsx con estructura simplificada"""
    
    print("🚨 Procesando archivo incidencias.xlsx...")
    
    file_path = 'data/raw/incidencias.xlsx'
    
    try:
        # Leer el archivo Excel
        df = pd.read_excel(file_path)
        print(f"✅ Archivo leído exitosamente: {df.shape[0]} registros, {df.shape[1]} columnas")
        
        # Mostrar información del dataset
        print("\n📊 Información del dataset:")
        print(f"Columnas: {df.columns.tolist()}")
        print(f"Estados: {df.shape[0]}")
        print(f"Total de delitos: {df['Número de Delitos'].sum():,}")
        
        # Limpiar y preparar datos
        df_clean = df.copy()
        df_clean['Estado'] = df_clean['Estado'].str.strip()
        df_clean['Año'] = 2025  # Datos de Junio 2025
        df_clean['Mes'] = 'Junio'
        df_clean['Periodo'] = 'Junio 2025'
        
        # Crear datos adicionales para el análisis
        df_clean['Ranking'] = df_clean['Número de Delitos'].rank(method='dense', ascending=False).astype(int)
        df_clean['Categoria_Riesgo'] = pd.cut(
            df_clean['Porcentaje de Incidencia'], 
            bins=[0, 0.02, 0.05, 0.10, 1.0], 
            labels=['Bajo', 'Medio', 'Alto', 'Muy Alto']
        )
        
        # Guardar CSV procesado
        csv_path = 'data/raw/criminalidad_estados_junio_2025.csv'
        df_clean.to_csv(csv_path, index=False, encoding='utf-8')
        print(f"✅ Datos guardados en: {csv_path}")
        
        # Conectar a MongoDB y guardar datos
        db = connect_to_mongodb()
        if db is not None:
            save_to_mongodb(db, df_clean)
        
        # Mostrar estadísticas
        print("\n📈 Estadísticas principales:")
        print(f"Estado con más delitos: {df_clean.loc[df_clean['Número de Delitos'].idxmax(), 'Estado']} ({df_clean['Número de Delitos'].max():,} delitos)")
        print(f"Estado con menos delitos: {df_clean.loc[df_clean['Número de Delitos'].idxmin(), 'Estado']} ({df_clean['Número de Delitos'].min():,} delitos)")
        print(f"Promedio de delitos por estado: {df_clean['Número de Delitos'].mean():.0f}")
        print(f"Porcentaje promedio de incidencia: {df_clean['Porcentaje de Incidencia'].mean():.4f}")
        
        print("\n🎉 ¡Datos de incidencias.xlsx procesados exitosamente!")
        print("🚀 Proyecto actualizado con datos simplificados por estado")
        
        return df_clean
        
    except Exception as e:
        print(f"❌ Error procesando el archivo: {e}")
        return None

def save_to_mongodb(db, df):
    """Guarda los datos en MongoDB Atlas"""
    try:
        # Limpiar colección existente
        collection = db['criminalidad_estados']
        collection.delete_many({})
        
        # Convertir DataFrame a diccionarios
        records = df.to_dict('records')
        
        # Insertar datos
        result = collection.insert_many(records)
        print(f"✅ {len(result.inserted_ids)} registros guardados en MongoDB")
        
        # Crear índices para optimizar consultas
        collection.create_index("Estado")
        collection.create_index("Número de Delitos")
        collection.create_index("Ranking")
        
        print("✅ Índices creados en MongoDB")
        
    except Exception as e:
        print(f"❌ Error guardando en MongoDB: {e}")

if __name__ == "__main__":
    df_result = process_incidencias()
    if df_result is not None:
        print(f"\n✅ Procesamiento completado. {len(df_result)} registros procesados.")
    else:
        print("\n❌ Error en el procesamiento.")
