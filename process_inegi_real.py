"""
Script para procesar el archivo real del INEGI
"""
import pandas as pd
import re

def process_inegi_file():
    file_path = 'data/raw/Indicadores20250803233401.csv'
    
    print("🔍 Analizando archivo del INEGI...")
    
    # Leer todas las líneas
    with open(file_path, 'r', encoding='latin-1') as f:
        lines = f.readlines()
    
    print(f"📄 Total de líneas: {len(lines)}")
    
    # Buscar donde empiezan los datos reales
    data_start = None
    for i, line in enumerate(lines):
        # Buscar línea que contenga columnas de datos
        if 'Periodos' in line or any(keyword in line.lower() for keyword in ['año', 'entidad', 'municipio', 'delito']):
            data_start = i
            print(f"📊 Datos encontrados en línea {i+1}: {line.strip()[:100]}...")
            break
    
    if data_start is None:
        print("❌ No se encontraron datos estructurados")
        return None
    
    # Intentar leer desde donde empiezan los datos
    try:
        # Leer desde la línea de datos
        df = pd.read_csv(file_path, encoding='latin-1', skiprows=data_start)
        print(f"✅ Datos cargados exitosamente")
        print(f"📏 Shape: {df.shape}")
        print(f"📋 Columnas: {df.columns.tolist()}")
        
        # Mostrar primeras filas
        print("\n🔍 Primeras 5 filas:")
        print(df.head())
        
        # Mostrar información de columnas
        print("\n📊 Información de columnas:")
        print(df.info())
        
        # Buscar columnas relacionadas con criminalidad
        crime_columns = []
        for col in df.columns:
            if any(keyword in str(col).lower() for keyword in ['delito', 'crimen', 'homicidio', 'robo', 'violencia']):
                crime_columns.append(col)
        
        if crime_columns:
            print(f"\n🚨 Columnas de criminalidad encontradas: {crime_columns}")
        
        return df
        
    except Exception as e:
        print(f"❌ Error procesando datos: {e}")
        return None

def save_processed_data(df):
    """Guardar datos procesados"""
    if df is not None:
        output_path = 'data/raw/inegi_processed.csv'
        df.to_csv(output_path, index=False, encoding='utf-8')
        print(f"💾 Datos guardados en: {output_path}")

if __name__ == "__main__":
    df = process_inegi_file()
    if df is not None:
        save_processed_data(df)
