# 📚 Documentación Técnica del Proyecto

## Análisis de Criminalidad en México usando MongoDB, Dash y datos del INEGI

---

## 📋 Tabla de Contenidos

1. [Arquitectura del Sistema](#arquitectura-del-sistema)
2. [Base de Datos](#base-de-datos)
3. [Proceso ETL](#proceso-etl)
4. [API y Conexiones](#api-y-conexiones)
5. [Dashboard Interactivo](#dashboard-interactivo)
6. [Análisis Estadístico](#análisis-estadístico)
7. [Instalación y Configuración](#instalación-y-configuración)
8. [Uso del Sistema](#uso-del-sistema)
9. [Troubleshooting](#troubleshooting)

---

## 🏗️ Arquitectura del Sistema

### Componentes Principales

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Datos INEGI   │───▶│   Proceso ETL   │───▶│    MongoDB      │
│   (CSV/JSON)    │    │   (Python)      │    │    Atlas        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                                                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Dashboard     │◀───│   Análisis      │◀───│   Consultas     │
│   (Dash/Plotly) │    │   Estadístico   │    │   (PyMongo)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Stack Tecnológico

- **Backend**: Python 3.8+
- **Base de Datos**: MongoDB Atlas (NoSQL)
- **Procesamiento**: Pandas, NumPy
- **Visualización**: Plotly, Dash, Matplotlib, Seaborn
- **Análisis**: Jupyter Notebooks, Scikit-learn
- **Control de Versiones**: Git

---

## 🗄️ Base de Datos

### Estructura de MongoDB

#### Colección: `delitos_municipales`

```javascript
{
  "_id": ObjectId("..."),
  "estado": "Ciudad de México",
  "municipio": "Benito Juárez",
  "clave_municipio": "09003",
  "poblacion": 434153,
  "homicidio_doloso": 15,
  "feminicidio": 3,
  "lesiones_dolosas": 167,
  "robo_casa_habitacion": 123,
  "robo_vehiculo": 201,
  "robo_transeunte": 345,
  "robo_negocio": 89,
  "violacion": 34,
  "secuestro": 2,
  "extorsion": 12,
  "mes": 1,
  "año": 2023,
  "fecha": ISODate("2023-01-01T00:00:00Z"),
  "total_delitos": 991,
  "tasa_delitos_100k": 228.34,
  "categoria_riesgo": "Alto",
  "latitud": 19.4326,
  "longitud": -99.1332
}
```

### Índices Optimizados

```javascript
// Índices para consultas frecuentes
db.delitos_municipales.createIndex({ "estado": 1 })
db.delitos_municipales.createIndex({ "municipio": 1 })
db.delitos_municipales.createIndex({ "fecha": 1 })
db.delitos_municipales.createIndex({ "estado": 1, "municipio": 1 })
db.delitos_municipales.createIndex({ "latitud": 1, "longitud": 1 })
db.delitos_municipales.createIndex({ "tasa_delitos_100k": -1 })
```

### Configuración de Conexión

```python
# config.py
MONGODB_URI = 'mongodb+srv://usuario:password@cluster.mongodb.net/criminalidad_mexico'
DATABASE_NAME = 'criminalidad_mexico'
COLLECTIONS = {
    'delitos': 'delitos_municipales',
    'municipios': 'municipios_info',
    'estados': 'estados_info'
}
```

---

## 🔄 Proceso ETL

### Extracción (Extract)

```python
def extract_data(self):
    """Extrae datos del archivo CSV"""
    df = pd.read_csv(self.raw_data_path, encoding='utf-8')
    return df
```

**Fuentes de datos:**
- Archivos CSV del INEGI
- APIs gubernamentales (opcional)
- Datos históricos de criminalidad

### Transformación (Transform)

```python
def transform_data(self, df):
    """Transforma y limpia los datos"""
    # Limpieza de columnas
    df.columns = df.columns.str.strip().str.lower()
    
    # Conversión de tipos
    numeric_columns = ['poblacion', 'homicidio_doloso', ...]
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Cálculos derivados
    df['total_delitos'] = df[delitos_columns].sum(axis=1)
    df['tasa_delitos_100k'] = (df['total_delitos'] / df['poblacion'] * 100000)
    
    # Categorización de riesgo
    df['categoria_riesgo'] = pd.cut(
        df['tasa_delitos_100k'],
        bins=[0, 1000, 2000, 5000, float('inf')],
        labels=['Bajo', 'Medio', 'Alto', 'Muy Alto']
    )
    
    return df
```

### Carga (Load)

```python
def load_to_mongodb(self, df):
    """Carga datos transformados a MongoDB"""
    records = df.to_dict('records')
    collection = self.db_connection.get_collection('delitos')
    result = collection.insert_many(records)
    return result
```

---

## 🔌 API y Conexiones

### Clase de Conexión MongoDB

```python
class MongoDBConnection:
    def __init__(self):
        self.client = MongoClient(MONGODB_URI)
        self.database = self.client[DATABASE_NAME]
    
    def get_collection(self, collection_name):
        actual_name = COLLECTIONS.get(collection_name, collection_name)
        return self.database[actual_name]
    
    def test_connection(self):
        try:
            self.client.admin.command('ping')
            return True
        except Exception:
            return False
```

### Consultas Especializadas

```python
class CriminalityQueries:
    def get_delitos_by_estado(self, estado):
        """Obtiene delitos por estado"""
        cursor = self.collection.find({'estado': estado})
        return list(cursor)
    
    def get_top_municipios_peligrosos(self, limit=10):
        """Obtiene los municipios más peligrosos"""
        pipeline = [
            {'$sort': {'tasa_delitos_100k': -1}},
            {'$limit': limit}
        ]
        return list(self.collection.aggregate(pipeline))
```

---

## 📊 Dashboard Interactivo

### Arquitectura Dash

```python
app = dash.Dash(__name__)

# Layout principal
app.layout = html.Div([
    # Header
    html.H1("Análisis de Criminalidad en México"),
    
    # Controles
    dcc.Dropdown(id='estado-dropdown'),
    dcc.RadioItems(id='viz-type'),
    
    # Gráficos
    dcc.Graph(id='main-chart'),
    dcc.Graph(id='delitos-pie-chart'),
    
    # Tabla
    html.Div(id='top-municipios-table')
])
```

### Callbacks Interactivos

```python
@app.callback(
    Output('main-chart', 'figure'),
    [Input('estado-dropdown', 'value'),
     Input('viz-type', 'value')]
)
def update_main_chart(selected_estado, viz_type):
    # Filtrar datos
    if selected_estado == 'todos':
        filtered_df = df.copy()
    else:
        filtered_df = df[df['estado'] == selected_estado]
    
    # Crear visualización según tipo
    if viz_type == 'mapa':
        fig = px.scatter_mapbox(...)
    elif viz_type == 'barras':
        fig = px.bar(...)
    else:
        fig = px.scatter(...)
    
    return fig
```

### Tipos de Visualizaciones

1. **Mapa de Calor Geográfico**
   - Scatter plot en mapa con coordenadas
   - Tamaño por total de delitos
   - Color por tasa de criminalidad

2. **Gráficos de Barras**
   - Top municipios por tasa
   - Comparación entre estados
   - Ranking interactivo

3. **Gráficos de Dispersión**
   - Relación población vs delitos
   - Correlaciones entre variables
   - Análisis de tendencias

4. **Gráficos Circulares**
   - Distribución de tipos de delitos
   - Proporciones por categoría
   - Análisis compositivo

---

## 📈 Análisis Estadístico

### Estadísticas Descriptivas

```python
def descriptive_statistics(self):
    """Calcula estadísticas descriptivas"""
    stats_dict = {}
    for col in delitos_cols:
        stats_dict[col] = {
            'total': self.data[col].sum(),
            'promedio': self.data[col].mean(),
            'mediana': self.data[col].median(),
            'desv_std': self.data[col].std(),
            'min': self.data[col].min(),
            'max': self.data[col].max()
        }
    return stats_dict
```

### Análisis de Correlaciones

```python
def correlation_analysis(self):
    """Análisis de correlaciones entre tipos de delitos"""
    correlation_matrix = self.data[delitos_cols].corr()
    
    # Encontrar correlaciones más altas
    correlations = []
    for i in range(len(delitos_cols)):
        for j in range(i+1, len(delitos_cols)):
            corr_value = correlation_matrix.iloc[i, j]
            correlations.append({
                'delito1': delitos_cols[i],
                'delito2': delitos_cols[j],
                'correlacion': corr_value
            })
    
    return sorted(correlations, key=lambda x: abs(x['correlacion']), reverse=True)
```

### Clustering de Municipios

```python
def clustering_analysis(self):
    """Análisis de clustering de municipios"""
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    
    # Preparar datos
    X = self.data[delitos_cols].fillna(0)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Aplicar K-means
    kmeans = KMeans(n_clusters=4, random_state=42)
    clusters = kmeans.fit_predict(X_scaled)
    
    self.data['cluster'] = clusters
    return clusters
```

---

## ⚙️ Instalación y Configuración

### Requisitos del Sistema

- Python 3.8 o superior
- MongoDB Atlas (cuenta gratuita)
- 4GB RAM mínimo
- Conexión a internet

### Instalación Paso a Paso

1. **Clonar el repositorio**
```bash
git clone https://github.com/tu-usuario/analisis-criminalidad-mexico.git
cd analisis-criminalidad-mexico
```

2. **Crear entorno virtual**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
cp .env.example .env
# Editar .env con tus credenciales de MongoDB
```

5. **Ejecutar ETL**
```bash
python src/etl/process_data.py
```

6. **Lanzar dashboard**
```bash
python dashboard/app.py
```

### Configuración de MongoDB Atlas

1. Crear cuenta en [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Crear un cluster gratuito
3. Configurar usuario y contraseña
4. Obtener string de conexión
5. Agregar IP a whitelist
6. Actualizar `MONGODB_URI` en `.env`

---

## 🚀 Uso del Sistema

### Ejecutar Proceso ETL

```bash
# Procesar datos desde CSV
python src/etl/process_data.py

# Verificar conexión a MongoDB
python src/database/mongodb_connection.py

# Ejecutar análisis estadístico
python src/analysis/statistical_analysis.py
```

### Lanzar Dashboard

```bash
# Iniciar servidor Dash
python dashboard/app.py

# Acceder en navegador
http://localhost:8050
```

### Usar Jupyter Notebooks

```bash
# Instalar Jupyter (si no está instalado)
pip install jupyter

# Lanzar Jupyter
jupyter notebook

# Abrir notebooks/analisis_exploratorio.ipynb
```

### Funcionalidades del Dashboard

1. **Filtros Interactivos**
   - Selección por estado
   - Tipo de visualización
   - Rango de fechas (si aplica)

2. **Visualizaciones Dinámicas**
   - Mapas interactivos
   - Gráficos responsivos
   - Tablas ordenables

3. **Exportación de Datos**
   - Descargar gráficos como PNG
   - Exportar datos filtrados
   - Generar reportes

---

## 🔧 Troubleshooting

### Problemas Comunes

#### Error de Conexión a MongoDB

```
ConnectionFailure: No se pudo conectar a MongoDB
```

**Solución:**
1. Verificar string de conexión en `.env`
2. Comprobar conectividad a internet
3. Revisar whitelist de IPs en MongoDB Atlas
4. Validar credenciales de usuario

#### Error al Cargar Datos

```
FileNotFoundError: No such file or directory: 'data/raw/...'
```

**Solución:**
1. Verificar que existan los archivos de datos
2. Comprobar rutas en `config.py`
3. Ejecutar desde directorio raíz del proyecto

#### Error en Dashboard

```
ModuleNotFoundError: No module named 'dash'
```

**Solución:**
1. Activar entorno virtual
2. Reinstalar dependencias: `pip install -r requirements.txt`
3. Verificar versión de Python

#### Problemas de Rendimiento

**Síntomas:**
- Dashboard lento
- Consultas que tardan mucho
- Memoria insuficiente

**Soluciones:**
1. Crear índices en MongoDB
2. Limitar cantidad de datos mostrados
3. Usar paginación en tablas
4. Optimizar consultas agregadas

### Logs y Debugging

```python
# Habilitar logging detallado
import logging
logging.basicConfig(level=logging.DEBUG)

# Verificar estado de conexiones
db = MongoDBConnection()
if db.test_connection():
    print("✅ MongoDB conectado")
else:
    print("❌ Error de conexión")

# Verificar datos cargados
collection = db.get_collection('delitos')
count = collection.count_documents({})
print(f"📊 Documentos en BD: {count}")
```

---

## 📝 Notas de Desarrollo

### Estructura de Archivos

```
proy_final/
├── config.py              # Configuración global
├── requirements.txt       # Dependencias Python
├── .env.example          # Variables de entorno
├── README.md             # Documentación principal
├── data/                 # Datos del proyecto
│   ├── raw/             # Datos originales
│   └── processed/       # Datos procesados
├── src/                  # Código fuente
│   ├── etl/             # Scripts ETL
│   ├── database/        # Conexiones BD
│   └── analysis/        # Análisis estadístico
├── dashboard/           # Aplicación Dash
├── notebooks/           # Jupyter notebooks
└── docs/               # Documentación técnica
```

### Convenciones de Código

- **Nombres de variables**: snake_case
- **Nombres de clases**: PascalCase
- **Nombres de funciones**: snake_case
- **Constantes**: UPPER_CASE
- **Documentación**: Docstrings en español
- **Comentarios**: Explicativos y concisos

### Versionado

- **v1.0.0**: Versión inicial con funcionalidades básicas
- **v1.1.0**: Mejoras en visualizaciones
- **v1.2.0**: Análisis estadístico avanzado
- **v2.0.0**: Dashboard mejorado y nuevas funcionalidades

---

## 🤝 Contribuciones

### Cómo Contribuir

1. Fork del repositorio
2. Crear rama feature: `git checkout -b feature/nueva-funcionalidad`
3. Commit cambios: `git commit -m 'Agregar nueva funcionalidad'`
4. Push a la rama: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

### Estándares de Código

- Seguir PEP 8 para Python
- Documentar funciones y clases
- Incluir tests unitarios
- Actualizar documentación

---

## 📞 Soporte

Para soporte técnico o preguntas:

- **Email**: equipo-analisis@proyecto.com
- **Issues**: GitHub Issues
- **Documentación**: `/docs/`
- **Wiki**: GitHub Wiki

---

*Documentación actualizada: Enero 2024*  
*Versión del proyecto: 1.0.0*
