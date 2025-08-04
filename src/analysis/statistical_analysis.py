"""
Análisis estadístico de datos de criminalidad
"""

import pandas as pd
import numpy as np
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.database.mongodb_connection import CriminalityQueries
from config import TIPOS_DELITOS, COLOR_PALETTE

class CriminalityAnalysis:
    def __init__(self):
        self.queries = CriminalityQueries()
        self.data = None
        self.load_data()
    
    def load_data(self):
        """Carga datos desde MongoDB"""
        try:
            print("📊 Cargando datos para análisis...")
            collection = self.queries.collection
            if collection is not None:
                cursor = collection.find({})
                self.data = pd.DataFrame(list(cursor))
                print(f"✅ Datos cargados: {len(self.data)} registros")
            else:
                print("❌ No se pudo conectar a la base de datos")
        except Exception as e:
            print(f"❌ Error al cargar datos: {e}")
    
    def descriptive_statistics(self):
        """Calcula estadísticas descriptivas"""
        if self.data is None or self.data.empty:
            print("❌ No hay datos disponibles para análisis")
            return None
        
        try:
            print("\n📈 ESTADÍSTICAS DESCRIPTIVAS")
            print("=" * 50)
            
            # Columnas numéricas de delitos
            delitos_cols = [
                'homicidio_doloso', 'feminicidio', 'lesiones_dolosas',
                'robo_casa_habitacion', 'robo_vehiculo', 'robo_transeunte',
                'robo_negocio', 'violacion', 'secuestro', 'extorsion'
            ]
            
            stats_dict = {}
            
            for col in delitos_cols:
                if col in self.data.columns:
                    stats_dict[col] = {
                        'total': self.data[col].sum(),
                        'promedio': self.data[col].mean(),
                        'mediana': self.data[col].median(),
                        'desv_std': self.data[col].std(),
                        'min': self.data[col].min(),
                        'max': self.data[col].max()
                    }
            
            # Mostrar estadísticas
            for delito, stats in stats_dict.items():
                print(f"\n🔸 {delito.replace('_', ' ').title()}:")
                print(f"   Total: {stats['total']:,}")
                print(f"   Promedio: {stats['promedio']:.2f}")
                print(f"   Mediana: {stats['mediana']:.2f}")
                print(f"   Desv. Estándar: {stats['desv_std']:.2f}")
                print(f"   Rango: {stats['min']} - {stats['max']}")
            
            return stats_dict
            
        except Exception as e:
            print(f"❌ Error en análisis descriptivo: {e}")
            return None
    
    def correlation_analysis(self):
        """Análisis de correlaciones entre tipos de delitos"""
        if self.data is None or self.data.empty:
            return None
        
        try:
            print("\n🔗 ANÁLISIS DE CORRELACIONES")
            print("=" * 50)
            
            # Seleccionar columnas numéricas de delitos
            delitos_cols = [
                'homicidio_doloso', 'feminicidio', 'lesiones_dolosas',
                'robo_casa_habitacion', 'robo_vehiculo', 'robo_transeunte',
                'robo_negocio', 'violacion', 'secuestro', 'extorsion'
            ]
            
            # Filtrar columnas que existen en los datos
            available_cols = [col for col in delitos_cols if col in self.data.columns]
            
            if len(available_cols) < 2:
                print("❌ No hay suficientes columnas para análisis de correlación")
                return None
            
            # Calcular matriz de correlación
            correlation_matrix = self.data[available_cols].corr()
            
            # Encontrar correlaciones más altas
            correlations = []
            for i in range(len(available_cols)):
                for j in range(i+1, len(available_cols)):
                    corr_value = correlation_matrix.iloc[i, j]
                    correlations.append({
                        'delito1': available_cols[i],
                        'delito2': available_cols[j],
                        'correlacion': corr_value
                    })
            
            # Ordenar por correlación absoluta
            correlations.sort(key=lambda x: abs(x['correlacion']), reverse=True)
            
            print("🔝 Top 10 correlaciones más fuertes:")
            for i, corr in enumerate(correlations[:10]):
                print(f"{i+1:2d}. {corr['delito1']} ↔ {corr['delito2']}: {corr['correlacion']:.3f}")
            
            return correlation_matrix
            
        except Exception as e:
            print(f"❌ Error en análisis de correlación: {e}")
            return None
    
    def geographic_analysis(self):
        """Análisis geográfico por estados"""
        if self.data is None or self.data.empty:
            return None
        
        try:
            print("\n🗺️ ANÁLISIS GEOGRÁFICO")
            print("=" * 50)
            
            # Agrupar por estado
            estado_stats = self.data.groupby('estado').agg({
                'total_delitos': 'sum',
                'poblacion': 'sum',
                'tasa_delitos_100k': 'mean',
                'municipio': 'count'
            }).round(2)
            
            estado_stats.columns = ['Total_Delitos', 'Poblacion_Total', 'Tasa_Promedio', 'Num_Municipios']
            
            # Calcular tasa real por estado
            estado_stats['Tasa_Real'] = (
                estado_stats['Total_Delitos'] / estado_stats['Poblacion_Total'] * 100000
            ).round(2)
            
            # Ordenar por tasa de delitos
            estado_stats = estado_stats.sort_values('Tasa_Real', ascending=False)
            
            print("🏆 Estados con mayor tasa de delitos (por 100k habitantes):")
            for i, (estado, row) in enumerate(estado_stats.head(10).iterrows()):
                print(f"{i+1:2d}. {estado}: {row['Tasa_Real']:.2f} delitos/100k hab")
            
            print("\n🏅 Estados con menor tasa de delitos (por 100k habitantes):")
            for i, (estado, row) in enumerate(estado_stats.tail(5).iterrows()):
                print(f"{i+1:2d}. {estado}: {row['Tasa_Real']:.2f} delitos/100k hab")
            
            return estado_stats
            
        except Exception as e:
            print(f"❌ Error en análisis geográfico: {e}")
            return None
    
    def clustering_analysis(self):
        """Análisis de clustering de municipios"""
        if self.data is None or self.data.empty:
            return None
        
        try:
            print("\n🎯 ANÁLISIS DE CLUSTERING")
            print("=" * 50)
            
            # Seleccionar características para clustering
            features = [
                'homicidio_doloso', 'feminicidio', 'lesiones_dolosas',
                'robo_casa_habitacion', 'robo_vehiculo', 'robo_transeunte',
                'robo_negocio', 'violacion', 'secuestro', 'extorsion'
            ]
            
            # Filtrar características disponibles
            available_features = [f for f in features if f in self.data.columns]
            
            if len(available_features) < 3:
                print("❌ No hay suficientes características para clustering")
                return None
            
            # Preparar datos
            X = self.data[available_features].fillna(0)
            
            # Normalizar datos
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Aplicar K-means
            n_clusters = 4
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            clusters = kmeans.fit_predict(X_scaled)
            
            # Agregar clusters a los datos
            self.data['cluster'] = clusters
            
            # Analizar clusters
            print(f"📊 Municipios agrupados en {n_clusters} clusters:")
            
            for i in range(n_clusters):
                cluster_data = self.data[self.data['cluster'] == i]
                print(f"\n🔸 Cluster {i+1} ({len(cluster_data)} municipios):")
                print(f"   Tasa promedio: {cluster_data['tasa_delitos_100k'].mean():.2f}")
                print(f"   Estados principales: {', '.join(cluster_data['estado'].value_counts().head(3).index.tolist())}")
                
                # Municipios ejemplo
                ejemplos = cluster_data.nlargest(3, 'tasa_delitos_100k')[['municipio', 'estado', 'tasa_delitos_100k']]
                print("   Ejemplos:")
                for _, row in ejemplos.iterrows():
                    print(f"     - {row['municipio']}, {row['estado']}: {row['tasa_delitos_100k']:.2f}")
            
            return clusters
            
        except Exception as e:
            print(f"❌ Error en análisis de clustering: {e}")
            return None
    
    def risk_assessment(self):
        """Evaluación de riesgo por municipio"""
        if self.data is None or self.data.empty:
            return None
        
        try:
            print("\n⚠️ EVALUACIÓN DE RIESGO")
            print("=" * 50)
            
            # Contar municipios por categoría de riesgo
            if 'categoria_riesgo' in self.data.columns:
                risk_counts = self.data['categoria_riesgo'].value_counts()
                
                print("📊 Distribución de municipios por nivel de riesgo:")
                for categoria, count in risk_counts.items():
                    percentage = (count / len(self.data)) * 100
                    print(f"   {categoria}: {count} municipios ({percentage:.1f}%)")
                
                # Municipios de muy alto riesgo
                high_risk = self.data[self.data['categoria_riesgo'] == 'Muy Alto'].nlargest(10, 'tasa_delitos_100k')
                
                print("\n🚨 Top 10 municipios de MUY ALTO riesgo:")
                for i, (_, row) in enumerate(high_risk.iterrows()):
                    print(f"{i+1:2d}. {row['municipio']}, {row['estado']}: {row['tasa_delitos_100k']:.2f} delitos/100k hab")
                
                return risk_counts
            else:
                print("❌ No se encontró información de categorías de riesgo")
                return None
                
        except Exception as e:
            print(f"❌ Error en evaluación de riesgo: {e}")
            return None
    
    def generate_insights(self):
        """Genera insights y conclusiones del análisis"""
        if self.data is None or self.data.empty:
            return None
        
        try:
            print("\n💡 INSIGHTS Y CONCLUSIONES")
            print("=" * 50)
            
            # Insight 1: Delito más común
            delitos_cols = [
                'homicidio_doloso', 'feminicidio', 'lesiones_dolosas',
                'robo_casa_habitacion', 'robo_vehiculo', 'robo_transeunte',
                'robo_negocio', 'violacion', 'secuestro', 'extorsion'
            ]
            
            available_cols = [col for col in delitos_cols if col in self.data.columns]
            delitos_totales = {col: self.data[col].sum() for col in available_cols}
            delito_mas_comun = max(delitos_totales, key=delitos_totales.get)
            
            print(f"🔸 Delito más común: {delito_mas_comun.replace('_', ' ').title()}")
            print(f"   Total de casos: {delitos_totales[delito_mas_comun]:,}")
            
            # Insight 2: Estado más afectado
            estado_mas_afectado = self.data.groupby('estado')['total_delitos'].sum().idxmax()
            total_estado = self.data.groupby('estado')['total_delitos'].sum().max()
            
            print(f"\n🔸 Estado más afectado: {estado_mas_afectado}")
            print(f"   Total de delitos: {total_estado:,}")
            
            # Insight 3: Correlación población-delitos
            if 'poblacion' in self.data.columns and 'total_delitos' in self.data.columns:
                corr_pob_delitos = self.data['poblacion'].corr(self.data['total_delitos'])
                print(f"\n🔸 Correlación población-delitos: {corr_pob_delitos:.3f}")
                
                if corr_pob_delitos > 0.7:
                    print("   Interpretación: Fuerte correlación positiva")
                elif corr_pob_delitos > 0.3:
                    print("   Interpretación: Correlación moderada")
                else:
                    print("   Interpretación: Correlación débil")
            
            # Insight 4: Variabilidad entre municipios
            if 'tasa_delitos_100k' in self.data.columns:
                cv = self.data['tasa_delitos_100k'].std() / self.data['tasa_delitos_100k'].mean()
                print(f"\n🔸 Coeficiente de variación en tasas: {cv:.3f}")
                
                if cv > 1:
                    print("   Interpretación: Alta variabilidad entre municipios")
                elif cv > 0.5:
                    print("   Interpretación: Variabilidad moderada")
                else:
                    print("   Interpretación: Baja variabilidad")
            
            return True
            
        except Exception as e:
            print(f"❌ Error generando insights: {e}")
            return None
    
    def run_complete_analysis(self):
        """Ejecuta análisis completo"""
        print("🔍 ANÁLISIS ESTADÍSTICO COMPLETO DE CRIMINALIDAD")
        print("=" * 60)
        
        if self.data is None or self.data.empty:
            print("❌ No hay datos disponibles para análisis")
            return False
        
        try:
            # Ejecutar todos los análisis
            self.descriptive_statistics()
            self.correlation_analysis()
            self.geographic_analysis()
            self.clustering_analysis()
            self.risk_assessment()
            self.generate_insights()
            
            print("\n" + "=" * 60)
            print("✅ Análisis estadístico completado exitosamente")
            return True
            
        except Exception as e:
            print(f"❌ Error en análisis completo: {e}")
            return False

def main():
    """Función principal"""
    analysis = CriminalityAnalysis()
    analysis.run_complete_analysis()

if __name__ == "__main__":
    main()
