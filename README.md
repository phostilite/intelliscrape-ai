# IntelliScrape AI

IntelliScrape AI is a web application built with Django that provides intelligent web scraping capabilities. It allows users to scrape websites, discover endpoints, and store the scraped content for later analysis.

## Features

- Website crawling and content scraping
- Automatic endpoint discovery
- HTML content storage and preview
- Job status tracking
- Paginated results view
- Modern UI with Tailwind CSS

## Requirements

- Python 3.8+
- Django 3.2+
- BeautifulSoup4
- Requests
- Tailwind CSS

## Installation

1. Clone the repository:
```bash
git clone <https://github.com/phostilite/intelliscrape-ai>
cd intelliscrape
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Apply migrations:
```bash
python manage.py migrate
```

5. Create a superuser (optional):
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

## Usage

1. Access the application at `http://localhost:8000`
2. Enter a website URL in the form
3. Click "Start Scraping" to begin the scraping process
4. View the results in the job detail page, which includes:
   - Job status and details
   - Discovered endpoints
   - Scraped content with HTML previews
   - Download options for full HTML content

## Project Structure

```
intelliscrape/
├── scraper/
│   ├── services/
│   │   └── scraper_service.py    # Core scraping functionality
│   ├── templates/
│   │   └── scraper/
│   │       ├── index.html        # Home page template
│   │       └── results.html      # Results page template
│   ├── models.py                 # Database models
│   ├── views.py                  # View controllers
│   └── urls.py                   # URL routing
└── manage.py
```

## Models

- `ScrapingJob`: Tracks scraping jobs and their status
- `ScrapedContent`: Stores scraped HTML content and metadata
- `WebsiteEndpoint`: Records discovered website endpoints

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License
