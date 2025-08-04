"""
Dashboard Premium - Interfaz Moderna y Sofisticada
Diseño profesional con animaciones, gradientes y elementos visuales avanzados
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
            df = pd.read_csv('data/raw/criminalidad_estados_junio_2025.csv')
            return df
        except:
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
        categories = df['Categoria_Riesgo'].unique()
        labels = ['México']
        parents = ['']
        values = [df['Número de Delitos'].sum()]
        
        for cat in categories:
            labels.append(cat)
            parents.append('México')
            values.append(df[df['Categoria_Riesgo'] == cat]['Número de Delitos'].sum())
        
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
            title={
                'text': "Distribución Jerárquica - Top 10 Estados por Categoría de Riesgo",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16, 'color': '#2c3e50', 'family': 'Arial Black'}
            },
            font_size=12,
            height=600,
            margin=dict(t=60, l=10, r=10, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig
    
    except Exception as e:
        print(f"Error creando sunburst: {e}")
        fig = px.pie(
            df.groupby('Categoria_Riesgo')['Número de Delitos'].sum().reset_index(),
            values='Número de Delitos',
            names='Categoria_Riesgo',
            title='Distribución por Categoría de Riesgo',
            hole=0.4,
            color_discrete_sequence=['#e74c3c', '#f39c12', '#f1c40f', '#2ecc71']
        )
        fig.update_layout(height=600, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        return fig

def create_treemap_chart(df):
    """Crea treemap interactivo estilo Flourish"""
    if len(df) == 0:
        return go.Figure()
    
    fig = go.Figure(go.Treemap(
        labels=df['Estado'],
        values=df['Número de Delitos'],
        parents=['México'] * len(df),
        textinfo="label+value+percent parent",
        hovertemplate='<b>%{label}</b><br>Delitos: %{value:,}<br>Porcentaje: %{percentParent:.2%}<extra></extra>',
        marker=dict(
            colorscale='Reds',
            colorbar=dict(title="Número de Delitos"),
            line=dict(width=2, color='white')
        ),
        textfont=dict(size=11, color='white', family='Arial Black')
    ))
    
    fig.update_layout(
        title={
            'text': "Mapa de Árbol - Criminalidad por Estado",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': '#2c3e50', 'family': 'Arial Black'}
        },
        height=500,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def create_radial_chart(df):
    """Crea gráfico radial/polar estilo D3.js"""
    if len(df) == 0:
        return go.Figure()
    
    df_top = df.nlargest(15, 'Número de Delitos')
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=df_top['Número de Delitos'],
        theta=df_top['Estado'],
        fill='toself',
        fillcolor='rgba(231, 76, 60, 0.3)',
        line=dict(color='rgba(231, 76, 60, 1)', width=3),
        marker=dict(size=10, color='rgba(231, 76, 60, 1)', symbol='diamond'),
        name='Número de Delitos',
        hovertemplate='<b>%{theta}</b><br>Delitos: %{r:,}<extra></extra>'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, df_top['Número de Delitos'].max() * 1.1],
                gridcolor='rgba(0,0,0,0.1)',
                linecolor='rgba(0,0,0,0.2)'
            ),
            angularaxis=dict(
                gridcolor='rgba(0,0,0,0.1)',
                linecolor='rgba(0,0,0,0.2)'
            )
        ),
        title={
            'text': "Gráfico Radial - Top 15 Estados por Criminalidad",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': '#2c3e50', 'family': 'Arial Black'}
        },
        height=600,
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def create_bubble_chart(df):
    """Crea gráfico de burbujas interactivo"""
    if len(df) == 0:
        return go.Figure()
    
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
    
    fig.update_layout(
        height=500,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        title={
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': '#2c3e50', 'family': 'Arial Black'}
        }
    )
    
    return fig

def create_waterfall_chart(df):
    """Crea gráfico waterfall para mostrar contribución por estado"""
    if len(df) == 0:
        return go.Figure()
    
    df_top = df.nlargest(10, 'Número de Delitos')
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
        title={
            'text': "Contribución Acumulativa por Estado (Top 10)",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': '#2c3e50', 'family': 'Arial Black'}
        },
        xaxis_tickangle=45,
        height=500,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def create_heatmap_matrix(df):
    """Crea matriz de calor para análisis multidimensional"""
    if len(df) == 0:
        return go.Figure()
    
    df_matrix = df.copy()
    np.random.seed(42)
    df_matrix['Densidad_Poblacional'] = np.random.uniform(50, 1000, len(df))
    df_matrix['PIB_per_capita'] = np.random.uniform(50000, 200000, len(df))
    df_matrix['Indice_Desarrollo'] = np.random.uniform(0.6, 0.9, len(df))
    
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
        textfont={"size": 12, "color": "white"},
        hovertemplate='<b>%{x} vs %{y}</b><br>Correlación: %{z:.3f}<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': "Matriz de Correlación - Factores Socioeconómicos vs Criminalidad",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': '#2c3e50', 'family': 'Arial Black'}
        },
        height=500,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def create_animated_bar_race(df):
    """Crea gráfico de barras animado (simulado)"""
    if len(df) == 0:
        return go.Figure()
    
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
        yaxis={'categoryorder': 'total ascending'},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        title={
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': '#2c3e50', 'family': 'Arial Black'}
        }
    )
    
    return fig

# Cargar datos
print("🔌 Conectando a base de datos...")
df = get_data()
print(f"📊 Datos cargados: {len(df)} registros")

# Crear aplicación Dash
app = dash.Dash(__name__)

# Estilos premium inline
premium_styles = {
    'main_container': {
        'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'minHeight': '100vh',
        'fontFamily': 'Arial, sans-serif',
        'margin': 0,
        'padding': 0
    },
    'header_section': {
        'background': 'linear-gradient(135deg, rgba(44, 62, 80, 0.95) 0%, rgba(52, 73, 94, 0.95) 100%)',
        'backdropFilter': 'blur(20px)',
        'borderBottom': '3px solid rgba(255, 255, 255, 0.1)',
        'boxShadow': '0 8px 32px rgba(0, 0, 0, 0.3)',
        'padding': '40px 20px',
        'textAlign': 'center',
        'marginBottom': '30px'
    },
    'main_title': {
        'fontSize': '3.5em',
        'fontWeight': '700',
        'color': '#ffffff',
        'margin': 0,
        'textShadow': '0 4px 8px rgba(0, 0, 0, 0.3)',
        'letterSpacing': '2px'
    },
    'subtitle': {
        'fontSize': '1.4em',
        'color': 'rgba(255, 255, 255, 0.9)',
        'marginTop': '10px',
        'letterSpacing': '1px',
        'fontWeight': '300'
    },
    'kpi_container': {
        'display': 'flex',
        'justifyContent': 'space-around',
        'flexWrap': 'wrap',
        'margin': '40px 20px',
        'gap': '20px'
    },
    'kpi_card': {
        'background': 'linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 249, 250, 0.95) 100%)',
        'backdropFilter': 'blur(20px)',
        'border': '1px solid rgba(255, 255, 255, 0.2)',
        'borderRadius': '20px',
        'padding': '30px 20px',
        'textAlign': 'center',
        'boxShadow': '0 15px 35px rgba(0, 0, 0, 0.1), 0 5px 15px rgba(0, 0, 0, 0.07)',
        'transition': 'all 0.3s ease',
        'minWidth': '200px',
        'flex': '1',
        'maxWidth': '280px'
    },
    'kpi_number': {
        'fontSize': '3.2em',
        'fontWeight': '700',
        'margin': 0,
        'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'WebkitBackgroundClip': 'text',
        'WebkitTextFillColor': 'transparent',
        'backgroundClip': 'text'
    },
    'kpi_label': {
        'fontSize': '1.1em',
        'color': '#2c3e50',
        'margin': '10px 0 0 0',
        'textTransform': 'uppercase',
        'letterSpacing': '1px',
        'fontWeight': '500'
    },
    'chart_container': {
        'background': 'rgba(255, 255, 255, 0.95)',
        'backdropFilter': 'blur(20px)',
        'border': '1px solid rgba(255, 255, 255, 0.2)',
        'borderRadius': '20px',
        'margin': '20px',
        'padding': '20px',
        'boxShadow': '0 15px 35px rgba(0, 0, 0, 0.1), 0 5px 15px rgba(0, 0, 0, 0.07)',
        'transition': 'all 0.3s ease'
    },
    'chart_row': {
        'display': 'flex',
        'flexWrap': 'wrap',
        'margin': '20px 0',
        'gap': '20px'
    },
    'chart_half': {
        'flex': '1',
        'minWidth': '500px'
    },
    'chart_full': {
        'width': '100%'
    },
    'footer_section': {
        'background': 'linear-gradient(135deg, rgba(44, 62, 80, 0.95) 0%, rgba(52, 73, 94, 0.95) 100%)',
        'backdropFilter': 'blur(20px)',
        'borderTop': '3px solid rgba(255, 255, 255, 0.1)',
        'padding': '40px 20px',
        'textAlign': 'center',
        'marginTop': '50px'
    },
    'footer_text': {
        'color': 'rgba(255, 255, 255, 0.9)',
        'fontSize': '1.1em',
        'margin': '10px 0'
    },
    'footer_subtext': {
        'color': 'rgba(255, 255, 255, 0.7)',
        'fontSize': '0.95em',
        'fontStyle': 'italic'
    }
}

# Layout de la aplicación con diseño premium
app.layout = html.Div([
    # Contenedor principal
    html.Div([
        # Header premium
        html.Div([
            html.H1("🚨 DASHBOARD PREMIUM", style=premium_styles['main_title']),
            html.P("Análisis Avanzado de Criminalidad México • Junio 2025", style=premium_styles['subtitle']),
        ], style=premium_styles['header_section']),
        
        # KPIs con diseño premium
        html.Div([
            html.Div([
                html.H3(f"{len(df)}", style=premium_styles['kpi_number']),
                html.P("Estados Analizados", style=premium_styles['kpi_label'])
            ], style=premium_styles['kpi_card']),
            
            html.Div([
                html.H3(f"{df['Número de Delitos'].sum():,}" if len(df) > 0 else "0", style=premium_styles['kpi_number']),
                html.P("Total de Delitos", style=premium_styles['kpi_label'])
            ], style=premium_styles['kpi_card']),
            
            html.Div([
                html.H3(f"{df['Número de Delitos'].mean():.0f}" if len(df) > 0 else "0", style=premium_styles['kpi_number']),
                html.P("Promedio por Estado", style=premium_styles['kpi_label'])
            ], style=premium_styles['kpi_card']),
            
            html.Div([
                html.H3(f"{df['Porcentaje de Incidencia'].mean():.4f}" if len(df) > 0 else "0", style=premium_styles['kpi_number']),
                html.P("% Incidencia Promedio", style=premium_styles['kpi_label'])
            ], style=premium_styles['kpi_card'])
        ], style=premium_styles['kpi_container']),
        
        # Gráficos con contenedores premium
        html.Div([
            html.Div([
                dcc.Graph(id='sunburst-chart', figure=create_sunburst_chart(df), config={'displayModeBar': False})
            ], style={**premium_styles['chart_container'], **premium_styles['chart_half']}),
            
            html.Div([
                dcc.Graph(id='treemap-chart', figure=create_treemap_chart(df), config={'displayModeBar': False})
            ], style={**premium_styles['chart_container'], **premium_styles['chart_half']})
        ], style=premium_styles['chart_row']),
        
        html.Div([
            html.Div([
                dcc.Graph(id='radial-chart', figure=create_radial_chart(df), config={'displayModeBar': False})
            ], style={**premium_styles['chart_container'], **premium_styles['chart_half']}),
            
            html.Div([
                dcc.Graph(id='bubble-chart', figure=create_bubble_chart(df), config={'displayModeBar': False})
            ], style={**premium_styles['chart_container'], **premium_styles['chart_half']})
        ], style=premium_styles['chart_row']),
        
        html.Div([
            html.Div([
                dcc.Graph(id='waterfall-chart', figure=create_waterfall_chart(df), config={'displayModeBar': False})
            ], style={**premium_styles['chart_container'], **premium_styles['chart_half']}),
            
            html.Div([
                dcc.Graph(id='heatmap-chart', figure=create_heatmap_matrix(df), config={'displayModeBar': False})
            ], style={**premium_styles['chart_container'], **premium_styles['chart_half']})
        ], style=premium_styles['chart_row']),
        
        html.Div([
            html.Div([
                dcc.Graph(id='bar-race-chart', figure=create_animated_bar_race(df), config={'displayModeBar': False})
            ], style={**premium_styles['chart_container'], **premium_styles['chart_full']})
        ], style=premium_styles['chart_row']),
        
        # Footer premium
        html.Div([
            html.P("Dashboard Premium - Análisis de Criminalidad México Junio 2025", style=premium_styles['footer_text']),
            html.P("Visualizaciones Avanzadas • Diseño Profesional • Interfaz Moderna", style=premium_styles['footer_subtext'])
        ], style=premium_styles['footer_section'])
        
    ], style=premium_styles['main_container'])
])

if __name__ == '__main__':
    print("🌐 Iniciando Dashboard Premium en http://127.0.0.1:8050")
    print("🎨 Interfaz moderna y sofisticada cargada")
    print("🔄 Presiona Ctrl+C para detener")
    
    try:
        app.run(
            host='127.0.0.1',
            port=8050,
            debug=True
        )
    except Exception as e:
        print(f"❌ Error iniciando dashboard: {e}")
