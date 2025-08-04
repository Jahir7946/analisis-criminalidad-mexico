"""
Dashboard interactivo para análisis de criminalidad en México
Desarrollado con Dash y Plotly
"""

import dash
from dash import dcc, html, Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.database.mongodb_connection import CriminalityQueries
from config import DASH_HOST, DASH_PORT, DASH_DEBUG, COLOR_PALETTE, TIPOS_DELITOS

# Inicializar la aplicación Dash
app = dash.Dash(__name__)
app.title = "Análisis de Criminalidad en México"

# Cargar datos
queries = CriminalityQueries()

def load_data():
    """Carga datos desde MongoDB"""
    try:
        collection = queries.collection
        if collection is not None:
            cursor = collection.find({})
            data = pd.DataFrame(list(cursor))
            return data
        else:
            print("❌ No se pudo conectar a la base de datos")
            return pd.DataFrame()
    except Exception as e:
        print(f"❌ Error al cargar datos: {e}")
        return pd.DataFrame()

# Cargar datos globalmente
df = load_data()

# Estilos CSS
external_stylesheets = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Layout principal
app.layout = html.Div([
    # Header
    html.Div([
        html.H1("🚨 Análisis de Criminalidad en México", 
                style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '10px'}),
        html.P("Dashboard interactivo con datos del INEGI - Proyecto Final", 
               style={'textAlign': 'center', 'color': '#7f8c8d', 'fontSize': '18px'}),
        html.Hr()
    ], style={'backgroundColor': '#ecf0f1', 'padding': '20px', 'marginBottom': '20px'}),
    
    # Métricas principales
    html.Div([
        html.Div([
            html.H3(f"{len(df):,}", style={'color': '#3498db', 'margin': '0'}),
            html.P("Municipios Analizados", style={'margin': '0'})
        ], className='three columns', style={'textAlign': 'center', 'backgroundColor': '#fff', 'padding': '20px', 'border': '1px solid #ddd'}),
        
        html.Div([
            html.H3(f"{df['total_delitos'].sum():,}" if not df.empty else "0", style={'color': '#e74c3c', 'margin': '0'}),
            html.P("Total de Delitos", style={'margin': '0'})
        ], className='three columns', style={'textAlign': 'center', 'backgroundColor': '#fff', 'padding': '20px', 'border': '1px solid #ddd'}),
        
        html.Div([
            html.H3(f"{df['estado'].nunique()}" if not df.empty else "0", style={'color': '#2ecc71', 'margin': '0'}),
            html.P("Estados Incluidos", style={'margin': '0'})
        ], className='three columns', style={'textAlign': 'center', 'backgroundColor': '#fff', 'padding': '20px', 'border': '1px solid #ddd'}),
        
        html.Div([
            html.H3(f"{df['tasa_delitos_100k'].mean():.1f}" if not df.empty else "0", style={'color': '#f39c12', 'margin': '0'}),
            html.P("Tasa Promedio/100k", style={'margin': '0'})
        ], className='three columns', style={'textAlign': 'center', 'backgroundColor': '#fff', 'padding': '20px', 'border': '1px solid #ddd'})
    ], className='row', style={'marginBottom': '30px'}),
    
    # Controles
    html.Div([
        html.Div([
            html.Label("Seleccionar Estado:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='estado-dropdown',
                options=[{'label': 'Todos los Estados', 'value': 'todos'}] + 
                        [{'label': estado, 'value': estado} for estado in sorted(df['estado'].unique())] if not df.empty else [],
                value='todos',
                style={'marginBottom': '10px'}
            )
        ], className='six columns'),
        
        html.Div([
            html.Label("Tipo de Visualización:", style={'fontWeight': 'bold'}),
            dcc.RadioItems(
                id='viz-type',
                options=[
                    {'label': ' Mapa de Calor', 'value': 'mapa'},
                    {'label': ' Gráfico de Barras', 'value': 'barras'},
                    {'label': ' Dispersión', 'value': 'scatter'}
                ],
                value='mapa',
                inline=True,
                style={'marginTop': '10px'}
            )
        ], className='six columns')
    ], className='row', style={'backgroundColor': '#f8f9fa', 'padding': '20px', 'marginBottom': '20px'}),
    
    # Gráficos principales
    html.Div([
        html.Div([
            dcc.Graph(id='main-chart')
        ], className='eight columns'),
        
        html.Div([
            dcc.Graph(id='delitos-pie-chart')
        ], className='four columns')
    ], className='row', style={'marginBottom': '20px'}),
    
    # Gráficos secundarios
    html.Div([
        html.Div([
            dcc.Graph(id='estados-ranking')
        ], className='six columns'),
        
        html.Div([
            dcc.Graph(id='correlation-heatmap')
        ], className='six columns')
    ], className='row', style={'marginBottom': '20px'}),
    
    # Tabla de datos
    html.Div([
        html.H3("📊 Top 20 Municipios con Mayor Tasa de Delitos", style={'color': '#2c3e50'}),
        html.Div(id='top-municipios-table')
    ], style={'backgroundColor': '#fff', 'padding': '20px', 'border': '1px solid #ddd'}),
    
    # Footer
    html.Div([
        html.Hr(),
        html.P("Desarrollado por: Equipo de Análisis de Datos | Fuente: INEGI/SNSP | Tecnologías: MongoDB, Python, Dash, Plotly", 
               style={'textAlign': 'center', 'color': '#7f8c8d', 'fontSize': '14px'})
    ], style={'marginTop': '40px'})
])

# Callbacks para interactividad
@app.callback(
    Output('main-chart', 'figure'),
    [Input('estado-dropdown', 'value'),
     Input('viz-type', 'value')]
)
def update_main_chart(selected_estado, viz_type):
    """Actualiza el gráfico principal"""
    if df.empty:
        return go.Figure().add_annotation(text="No hay datos disponibles", 
                                        xref="paper", yref="paper", x=0.5, y=0.5)
    
    # Filtrar datos
    if selected_estado == 'todos':
        filtered_df = df.copy()
        title_suffix = "- Todos los Estados"
    else:
        filtered_df = df[df['estado'] == selected_estado]
        title_suffix = f"- {selected_estado}"
    
    if filtered_df.empty:
        return go.Figure().add_annotation(text="No hay datos para el estado seleccionado", 
                                        xref="paper", yref="paper", x=0.5, y=0.5)
    
    # Crear gráfico según el tipo seleccionado
    if viz_type == 'mapa':
        fig = px.scatter_mapbox(
            filtered_df,
            lat='latitud',
            lon='longitud',
            size='total_delitos',
            color='tasa_delitos_100k',
            hover_name='municipio',
            hover_data={'estado': True, 'poblacion': ':,', 'tasa_delitos_100k': ':.2f'},
            color_continuous_scale='Reds',
            size_max=20,
            zoom=4,
            center={'lat': 23.6345, 'lon': -102.5528},
            mapbox_style='open-street-map',
            title=f'Mapa de Criminalidad por Municipio {title_suffix}'
        )
        fig.update_layout(height=500)
        
    elif viz_type == 'barras':
        top_municipios = filtered_df.nlargest(15, 'tasa_delitos_100k')
        fig = px.bar(
            top_municipios,
            x='tasa_delitos_100k',
            y='municipio',
            color='estado',
            orientation='h',
            title=f'Top 15 Municipios por Tasa de Delitos {title_suffix}',
            labels={'tasa_delitos_100k': 'Tasa de Delitos por 100k hab', 'municipio': 'Municipio'}
        )
        fig.update_layout(height=500, yaxis={'categoryorder': 'total ascending'})
        
    else:  # scatter
        fig = px.scatter(
            filtered_df,
            x='poblacion',
            y='total_delitos',
            size='tasa_delitos_100k',
            color='estado',
            hover_name='municipio',
            title=f'Relación Población vs Total de Delitos {title_suffix}',
            labels={'poblacion': 'Población', 'total_delitos': 'Total de Delitos'}
        )
        fig.update_layout(height=500)
        fig.update_xaxis(type='log')
    
    return fig

@app.callback(
    Output('delitos-pie-chart', 'figure'),
    [Input('estado-dropdown', 'value')]
)
def update_pie_chart(selected_estado):
    """Actualiza el gráfico de pie de tipos de delitos"""
    if df.empty:
        return go.Figure().add_annotation(text="No hay datos disponibles", 
                                        xref="paper", yref="paper", x=0.5, y=0.5)
    
    # Filtrar datos
    if selected_estado == 'todos':
        filtered_df = df.copy()
        title_suffix = "- Nacional"
    else:
        filtered_df = df[df['estado'] == selected_estado]
        title_suffix = f"- {selected_estado}"
    
    if filtered_df.empty:
        return go.Figure().add_annotation(text="No hay datos disponibles", 
                                        xref="paper", yref="paper", x=0.5, y=0.5)
    
    # Calcular totales por tipo de delito
    delitos_data = {
        'Homicidio Doloso': filtered_df['homicidio_doloso'].sum(),
        'Feminicidio': filtered_df['feminicidio'].sum(),
        'Lesiones Dolosas': filtered_df['lesiones_dolosas'].sum(),
        'Robo Casa': filtered_df['robo_casa_habitacion'].sum(),
        'Robo Vehículo': filtered_df['robo_vehiculo'].sum(),
        'Robo Transeúnte': filtered_df['robo_transeunte'].sum(),
        'Robo Negocio': filtered_df['robo_negocio'].sum(),
        'Violación': filtered_df['violacion'].sum(),
        'Secuestro': filtered_df['secuestro'].sum(),
        'Extorsión': filtered_df['extorsion'].sum()
    }
    
    # Filtrar delitos con valores > 0
    delitos_data = {k: v for k, v in delitos_data.items() if v > 0}
    
    fig = px.pie(
        values=list(delitos_data.values()),
        names=list(delitos_data.keys()),
        title=f'Distribución de Tipos de Delitos {title_suffix}',
        color_discrete_sequence=COLOR_PALETTE
    )
    fig.update_layout(height=400)
    
    return fig

@app.callback(
    Output('estados-ranking', 'figure'),
    [Input('estado-dropdown', 'value')]
)
def update_estados_ranking(selected_estado):
    """Actualiza el ranking de estados"""
    if df.empty:
        return go.Figure().add_annotation(text="No hay datos disponibles", 
                                        xref="paper", yref="paper", x=0.5, y=0.5)
    
    # Agrupar por estado
    estados_stats = df.groupby('estado').agg({
        'total_delitos': 'sum',
        'poblacion': 'sum'
    }).reset_index()
    
    estados_stats['tasa_estado'] = (estados_stats['total_delitos'] / estados_stats['poblacion'] * 100000).round(2)
    estados_stats = estados_stats.sort_values('tasa_estado', ascending=True).tail(15)
    
    fig = px.bar(
        estados_stats,
        x='tasa_estado',
        y='estado',
        orientation='h',
        title='Top 15 Estados por Tasa de Delitos',
        labels={'tasa_estado': 'Tasa por 100k habitantes', 'estado': 'Estado'},
        color='tasa_estado',
        color_continuous_scale='Reds'
    )
    fig.update_layout(height=400, yaxis={'categoryorder': 'total ascending'})
    
    return fig

@app.callback(
    Output('correlation-heatmap', 'figure'),
    [Input('estado-dropdown', 'value')]
)
def update_correlation_heatmap(selected_estado):
    """Actualiza el mapa de calor de correlaciones"""
    if df.empty:
        return go.Figure().add_annotation(text="No hay datos disponibles", 
                                        xref="paper", yref="paper", x=0.5, y=0.5)
    
    # Filtrar datos
    if selected_estado == 'todos':
        filtered_df = df.copy()
    else:
        filtered_df = df[df['estado'] == selected_estado]
    
    if filtered_df.empty:
        return go.Figure().add_annotation(text="No hay datos disponibles", 
                                        xref="paper", yref="paper", x=0.5, y=0.5)
    
    # Seleccionar columnas para correlación
    corr_columns = [
        'homicidio_doloso', 'feminicidio', 'lesiones_dolosas',
        'robo_casa_habitacion', 'robo_vehiculo', 'robo_transeunte',
        'robo_negocio', 'violacion', 'secuestro', 'extorsion'
    ]
    
    # Filtrar columnas que existen
    available_columns = [col for col in corr_columns if col in filtered_df.columns]
    
    if len(available_columns) < 2:
        return go.Figure().add_annotation(text="Datos insuficientes para correlación", 
                                        xref="paper", yref="paper", x=0.5, y=0.5)
    
    # Calcular correlación
    corr_matrix = filtered_df[available_columns].corr()
    
    # Crear labels más legibles
    labels = [col.replace('_', ' ').title() for col in available_columns]
    
    fig = px.imshow(
        corr_matrix,
        x=labels,
        y=labels,
        color_continuous_scale='RdBu',
        aspect='auto',
        title='Correlación entre Tipos de Delitos'
    )
    fig.update_layout(height=400)
    
    return fig

@app.callback(
    Output('top-municipios-table', 'children'),
    [Input('estado-dropdown', 'value')]
)
def update_top_municipios_table(selected_estado):
    """Actualiza la tabla de top municipios"""
    if df.empty:
        return html.P("No hay datos disponibles")
    
    # Filtrar datos
    if selected_estado == 'todos':
        filtered_df = df.copy()
    else:
        filtered_df = df[df['estado'] == selected_estado]
    
    if filtered_df.empty:
        return html.P("No hay datos para el estado seleccionado")
    
    # Top 20 municipios
    top_municipios = filtered_df.nlargest(20, 'tasa_delitos_100k')
    
    # Crear tabla HTML
    table_header = [
        html.Thead([
            html.Tr([
                html.Th("#", style={'padding': '10px', 'backgroundColor': '#3498db', 'color': 'white'}),
                html.Th("Municipio", style={'padding': '10px', 'backgroundColor': '#3498db', 'color': 'white'}),
                html.Th("Estado", style={'padding': '10px', 'backgroundColor': '#3498db', 'color': 'white'}),
                html.Th("Población", style={'padding': '10px', 'backgroundColor': '#3498db', 'color': 'white'}),
                html.Th("Total Delitos", style={'padding': '10px', 'backgroundColor': '#3498db', 'color': 'white'}),
                html.Th("Tasa/100k", style={'padding': '10px', 'backgroundColor': '#3498db', 'color': 'white'}),
                html.Th("Categoría", style={'padding': '10px', 'backgroundColor': '#3498db', 'color': 'white'})
            ])
        ])
    ]
    
    table_body = []
    for i, (_, row) in enumerate(top_municipios.iterrows()):
        # Color de fila según categoría de riesgo
        if row.get('categoria_riesgo') == 'Muy Alto':
            row_color = '#ffebee'
        elif row.get('categoria_riesgo') == 'Alto':
            row_color = '#fff3e0'
        elif row.get('categoria_riesgo') == 'Medio':
            row_color = '#f3e5f5'
        else:
            row_color = '#e8f5e8'
        
        table_body.append(
            html.Tr([
                html.Td(f"{i+1}", style={'padding': '8px', 'backgroundColor': row_color}),
                html.Td(row['municipio'], style={'padding': '8px', 'backgroundColor': row_color}),
                html.Td(row['estado'], style={'padding': '8px', 'backgroundColor': row_color}),
                html.Td(f"{row['poblacion']:,}", style={'padding': '8px', 'backgroundColor': row_color}),
                html.Td(f"{row['total_delitos']:,}", style={'padding': '8px', 'backgroundColor': row_color}),
                html.Td(f"{row['tasa_delitos_100k']:.2f}", style={'padding': '8px', 'backgroundColor': row_color}),
                html.Td(row.get('categoria_riesgo', 'N/A'), style={'padding': '8px', 'backgroundColor': row_color})
            ])
        )
    
    return html.Table(
        table_header + [html.Tbody(table_body)],
        style={'width': '100%', 'border': '1px solid #ddd', 'borderCollapse': 'collapse'}
    )

# Ejecutar la aplicación
if __name__ == '__main__':
    print("🚀 Iniciando dashboard de criminalidad...")
    print(f"📊 Datos cargados: {len(df)} registros")
    print(f"🌐 Accede al dashboard en: http://{DASH_HOST}:{DASH_PORT}")
    
    app.run_server(
        host=DASH_HOST,
        port=DASH_PORT,
        debug=DASH_DEBUG
    )
