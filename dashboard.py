"""
Dashboard funcional de criminalidad en México
"""

import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
from pymongo import MongoClient

# Configuración
MONGODB_URI = "mongodb+srv://23202001:23202001@cluster0.vgypvgq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DATABASE_NAME = 'criminalidad_mexico'
COLLECTION_NAME = 'delitos_municipales'

def get_data():
    """Obtiene datos de MongoDB"""
    try:
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]
        
        data = list(collection.find())
        df = pd.DataFrame(data)
        
        client.close()
        return df
    except Exception as e:
        print(f"Error obteniendo datos: {e}")
        return pd.DataFrame()

def create_top_municipios_chart(df):
    """Crea gráfico de top municipios"""
    if len(df) == 0:
        return {}
    
    top_10 = df.nlargest(10, 'tasa_delitos_100k')
    
    fig = px.bar(
        top_10,
        x='municipio',
        y='tasa_delitos_100k',
        color='categoria_riesgo',
        title='Top 10 Municipios con Mayor Tasa de Criminalidad',
        labels={'tasa_delitos_100k': 'Tasa por 100k hab', 'municipio': 'Municipio'},
        color_discrete_map={
            'Bajo': '#2ecc71',
            'Medio': '#f39c12',
            'Alto': '#e74c3c',
            'Muy Alto': '#8e44ad'
        }
    )
    
    fig.update_layout(
        xaxis_tickangle=45,
        height=500,
        showlegend=True
    )
    
    return fig

def create_risk_distribution_chart(df):
    """Crea gráfico de distribución por riesgo"""
    if len(df) == 0:
        return {}
    
    risk_counts = df['categoria_riesgo'].value_counts()
    
    fig = px.pie(
        values=risk_counts.values,
        names=risk_counts.index,
        title='Distribución de Municipios por Nivel de Riesgo',
        color_discrete_map={
            'Bajo': '#2ecc71',
            'Medio': '#f39c12',
            'Alto': '#e74c3c',
            'Muy Alto': '#8e44ad'
        }
    )
    
    fig.update_layout(height=400)
    
    return fig

def create_scatter_chart(df):
    """Crea gráfico de dispersión"""
    if len(df) == 0:
        return {}
    
    fig = px.scatter(
        df,
        x='poblacion',
        y='total_delitos',
        color='estado',
        size='tasa_delitos_100k',
        hover_data=['municipio'],
        title='Relación entre Población y Total de Delitos',
        labels={'poblacion': 'Población', 'total_delitos': 'Total de Delitos'}
    )
    
    fig.update_layout(height=500)
    
    return fig

# Cargar datos
print("🔌 Conectando a MongoDB...")
df = get_data()
print(f"📊 Datos cargados: {len(df)} registros")

# Crear aplicación Dash
app = dash.Dash(__name__)

# Layout del dashboard
app.layout = html.Div([
    html.H1("🚨 Dashboard de Criminalidad en México", 
            style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': 30}),
    
    html.Div([
        html.H3("📊 Estadísticas Generales"),
        html.P(f"Total de municipios analizados: {len(df)}"),
        html.P(f"Total de delitos: {df['total_delitos'].sum():,}" if len(df) > 0 else "No hay datos"),
        html.P(f"Tasa promedio: {df['tasa_delitos_100k'].mean():.2f}/100k hab" if len(df) > 0 else "No hay datos"),
    ], style={'backgroundColor': '#ecf0f1', 'padding': 20, 'margin': 10, 'borderRadius': 10}),
    
    html.Div([
        dcc.Graph(
            id='top-municipios',
            figure=create_top_municipios_chart(df)
        )
    ], style={'margin': 10}),
    
    html.Div([
        dcc.Graph(
            id='distribucion-riesgo',
            figure=create_risk_distribution_chart(df)
        )
    ], style={'margin': 10}),
    
    html.Div([
        dcc.Graph(
            id='poblacion-vs-delitos',
            figure=create_scatter_chart(df)
        )
    ], style={'margin': 10}),
    
    html.Footer([
        html.P("Proyecto Final - Análisis de Criminalidad en México", 
               style={'textAlign': 'center', 'color': '#7f8c8d', 'marginTop': 30})
    ])
])

if __name__ == '__main__':
    print("🌐 Iniciando dashboard en http://127.0.0.1:8050")
    print("🔄 Presiona Ctrl+C para detener")
    
    try:
        app.run(
            host='127.0.0.1',
            port=8050,
            debug=True
        )
    except Exception as e:
        print(f"❌ Error iniciando dashboard: {e}")
