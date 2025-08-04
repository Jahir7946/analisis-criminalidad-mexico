"""
Aplicación principal para despliegue en Render
"""

import os
import sys
from dashboard import app

# Exponer el servidor para Gunicorn
server = app.server

# Configurar el puerto para Render
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8050))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False
    )
