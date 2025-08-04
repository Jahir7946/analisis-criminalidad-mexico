# Análisis de Criminalidad en México usando MongoDB, Dash y datos del INEGI

## 📊 Descripción del Proyecto

Este proyecto analiza los datos de criminalidad en municipios de México utilizando tecnologías NoSQL (MongoDB), procesamiento de datos con Python (Pandas) y visualización interactiva con Dash y Plotly. El objetivo es identificar patrones, tendencias y correlaciones en los índices delictivos para apoyar la toma de decisiones en políticas públicas de seguridad.

## 🎯 Objetivos

### Objetivo General
Desarrollar un sistema de análisis de datos de criminalidad que permita visualizar tendencias, patrones geográficos y temporales de delitos en México, utilizando bases de datos NoSQL y herramientas de visualización interactiva.

### Objetivos Específicos
- Extraer y procesar datos de criminalidad del INEGI/SNSP
- Implementar un pipeline ETL para limpieza y normalización de datos
- Almacenar información en MongoDB Atlas con estructura optimizada
- Crear dashboards interactivos con Python (Dash, Plotly)
- Generar análisis estadísticos de tendencias delictivas
- Desplegar la aplicación para acceso web

## 🔍 Justificación del Problema

La criminalidad es uno de los principales problemas sociales en México. El análisis de datos delictivos permite:
- Identificar zonas de alto riesgo
- Detectar patrones temporales de delitos
- Apoyar la asignación eficiente de recursos policiales
- Informar políticas públicas basadas en evidencia
- Mejorar la seguridad ciudadana mediante análisis predictivo

## 📚 Marco Conceptual

### Bases de Datos NoSQL
MongoDB permite almacenar datos semi-estructurados con flexibilidad para diferentes tipos de registros delictivos, escalabilidad horizontal y consultas complejas sobre datos geoespaciales.

### Servicios en la Nube
MongoDB Atlas proporciona infraestructura escalable, respaldos automáticos y acceso global para el análisis de grandes volúmenes de datos.

### Proceso ETL
- **Extracción**: Obtención de datos CSV/JSON del INEGI
- **Transformación**: Limpieza, normalización y enriquecimiento
- **Carga**: Inserción estructurada en MongoDB

### Datasets Abiertos
Utilización de datos gubernamentales del INEGI y SNSP que garantizan calidad, actualización y representatividad nacional.

### Librerías de Visualización
- **Plotly**: Gráficos interactivos y mapas geoespaciales
- **Dash**: Aplicaciones web interactivas
- **Pandas**: Manipulación y análisis de datos

## 🛠️ Tecnologías y Herramientas

- **Base de Datos**: MongoDB Atlas
- **Procesamiento**: Python, Pandas, NumPy
- **Visualización**: Plotly, Dash, Matplotlib
- **Desarrollo**: Jupyter Notebooks, VS Code
- **Control de Versiones**: Git, GitHub
- **Despliegue**: Render/Heroku (opcional)
- **Datos**: INEGI, SNSP

## 📁 Estructura del Proyecto

```
proy_final/
├── data/                   # Datos CSV/JSON
├── src/                    # Código fuente
│   ├── etl/               # Scripts ETL
│   ├── database/          # Conexión MongoDB
│   └── analysis/          # Análisis estadístico
├── dashboard/             # Aplicación Dash
├── notebooks/             # Jupyter notebooks
├── docs/                  # Documentación
├── requirements.txt       # Dependencias
└── README.md             # Este archivo
```

## 🚀 Instalación y Uso

1. **Clonar el repositorio**
```bash
git clone https://github.com/tu-usuario/analisis-criminalidad-mexico.git
cd analisis-criminalidad-mexico
```

2. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

3. **Configurar MongoDB**
- Crear cuenta en MongoDB Atlas
- Configurar string de conexión en `config.py`

4. **Ejecutar ETL**
```bash
python src/etl/process_data.py
```

5. **Lanzar dashboard**
```bash
python dashboard.py
```

O usando el script principal:
```bash
python main.py dashboard
```

## 👥 Equipo de Desarrollo

- **Integrante 1**: Análisis de datos y ETL
- **Integrante 2**: Base de datos y backend
- **Integrante 3**: Visualización y dashboard
- **Integrante 4**: Documentación y testing

## 📈 Resultados Esperados

- Dashboard interactivo con mapas de calor de criminalidad
- Análisis temporal de tendencias delictivas
- Comparativas entre estados y municipios
- Correlaciones entre tipos de delitos
- Predicciones básicas de riesgo

## 🔗 Enlaces

- [Dashboard en vivo](#) (Pendiente despliegue)
- [Notebooks de análisis](./notebooks/)
- [Documentación técnica](./docs/)

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.
