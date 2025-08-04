# 🚀 Guía de Despliegue en Render

## 📋 Preparación Completada

Tu proyecto ya está preparado para Render con los siguientes archivos:

- ✅ `app.py` - Aplicación principal para Render
- ✅ `render.yaml` - Configuración de despliegue
- ✅ `requirements.txt` - Dependencias optimizadas
- ✅ `.gitignore` - Archivos a ignorar

## 🔧 Pasos para Desplegar en Render

### 1. **Subir a GitHub**

```bash
# Inicializar repositorio (si no existe)
git init

# Agregar archivos
git add .

# Commit inicial
git commit -m "Proyecto de análisis de criminalidad listo para Render"

# Conectar con GitHub
git remote add origin https://github.com/tu-usuario/analisis-criminalidad-mexico.git

# Subir código
git push -u origin main
```

### 2. **Crear Servicio en Render**

1. Ve a [render.com](https://render.com) y crea una cuenta
2. Conecta tu cuenta de GitHub
3. Haz clic en "New +" → "Web Service"
4. Selecciona tu repositorio `analisis-criminalidad-mexico`
5. Configura el servicio:

**Configuración Básica:**
- **Name**: `analisis-criminalidad-mexico`
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python app.py`

### 3. **Variables de Entorno**

En la sección "Environment Variables" de Render, agrega:

```
MONGODB_URI = mongodb+srv://23202001:23202001@cluster0.vgypvgq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
DATABASE_NAME = criminalidad_mexico
DASH_DEBUG = False
```

### 4. **Desplegar**

1. Haz clic en "Create Web Service"
2. Render automáticamente:
   - Clonará tu repositorio
   - Instalará las dependencias
   - Ejecutará tu aplicación
3. El proceso toma 2-5 minutos

### 5. **Acceder a tu Aplicación**

Una vez desplegada, Render te dará una URL como:
```
https://analisis-criminalidad-mexico.onrender.com
```

## 🔍 Verificación del Despliegue

### **Logs a Revisar:**
- Build logs: Instalación de dependencias
- Deploy logs: Inicio de la aplicación
- Runtime logs: Funcionamiento en vivo

### **Señales de Éxito:**
```
🔌 Conectando a MongoDB...
📊 Datos cargados: 30 registros
🌐 Iniciando dashboard en http://0.0.0.0:10000
Dash is running on http://0.0.0.0:10000/
```

## 🛠️ Solución de Problemas Comunes

### **Error de Conexión MongoDB:**
- Verifica que `MONGODB_URI` esté correctamente configurada
- Asegúrate de que MongoDB Atlas permita conexiones desde cualquier IP (0.0.0.0/0)

### **Error de Dependencias:**
- Revisa que `requirements.txt` tenga todas las librerías necesarias
- Verifica las versiones de Python compatibles

### **Error de Puerto:**
- Render asigna automáticamente el puerto via variable `PORT`
- El archivo `app.py` ya está configurado para esto

## 📱 Funcionalidades Desplegadas

Una vez en línea, tu dashboard tendrá:

- ✅ **3 Visualizaciones Interactivas**
- ✅ **Conexión en Tiempo Real a MongoDB Atlas**
- ✅ **Datos de 30 Municipios Procesados**
- ✅ **Análisis de Criminalidad Actualizado**
- ✅ **Interfaz Responsiva y Profesional**

## 🎯 Para tu Presentación

**URL del Proyecto Desplegado:**
```
https://analisis-criminalidad-mexico.onrender.com
```

**Demostración:**
1. Abre la URL en el navegador
2. Muestra las 3 visualizaciones interactivas
3. Explica que está conectado a MongoDB Atlas en tiempo real
4. Destaca los hallazgos clave (Irapuato, Acapulco más peligrosos)

## 🏆 Ventajas del Despliegue

- ✅ **Acceso Global**: Cualquiera puede ver tu proyecto
- ✅ **Profesional**: URL propia para tu portafolio
- ✅ **Tiempo Real**: Datos actualizados desde MongoDB
- ✅ **Escalable**: Render maneja el tráfico automáticamente
- ✅ **Gratuito**: Plan gratuito suficiente para presentaciones

**¡Tu proyecto estará disponible 24/7 en internet!** 🌐🚀
