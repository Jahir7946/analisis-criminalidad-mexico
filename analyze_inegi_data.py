"""
Script para analizar el archivo de datos del INEGI
"""
import pandas as pd
import chardet

def analyze_inegi_file():
    file_path = 'data/raw/Indicadores20250803233401.csv'
    
    # Detectar encoding
    with open(file_path, 'rb') as f:
        raw_data = f.read()
        encoding = chardet.detect(raw_data)
        print(f"Encoding detectado: {encoding}")
    
    # Intentar leer con diferentes configuraciones
    encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    
    for enc in encodings:
        try:
            print(f"\n--- Probando encoding: {enc} ---")
            
            # Leer primeras líneas para ver estructura
            with open(file_path, 'r', encoding=enc) as f:
                lines = [f.readline().strip() for _ in range(10)]
                for i, line in enumerate(lines):
                    print(f"Línea {i+1}: {line[:100]}...")
            
            # Intentar leer como CSV
            df = pd.read_csv(file_path, encoding=enc, nrows=5)
            print(f"✅ Éxito con {enc}")
            print(f"Shape: {df.shape}")
            print(f"Columnas: {df.columns.tolist()}")
            print("Primeras filas:")
            print(df.head())
            break
            
        except Exception as e:
            print(f"❌ Error con {enc}: {str(e)[:100]}...")
            continue

if __name__ == "__main__":
    analyze_inegi_file()
