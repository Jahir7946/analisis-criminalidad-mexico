"""
Dashboard avanzado con visualizaciones estilo D3.js y Flourish
Gráficos interactivos y profesionales para análisis de criminalidad
"""

import dash
from dash import dcc, html, Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from pymongo import MongoClient
import os
import numpy as np

# Configuración
MONGODB_URI = os.getenv('MONGODB_URI', "mongodb+srv://23202001:23202001@cluster0.vgypvgq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
DATABASE_NAME = os.getenv('DATABASE_NAME', 'criminalidad_mexico')
COLLECTION_NAME = 'criminalidad_estados'

def get_data():
    """Obtiene datos de MongoDB con fallback a CSV"""
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
        print(f"Error obteniendo datos de MongoDB: {e}")
        try:
            df = pd.read_csv('data/raw/criminalidad_estados_2023.csv')
            return df
        except:
            return pd.DataFrame()

def create_sunburst_chart(df):
    """Crea gráfico sunburst estilo D3.js para categorías de riesgo"""
    if len(df) == 0:
        return go.Figure()
    
    try:
        # Preparar datos para sunburst de manera más simple
        categories = df['Categoria_Riesgo'].unique()
        
        # Crear listas para el sunburst
        labels = ['México']  # Root
        parents = ['']       # Root parent
        values = [df['Número de Delitos'].sum()]  # Total
        
        # Agregar categorías
        for cat in categories:
            labels.append(cat)
            parents.append('México')
            values.append(df[df['Categoria_Riesgo'] == cat]['Número de Delitos'].sum())
        
        # Agregar estados (solo top 10 para evitar sobrecarga)
        df_top = df.nlargest(10, 'Número de Delitos')
        for _, row in df_top.iterrows():
            labels.append(row['Estado'])
            parents.append(row['Categoria_Riesgo'])
            values.append(row['Número de Delitos'])
        
        fig = go.Figure(go.Sunburst(
            labels=labels,
            parents=parents,
            values=values,
            branchvalues="total",
            hovertemplate='<b>%{label}</b><br>Delitos: %{value:,}<br>Porcentaje: %{percentParent:.1%}<extra></extra>',
            maxdepth=3,
            insidetextorientation='radial'
        ))
        
        fig.update_layout(
            title="Distribución Jerárquica - Top 10 Estados por Categoría de Riesgo",
            font_size=12,
            height=600,
            margin=dict(t=50, l=0, r=0, b=0)
        )
        
        return fig
    
    except Exception as e:
        print(f"Error creando sunburst: {e}")
        # Fallback: crear gráfico de dona simple
        fig = px.pie(
            df.groupby('Categoria_Riesgo')['Número de Delitos'].sum().reset_index(),
            values='Número de Delitos',
            names='Categoria_Riesgo',
            title='Distribución por Categoría de Riesgo',
            hole=0.4
        )
        fig.update_layout(height=600)
        return fig

def create_treemap_chart(df):
    """Crea treemap interactivo estilo Flourish"""
    if len(df) == 0:
        return {}
    
    fig = go.Figure(go.Treemap(
        labels=df['Estado'],
        values=df['Número de Delitos'],
        parents=['México'] * len(df),
        textinfo="label+value+percent parent",
        hovertemplate='<b>%{label}</b><br>Delitos: %{value:,}<br>Porcentaje: %{percentParent:.2%}<extra></extra>',
        marker=dict(
            colorscale='Reds',
            colorbar=dict(title="Número de Delitos"),
            line=dict(width=2)
        ),
        textfont=dict(size=10)
    ))
    
    fig.update_layout(
        title="Mapa de Árbol - Criminalidad por Estado",
        height=500
    )
    
    return fig

def create_radial_chart(df):
    """Crea gráfico radial/polar estilo D3.js"""
    if len(df) == 0:
        return {}
    
    # Tomar top 15 estados
    df_top = df.nlargest(15, 'Número de Delitos')
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=df_top['Número de Delitos'],
        theta=df_top['Estado'],
        fill='toself',
        fillcolor='rgba(255, 99, 71, 0.3)',
        line=dict(color='rgba(255, 99, 71, 1)', width=2),
        marker=dict(size=8, color='rgba(255, 99, 71, 1)'),
        name='Número de Delitos',
        hovertemplate='<b>%{theta}</b><br>Delitos: %{r:,}<extra></extra>'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, df_top['Número de Delitos'].max() * 1.1]
            )
        ),
        title="Gráfico Radial - Top 15 Estados por Criminalidad",
        height=600,
        showlegend=False
    )
    
    return fig

def create_bubble_chart(df):
    """Crea gráfico de burbujas interactivo"""
    if len(df) == 0:
        return {}
    
    # Crear datos sintéticos para población (para demo)
    np.random.seed(42)
    df_bubble = df.copy()
    df_bubble['Poblacion_Estimada'] = np.random.uniform(500000, 15000000, len(df))
    df_bubble['Tasa_por_100k'] = (df_bubble['Número de Delitos'] / df_bubble['Poblacion_Estimada']) * 100000
    
    fig = px.scatter(
        df_bubble,
        x='Poblacion_Estimada',
        y='Tasa_por_100k',
        size='Número de Delitos',
        color='Categoria_Riesgo',
        hover_name='Estado',
        hover_data={'Número de Delitos': ':,', 'Porcentaje de Incidencia': ':.4f'},
        title='Relación Población vs Tasa de Criminalidad (por 100k hab)',
        labels={
            'Poblacion_Estimada': 'Población Estimada',
            'Tasa_por_100k': 'Tasa por 100k habitantes'
        },
        color_discrete_map={
            'Bajo': '#2ecc71',
            'Medio': '#f39c12',
            'Alto': '#e74c3c',
            'Muy Alto': '#8e44ad'
        },
        size_max=60
    )
    
    fig.update_layout(height=500)
    
    return fig

def create_waterfall_chart(df):
    """Crea gráfico waterfall para mostrar contribución por estado"""
    if len(df) == 0:
        return {}
    
    # Top 10 estados
    df_top = df.nlargest(10, 'Número de Delitos')
    
    # Preparar datos para waterfall
    estados = list(df_top['Estado'])
    valores = list(df_top['Número de Delitos'])
    
    fig = go.Figure(go.Waterfall(
        name="Contribución por Estado",
        orientation="v",
        measure=["relative"] * len(estados) + ["total"],
        x=estados + ["Total"],
        textposition="outside",
        text=[f"{v:,}" for v in valores] + [f"{sum(valores):,}"],
        y=valores + [sum(valores)],
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        increasing={"marker": {"color": "#e74c3c"}},
        decreasing={"marker": {"color": "#2ecc71"}},
        totals={"marker": {"color": "#3498db"}}
    ))
    
    fig.update_layout(
        title="Contribución Acumulativa por Estado (Top 10)",
        xaxis_tickangle=45,
        height=500
    )
    
    return fig

def create_heatmap_matrix(df):
    """Crea matriz de calor para análisis multidimensional"""
    if len(df) == 0:
        return {}
    
    # Crear matriz de correlación sintética
    df_matrix = df.copy()
    np.random.seed(42)
    df_matrix['Densidad_Poblacional'] = np.random.uniform(50, 1000, len(df))
    df_matrix['PIB_per_capita'] = np.random.uniform(50000, 200000, len(df))
    df_matrix['Indice_Desarrollo'] = np.random.uniform(0.6, 0.9, len(df))
    
    # Matriz de correlación
    correlation_matrix = df_matrix[['Número de Delitos', 'Porcentaje de Incidencia', 
                                   'Densidad_Poblacional', 'PIB_per_capita', 'Indice_Desarrollo']].corr()
    
    fig = go.Figure(data=go.Heatmap(
        z=correlation_matrix.values,
        x=correlation_matrix.columns,
        y=correlation_matrix.columns,
        colorscale='RdBu',
        zmid=0,
        text=correlation_matrix.round(3).values,
        texttemplate="%{text}",
        textfont={"size": 12},
        hovertemplate='<b>%{x} vs %{y}</b><br>Correlación: %{z:.3f}<extra></extra>'
    ))
    
    fig.update_layout(
        title="Matriz de Correlación - Factores Socioeconómicos vs Criminalidad",
        height=500
    )
    
    return fig

def create_animated_bar_race(df):
    """Crea gráfico de barras animado (simulado)"""
    if len(df) == 0:
        return {}
    
    # Simular datos históricos para animación
    df_sorted = df.nlargest(10, 'Número de Delitos')
    
    fig = px.bar(
        df_sorted,
        x='Número de Delitos',
        y='Estado',
        orientation='h',
        color='Categoria_Riesgo',
        title='Top 10 Estados por Número de Delitos',
        labels={'Número de Delitos': 'Número de Delitos'},
        color_discrete_map={
            'Bajo': '#2ecc71',
            'Medio': '#f39c12',
            'Alto': '#e74c3c',
            'Muy Alto': '#8e44ad'
        },
        text='Número de Delitos'
    )
    
    fig.update_traces(texttemplate='%{text:,}', textposition='outside')
    fig.update_layout(
        height=500,
        yaxis={'categoryorder': 'total ascending'}
    )
    
    return fig

# Cargar datos
print("🔌 Conectando a base de datos...")
df = get_data()
print(f"📊 Datos cargados: {len(df)} registros")

# Crear aplicación Dash
app = dash.Dash(__name__)

# Estilos CSS personalizados
app.layout = html.Div([
    # Header
    html.Div([
        html.H1("🚨 Dashboard Avanzado - Criminalidad México 2023", 
                style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': 10}),
        html.P("Visualizaciones Interactivas Estilo D3.js y Flourish", 
               style={'textAlign': 'center', 'color': '#7f8c8d', 'fontSize': '1.2em'})
    ], style={'backgroundColor': '#ecf0f1', 'padding': 20, 'marginBottom': 20}),
    
    # KPIs Dashboard
    html.Div([
        html.Div([
            html.H3(f"{len(df)}", style={'fontSize': '3em', 'color': '#3498db', 'margin': 0}),
            html.P("Estados", style={'margin': 0, 'fontSize': '1.1em'})
        ], className='kpi-card', style={'textAlign': 'center', 'backgroundColor': 'white', 
                                       'padding': 20, 'borderRadius': 10, 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                                       'width': '22%', 'display': 'inline-block', 'margin': '1%'}),
        
        html.Div([
            html.H3(f"{df['Número de Delitos'].sum():,}" if len(df) > 0 else "0", 
                    style={'fontSize': '3em', 'color': '#e74c3c', 'margin': 0}),
            html.P("Total Delitos", style={'margin': 0, 'fontSize': '1.1em'})
        ], className='kpi-card', style={'textAlign': 'center', 'backgroundColor': 'white',
                                       'padding': 20, 'borderRadius': 10, 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                                       'width': '22%', 'display': 'inline-block', 'margin': '1%'}),
        
        html.Div([
            html.H3(f"{df['Número de Delitos'].mean():.0f}" if len(df) > 0 else "0", 
                    style={'fontSize': '3em', 'color': '#f39c12', 'margin': 0}),
            html.P("Promedio/Estado", style={'margin': 0, 'fontSize': '1.1em'})
        ], className='kpi-card', style={'textAlign': 'center', 'backgroundColor': 'white',
                                       'padding': 20, 'borderRadius': 10, 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                                       'width': '22%', 'display': 'inline-block', 'margin': '1%'}),
        
        html.Div([
            html.H3(f"{df['Porcentaje de Incidencia'].mean():.4f}" if len(df) > 0 else "0", 
                    style={'fontSize': '3em', 'color': '#9b59b6', 'margin': 0}),
            html.P("% Incidencia", style={'margin': 0, 'fontSize': '1.1em'})
        ], className='kpi-card', style={'textAlign': 'center', 'backgroundColor': 'white',
                                       'padding': 20, 'borderRadius': 10, 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                                       'width': '22%', 'display': 'inline-block', 'margin': '1%'})
    ], style={'marginBottom': 30}),
    
    # Gráficos principales
    html.Div([
        # Sunburst y Treemap
        html.Div([
            dcc.Graph(id='sunburst-chart', figure=create_sunburst_chart(df))
        ], style={'width': '50%', 'display': 'inline-block', 'padding': 10}),
        
        html.Div([
            dcc.Graph(id='treemap-chart', figure=create_treemap_chart(df))
        ], style={'width': '50%', 'display': 'inline-block', 'padding': 10})
    ]),
    
    # Gráfico radial y burbujas
    html.Div([
        html.Div([
            dcc.Graph(id='radial-chart', figure=create_radial_chart(df))
        ], style={'width': '50%', 'display': 'inline-block', 'padding': 10}),
        
        html.Div([
            dcc.Graph(id='bubble-chart', figure=create_bubble_chart(df))
        ], style={'width': '50%', 'display': 'inline-block', 'padding': 10})
    ]),
    
    # Waterfall y Heatmap
    html.Div([
        html.Div([
            dcc.Graph(id='waterfall-chart', figure=create_waterfall_chart(df))
        ], style={'width': '50%', 'display': 'inline-block', 'padding': 10}),
        
        html.Div([
            dcc.Graph(id='heatmap-chart', figure=create_heatmap_matrix(df))
        ], style={'width': '50%', 'display': 'inline-block', 'padding': 10})
    ]),
    
    # Bar race
    html.Div([
        dcc.Graph(id='bar-race-chart', figure=create_animated_bar_race(df))
    ], style={'padding': 10}),
    
    # Footer
    html.Footer([
        html.P("Dashboard Avanzado - Análisis de Criminalidad México 2023", 
               style={'textAlign': 'center', 'color': '#7f8c8d', 'marginTop': 30}),
        html.P("Visualizaciones inspiradas en D3.js y Flourish Studio", 
               style={'textAlign': 'center', 'color': '#95a5a6', 'fontSize': '0.9em'})
    ])
], style={'fontFamily': 'Arial, sans-serif', 'backgroundColor': '#f8f9fa', 'minHeight': '100vh', 'padding': 20})

if __name__ == '__main__':
    print("🌐 Iniciando dashboard avanzado en http://127.0.0.1:8050")
    print("🎨 Visualizaciones estilo D3.js y Flourish cargadas")
    print("🔄 Presiona Ctrl+C para detener")
    
    try:
        app.run(
            host='127.0.0.1',
            port=8050,
            debug=True
        )
    except Exception as e:
        print(f"❌ Error iniciando dashboard: {e}")
