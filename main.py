"""
Script principal para ejecutar el proyecto de análisis de criminalidad
"""

import sys
import os
import argparse
from datetime import datetime

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(__file__))

from src.etl.process_data import CriminalityETL
from src.database.mongodb_connection import MongoDBConnection
from src.analysis.statistical_analysis import CriminalityAnalysis

def print_banner():
    """Imprime el banner del proyecto"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║        🚨 ANÁLISIS DE CRIMINALIDAD EN MÉXICO 🚨              ║
    ║                                                              ║
    ║        Proyecto Final - Análisis de Datos                   ║
    ║        Tecnologías: MongoDB, Python, Dash, Plotly           ║
    ║        Fuente: INEGI/SNSP                                    ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def test_mongodb_connection():
    """Prueba la conexión a MongoDB"""
    print("\n🔌 Probando conexión a MongoDB...")
    db = MongoDBConnection()
    
    if db.test_connection():
        print("✅ Conexión a MongoDB exitosa")
        
        # Mostrar estadísticas
        stats = db.get_database_stats()
        if stats:
            print(f"📊 Estadísticas de la base de datos:")
            for key, value in stats.items():
                if isinstance(value, (int, float)):
                    print(f"   • {key}: {value:,}")
                else:
                    print(f"   • {key}: {value}")
        
        db.close_connection()
        return True
    else:
        print("❌ Error al conectar con MongoDB")
        print("💡 Verifica tu configuración en .env")
        db.close_connection()
        return False

def run_etl():
    """Ejecuta el proceso ETL"""
    print("\n🔄 Ejecutando proceso ETL...")
    etl = CriminalityETL()
    success = etl.run_etl()
    
    if success:
        print("✅ Proceso ETL completado exitosamente")
        return True
    else:
        print("❌ Error en el proceso ETL")
        return False

def run_analysis():
    """Ejecuta el análisis estadístico"""
    print("\n📊 Ejecutando análisis estadístico...")
    analysis = CriminalityAnalysis()
    success = analysis.run_complete_analysis()
    
    if success:
        print("✅ Análisis estadístico completado")
        return True
    else:
        print("❌ Error en el análisis estadístico")
        return False

def launch_dashboard():
    """Lanza el dashboard"""
    print("\n🚀 Lanzando dashboard...")
    print("📱 El dashboard se abrirá en: http://localhost:8050")
    print("⏹️  Presiona Ctrl+C para detener el servidor")
    
    try:
        # Importar y ejecutar la aplicación Dash
        from dashboard.app import app
        from config import DASH_HOST, DASH_PORT, DASH_DEBUG
        
        app.run_server(
            host=DASH_HOST,
            port=DASH_PORT,
            debug=DASH_DEBUG
        )
    except KeyboardInterrupt:
        print("\n⏹️  Dashboard detenido por el usuario")
    except Exception as e:
        print(f"❌ Error al lanzar dashboard: {e}")

def show_project_info():
    """Muestra información del proyecto"""
    print("\n📋 INFORMACIÓN DEL PROYECTO")
    print("=" * 50)
    print("📊 Título: Análisis de Criminalidad en México")
    print("🎯 Objetivo: Analizar patrones de criminalidad usando tecnologías NoSQL")
    print("📅 Fecha: Enero 2024")
    print("👥 Equipo: 3-4 integrantes")
    print("🔧 Tecnologías:")
    print("   • Base de datos: MongoDB Atlas")
    print("   • Procesamiento: Python, Pandas, NumPy")
    print("   • Visualización: Plotly, Dash, Matplotlib")
    print("   • Análisis: Jupyter Notebooks, Scikit-learn")
    print("📁 Estructura:")
    print("   • /data/ - Datos CSV/JSON")
    print("   • /src/ - Código fuente")
    print("   • /dashboard/ - Aplicación web")
    print("   • /notebooks/ - Análisis exploratorio")
    print("   • /docs/ - Documentación")

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description="Proyecto de Análisis de Criminalidad en México"
    )
    
    parser.add_argument(
        'command',
        choices=['info', 'test', 'etl', 'analysis', 'dashboard', 'full'],
        help='Comando a ejecutar'
    )
    
    parser.add_argument(
        '--skip-etl',
        action='store_true',
        help='Omitir proceso ETL en ejecución completa'
    )
    
    args = parser.parse_args()
    
    # Mostrar banner
    print_banner()
    print(f"⏰ Iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if args.command == 'info':
        show_project_info()
        
    elif args.command == 'test':
        test_mongodb_connection()
        
    elif args.command == 'etl':
        if test_mongodb_connection():
            run_etl()
        
    elif args.command == 'analysis':
        if test_mongodb_connection():
            run_analysis()
        
    elif args.command == 'dashboard':
        if test_mongodb_connection():
            launch_dashboard()
        
    elif args.command == 'full':
        print("\n🚀 Ejecutando proyecto completo...")
        
        # Probar conexión
        if not test_mongodb_connection():
            print("❌ No se puede continuar sin conexión a MongoDB")
            return
        
        # Ejecutar ETL (opcional)
        if not args.skip_etl:
            if not run_etl():
                print("⚠️  Continuando sin ETL...")
        
        # Ejecutar análisis
        run_analysis()
        
        # Lanzar dashboard
        print("\n" + "="*60)
        print("🎉 ¡Proyecto ejecutado exitosamente!")
        print("📱 Abriendo dashboard...")
        launch_dashboard()

def show_help():
    """Muestra ayuda de uso"""
    help_text = """
    🚨 ANÁLISIS DE CRIMINALIDAD EN MÉXICO 🚨
    
    Uso: python main.py <comando> [opciones]
    
    Comandos disponibles:
    
    info        - Muestra información del proyecto
    test        - Prueba la conexión a MongoDB
    etl         - Ejecuta solo el proceso ETL
    analysis    - Ejecuta solo el análisis estadístico
    dashboard   - Lanza solo el dashboard
    full        - Ejecuta el proyecto completo
    
    Opciones:
    
    --skip-etl  - Omite el proceso ETL en ejecución completa
    
    Ejemplos:
    
    python main.py info                    # Ver información
    python main.py test                    # Probar conexión
    python main.py etl                     # Solo ETL
    python main.py dashboard               # Solo dashboard
    python main.py full                    # Proyecto completo
    python main.py full --skip-etl         # Completo sin ETL
    
    Para más información, consulta la documentación en /docs/
    """
    print(help_text)

if __name__ == "__main__":
    try:
        if len(sys.argv) == 1:
            show_help()
        else:
            main()
    except KeyboardInterrupt:
        print("\n⏹️  Programa interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        print("💡 Consulta la documentación en /docs/ para más ayuda")
