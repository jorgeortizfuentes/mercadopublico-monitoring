# Mercado Público Monitor

A monitoring system for Chilean public tenders that automatically tracks and filters opportunities based on keywords.

## Features

- 🔍 Automatic tender monitoring
- 🎯 Keyword-based filtering (include/exclude)
- 📊 Web interface for tender management
- 📝 Detailed tender information
- 🔄 Real-time updates
- 📱 Responsive design
- 🐳 Docker support
- 📋 Export capabilities

## Requirements

- Python 3.12+
- Docker (optional)
- Mercado Público API key

## Installation

### Local Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/mercadopublico-monitor.git
cd mercadopublico-monitor
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create .env file:

```bash
TICKET_KEY=your_api_key
DATABASE_URL=sqlite:///db.sqlite3
LOG_LEVEL=INFO
```

### Docker Installation

1. Build the image:

```bash
docker-compose build
```

2. Start the container:

```bash
docker-compose up -d
```

## Configuration

### Environment Variables

| Variable     | Description             | Default              |
| ------------ | ----------------------- | -------------------- |
| TICKET_KEY   | Mercado Público API key | Required             |
| DATABASE_URL | Database connection URL | sqlite:///db.sqlite3 |
| LOG_LEVEL    | Logging level           | INFO                 |
| PORT         | Application port        | 5353                 |
| WORKERS      | Number of workers       | auto                 |

### Keywords Configuration

1. Access the settings page at `/settings`
2. Add include/exclude keywords
3. Keywords are used to filter relevant tenders

## Usage

1. Start the application:

```bash
python run.py
```

2. Access the web interface at `http://localhost:5353`
3. Configure your keywords in the Settings section
4. Use the Execute section to start a tender search
5. View results in the Tenders section

## API Documentation

### Endpoints

- `GET /api/tenders`: List all tenders
- `GET /api/keywords`: List all keywords
- `POST /api/keywords`: Create new keyword
- `PUT /api/keywords/{id}`: Update keyword
- `DELETE /api/keywords/{id}`: Delete keyword
- `POST /api/execute`: Execute tender search

For detailed API documentation, visit `/docs` when the application is running.

## Development

### Project Structure

```javascript
.
├── app/                # Web application
│   ├── api/           # API endpoints
│   ├── static/        # Static files
│   └── templates/     # HTML templates
├── src/               # Core functionality
│   ├── api/           # API client
│   ├── database/      # Database models
│   ├── models/        # Data models
│   └── utils/         # Utilities
```

## Docker Usage

### Build and Run

```bash
# Build image
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Environment Configuration

Create a `.env` file in the project root:

```env
TICKET_KEY=your_api_key
DATABASE_URL=sqlite:///db.sqlite3
LOG_LEVEL=INFO
BUILD_ENV=production
WORKERS=auto
TZ=America/Santiago
PORT=5353
UVICORN_TIMEOUT=300
UVICORN_BACKLOG=2048
UVICORN_LIMIT_CONCURRENCY=1000
UVICORN_KEEP_ALIVE=5
CPU_LIMIT=2
MEMORY_LIMIT=2G
CPU_RESERVATION=0.5
MEMORY_RESERVATION=512M
TAG=latest

```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
