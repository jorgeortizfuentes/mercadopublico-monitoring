import os
from dotenv import load_dotenv

# If .env file exists, load environment variables from it
if os.path.exists('.env'):
    load_dotenv()

# API Configuration
API_BASE_URL = "https://api.mercadopublico.cl/servicios/v1/publico/licitaciones.json"
API_TICKET = os.getenv('TICKET_KEY')

# Database Configuration
DATABASE_URL = os.getenv('DATABASE_URL')

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
