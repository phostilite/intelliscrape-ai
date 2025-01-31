import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlsplit
from django.utils import timezone
from django.conf import settings
import os
from pathlib import Path
import re
import random
import time
from ..models import ScrapingJob, ScrapedContent, WebsiteEndpoint

class WebScraper:
    # Common user agents list
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59'
    ]
    
    def __init__(self, job_id):
        self.job = ScrapingJob.objects.get(id=job_id)
        self.visited_urls = set()
        
        # Create website-specific storage directory with job ID
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        website_name = self._get_clean_website_name(self.job.url)
        self.storage_path = Path(settings.MEDIA_ROOT) / 'scraped_content' / f"job_{self.job.id}_{website_name}_{timestamp}"
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def start_scraping(self):
        try:
            self.job.status = 'IN_PROGRESS'
            self.job.save()
            
            # Scrape the initial URL
            self._scrape_url(self.job.url)
            
            self.job.status = 'COMPLETED'
            self.job.completed_at = timezone.now()
            self.job.save()
            
        except Exception as e:
            self.job.status = 'FAILED'
            self.job.error_message = str(e)
            self.job.save()
            raise

    def _get_clean_website_name(self, url):
        """Extract and clean website name from URL"""
        parsed = urlparse(url)
        domain = parsed.netloc.replace('www.', '')
        # Remove invalid characters and return clean name
        return re.sub(r'[^\w\-_]', '_', domain)

    def _get_clean_filename(self, url):
        """Generate clean filename from URL"""
        parsed = urlparse(url)
        path = parsed.path.strip('/')
        
        if not path:
            return 'index.html'
            
        # Clean the path to create a valid filename
        filename = re.sub(r'[^\w\-_]', '_', path)
        if not filename.endswith('.html'):
            filename += '.html'
            
        return filename

    def _ensure_unique_filename(self, base_filename):
        """Ensure filename is unique in the storage directory"""
        counter = 1
        filename = base_filename
        while (self.storage_path / filename).exists():
            name, ext = os.path.splitext(base_filename)
            filename = f"{name}_{counter}{ext}"
            counter += 1
        return filename

    def _save_html_file(self, content, job_id, url):
        # Generate filename from URL
        base_filename = self._get_clean_filename(url)
        filename = self._ensure_unique_filename(base_filename)
        file_path = self.storage_path / filename
        
        # Save the HTML content to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(file_path.relative_to(settings.MEDIA_ROOT))

    def _extract_endpoint_name(self, path):
        """Extract a human-readable endpoint name from the URL path"""
        parts = path.strip('/').split('/')
        if parts[-1]:
            name = parts[-1]
        elif len(parts) > 1:
            name = parts[-2]
        else:
            name = 'home'
            
        return name.replace('-', ' ').replace('_', ' ').title()

    def _extract_endpoints(self, soup, base_url):
        """Extract all internal links from the page"""
        base_domain = urlparse(base_url).netloc
        
        for anchor in soup.find_all('a', href=True):
            href = anchor.get('href')
            if not href or href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                continue
                
            # Convert relative URLs to absolute URLs
            absolute_url = urljoin(base_url, href)
            parsed_url = urlparse(absolute_url)
            
            # Only process internal links
            if parsed_url.netloc == base_domain:
                path = parsed_url.path
                if not path:
                    path = '/'
                    
                endpoint_name = self._extract_endpoint_name(path)
                
                # Store the endpoint
                WebsiteEndpoint.objects.get_or_create(
                    job=self.job,
                    url=absolute_url,
                    defaults={
                        'endpoint_name': endpoint_name,
                        'path': path
                    }
                )
                
                # Add to URLs to visit if not already visited
                if absolute_url not in self.visited_urls:
                    self._scrape_url(absolute_url)

    def _scrape_url(self, url):
        if url in self.visited_urls:
            return
            
        self.visited_urls.add(url)
        
        # Add random delay between requests (2-5 seconds)
        time.sleep(random.uniform(2, 5))
        
        try:
            # Use random user agent for each request
            headers = {
                'User-Agent': random.choice(self.USER_AGENTS)
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Check if content is HTML
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' not in content_type:
                return
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract and store endpoints
            self._extract_endpoints(soup, url)
            
            # Save HTML content to file
            file_path = self._save_html_file(response.text, self.job.id, url)
            
            # Store the scraped content
            ScrapedContent.objects.create(
                job=self.job,
                html_content=response.text,
                html_file_path=file_path,
                url=url
            )
            
        except requests.RequestException as e:
            print(f"Error scraping {url}: {str(e)}")