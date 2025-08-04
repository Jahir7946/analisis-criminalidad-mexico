"""
Dashboard optimizado para datos de incidencias.xlsx - Análisis por estados
"""

import dash
from dash import dcc, html
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from pymongo import MongoClient
import os

# Configuración
MONGODB_URI = os.getenv('MONGODB_URI', "mongodb+srv://23202001:23202001@cluster0.vgypvgq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
DATABASE_NAME = os.getenv('DATABASE_NAME', 'criminalidad_mexico')
COLLECTION_NAME = 'criminalidad_estados'

def get_data():
    """Obtiene datos de MongoDB"""
    try:
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]
        
        data = list(collection.find())
        df = pd.DataFrame(data)
        
        if len(df) > 0 and '_id' in df.columns:
            df = df.drop('_id', axis=1)
        
        client.close()
        return df
    except Exception as e:
        print(f"Error obteniendo datos: {e}")
        # Fallback: cargar desde CSV si MongoDB falla
        try:
            df = pd.read_csv('data/raw/criminalidad_estados_2023.csv')
            return df
        except:
            return pd.DataFrame()

def create_top_estados_chart(df):
    """Crea gráfico de top estados por número de delitos"""
    if len(df) == 0:
        return {}
    
    top_10 = df.nlargest(10, 'Número de Delitos')
    
    fig = px.bar(
        top_10,
        x='Estado',
        y='Número de Delitos',
        color='Categoria_Riesgo',
        title='Top 10 Estados con Mayor Número de Delitos',
        labels={'Número de Delitos': 'Número de Delitos', 'Estado': 'Estado'},
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

def create_percentage_chart(df):
    """Crea gráfico de porcentaje de incidencia"""
    if len(df) == 0:
        return {}
    
    top_10_pct = df.nlargest(10, 'Porcentaje de Incidencia')
    
    fig = px.bar(
        top_10_pct,
        x='Estado',
        y='Porcentaje de Incidencia',
        color='Porcentaje de Incidencia',
        title='Top 10 Estados por Porcentaje de Incidencia',
        labels={'Porcentaje de Incidencia': 'Porcentaje de Incidencia (%)', 'Estado': 'Estado'},
        color_continuous_scale='Reds'
    )
    
    fig.update_layout(
        xaxis_tickangle=45,
        height=500
    )
    
    return fig

def create_risk_distribution_chart(df):
    """Crea gráfico de distribución por categoría de riesgo"""
    if len(df) == 0 or 'Categoria_Riesgo' not in df.columns:
        return {}
    
    risk_counts = df['Categoria_Riesgo'].value_counts()
    
    fig = px.pie(
        values=risk_counts.values,
        names=risk_counts.index,
        title='Distribución de Estados por Categoría de Riesgo',
        color_discrete_map={
            'Bajo': '#2ecc71',
            'Medio': '#f39c12',
            'Alto': '#e74c3c', 
            'Muy Alto': '#8e44ad'
        }
    )
    
    fig.update_layout(height=400)
    
    return fig

def create_ranking_chart(df):
    """Crea gráfico de ranking de estados"""
    if len(df) == 0:
        return {}
    
    # Ordenar por ranking
    df_sorted = df.sort_values('Ranking').head(15)
    
    fig = px.scatter(
        df_sorted,
        x='Ranking',
        y='Número de Delitos',
        size='Porcentaje de Incidencia',
        color='Categoria_Riesgo',
        hover_data=['Estado'],
        title='Ranking de Estados por Criminalidad',
        labels={'Ranking': 'Posición en Ranking', 'Número de Delitos': 'Número de Delitos'},
        color_discrete_map={
            'Bajo': '#2ecc71',
            'Medio': '#f39c12',
            'Alto': '#e74c3c',
            'Muy Alto': '#8e44ad'
        }
    )
    
    fig.update_layout(height=500)
    
    return fig

def create_comparison_chart(df):
    """Crea gráfico comparativo de delitos vs porcentaje"""
    if len(df) == 0:
        return {}
    
    fig = go.Figure()
    
    # Barras para número de delitos
    fig.add_trace(go.Bar(
        name='Número de Delitos',
        x=df['Estado'][:15],
        y=df['Número de Delitos'][:15],
        yaxis='y',
        offsetgroup=1
    ))
    
    # Línea para porcentaje de incidencia
    fig.add_trace(go.Scatter(
        name='Porcentaje de Incidencia',
        x=df['Estado'][:15],
        y=df['Porcentaje de Incidencia'][:15] * 100000,  # Escalar para visualización
        yaxis='y2',
        mode='lines+markers',
        line=dict(color='red', width=3)
    ))
    
    fig.update_layout(
        title='Comparación: Número de Delitos vs Porcentaje de Incidencia',
        xaxis=dict(title='Estado', tickangle=45),
        yaxis=dict(title='Número de Delitos', side='left'),
        yaxis2=dict(title='Porcentaje de Incidencia (x100k)', side='right', overlaying='y'),
        height=500
    )
    
    return fig

# Cargar datos
print("🔌 Conectando a base de datos...")
df = get_data()
print(f"📊 Datos cargados: {len(df)} registros")

# Crear aplicación Dash
app = dash.Dash(__name__)

# Layout del dashboard
app.layout = html.Div([
    html.H1("🚨 Dashboard de Criminalidad por Estados - México 2023", 
            style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': 30}),
    
    html.Div([
        html.H3("📊 Estadísticas Generales"),
        html.Div([
            html.Div([
                html.H4(f"{len(df)}", style={'fontSize': '2em', 'color': '#3498db', 'margin': 0}),
                html.P("Estados Analizados", style={'margin': 0})
            ], style={'textAlign': 'center'}, className='col-md-3'),
            
            html.Div([
                html.H4(f"{df['Número de Delitos'].sum():,}" if len(df) > 0 else "0", 
                        style={'fontSize': '2em', 'color': '#e74c3c', 'margin': 0}),
                html.P("Total de Delitos", style={'margin': 0})
            ], style={'textAlign': 'center'}, className='col-md-3'),
            
            html.Div([
                html.H4(f"{df['Número de Delitos'].mean():.0f}" if len(df) > 0 else "0", 
                        style={'fontSize': '2em', 'color': '#f39c12', 'margin': 0}),
                html.P("Promedio por Estado", style={'margin': 0})
            ], style={'textAlign': 'center'}, className='col-md-3'),
            
            html.Div([
                html.H4(f"{df['Porcentaje de Incidencia'].mean():.4f}" if len(df) > 0 else "0", 
                        style={'fontSize': '2em', 'color': '#9b59b6', 'margin': 0}),
                html.P("% Incidencia Promedio", style={'margin': 0})
            ], style={'textAlign': 'center'}, className='col-md-3'),
        ], style={'display': 'flex', 'justifyContent': 'space-around'})
    ], style={'backgroundColor': '#ecf0f1', 'padding': 20, 'margin': 10, 'borderRadius': 10}),
    
    html.Div([
        dcc.Graph(
            id='top-estados-delitos',
            figure=create_top_estados_chart(df)
        )
    ], style={'margin': 10}),
    
    html.Div([
        dcc.Graph(
            id='top-estados-porcentaje',
            figure=create_percentage_chart(df)
        )
    ], style={'margin': 10}),
    
    html.Div([
        html.Div([
            dcc.Graph(
                id='distribucion-riesgo',
                figure=create_risk_distribution_chart(df)
            )
        ], style={'width': '50%', 'display': 'inline-block'}),
        
        html.Div([
            dcc.Graph(
                id='ranking-estados',
                figure=create_ranking_chart(df)
            )
        ], style={'width': '50%', 'display': 'inline-block'})
    ]),
    
    html.Div([
        dcc.Graph(
            id='comparacion-delitos-porcentaje',
            figure=create_comparison_chart(df)
        )
    ], style={'margin': 10}),
    
    html.Footer([
        html.P("Proyecto Final - Análisis de Criminalidad por Estados en México 2023", 
               style={'textAlign': 'center', 'color': '#7f8c8d', 'marginTop': 30}),
        html.P("Datos actualizados con archivo incidencias.xlsx", 
               style={'textAlign': 'center', 'color': '#95a5a6', 'fontSize': '0.9em'})
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
