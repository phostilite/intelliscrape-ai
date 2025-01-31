# views.py
import logging
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import HttpResponseServerError
import requests
from requests.exceptions import RequestException
from .models import Person, Profile, SearchHistory, Source
from .forms import PersonSearchForm
import json
import time
from django.http import HttpResponse
from .utils import (
    calculate_name_match_score,
    calculate_description_match_score,
    calculate_content_relevance_score,
    calculate_overall_score
)

# Configure logging
logger = logging.getLogger(__name__)

class PersonListView(ListView):
    model = Person
    template_name = 'profiles/person_list.html'
    context_object_name = 'persons'
    ordering = ['-created_at']
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        # Add search functionality
        search_term = self.request.GET.get('search', '')
        if search_term:
            queryset = queryset.filter(name__icontains=search_term)
        return queryset.prefetch_related('profiles', 'searchhistory_set')

class PersonDetailView(DetailView):
    model = Person
    template_name = 'profiles/person_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add additional context data
        context['search_history'] = self.object.searchhistory_set.all().order_by('-timestamp')
        context['profiles'] = self.object.profiles.all().order_by('-last_updated')
        return context

class SearchException(Exception):
    """Custom exception for search-related errors"""
    pass

def search_person(request):
    try:
        if request.method == 'POST':
            return handle_search_post(request)
        return handle_search_get(request)
    except SearchException as e:
        logger.error(f"Search error: {str(e)}")
        messages.error(request, f"Search failed: {str(e)}")
        return redirect('search-person')
    except Exception as e:
        logger.exception("Unexpected error in search_person view")
        messages.error(request, "An unexpected error occurred. Please try again later.")
        return HttpResponseServerError("Internal Server Error")

def handle_search_post(request) -> HttpResponse:
    form = PersonSearchForm(request.POST)
    if not form.is_valid():
        logger.warning(f"Invalid form submission: {form.errors}")
        return render(request, 'profiles/search.html', {'form': form})

    name = form.cleaned_data['name']
    description = form.cleaned_data['description']
    source = form.cleaned_data['source']

    try:
        with transaction.atomic():
            person, search_results = process_search(name, description, source)
            if not search_results:
                messages.warning(request, "No results found. Try modifying your search terms.")
            else:
                messages.success(request, f"Found {len(search_results)} results for {name}")
            return redirect('person-detail', pk=person.pk)
    except ValidationError as e:
        logger.error(f"Validation error during search: {str(e)}")
        messages.error(request, str(e))
        return render(request, 'profiles/search.html', {'form': form})

def handle_search_get(request) -> HttpResponse:
    form = PersonSearchForm()
    return render(request, 'profiles/search.html', {'form': form})

def process_search(name: str, description: str, source: Optional[str] = None) -> Tuple[Person, List[Dict]]:
    """Process the search request and return person and results"""
    # Create or get person
    person, created = Person.objects.get_or_create(
        name=name,
        defaults={'description': description}
    )
    
    if not created and description:
        person.description = description
        person.save()

    # Prepare search query
    search_query = f"{name} {description}".strip()
    if source:
        search_query = f"{search_query} site:{get_source_domain(source)}"
    
    start_time = time.time()
    
    try:
        results = perform_google_search(search_query)
        search_duration = time.time() - start_time
        
        # Log search metrics
        logger.info(f"Search completed for '{search_query}' in {search_duration:.2f}s with {len(results)} results")
        
        # Save search history
        search_history = SearchHistory.objects.create(
            person=person,
            query=search_query,
            results_count=len(results)
        )
        
        # Process and save results
        processed_results = process_search_results(person, results, search_query)
        return person, processed_results
        
    except Exception as e:
        logger.exception(f"Error during search processing for query '{search_query}'")
        raise SearchException(f"Failed to process search: {str(e)}")

def get_source_domain(source: str) -> str:
    """Convert source name to domain for search query"""
    if not source:
        return ''
    try:
        return Source.objects.get(name=source).domain
    except Source.DoesNotExist:
        logger.warning(f"Source not found: {source}")
        return ''

def perform_google_search(query: str) -> List[Dict]:
    """Perform Google Custom Search with error handling and rate limiting"""
    base_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'key': settings.GOOGLE_API_KEY,
        'cx': settings.GOOGLE_CSE_ID,
        'q': query,
        'num': 10  # Number of results per request
    }
    
    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Log API response metrics
        logger.info(f"API Request successful: {response.status_code}, Query: '{query}'")
        
        if 'error' in data:
            logger.error(f"API Error: {data['error']}")
            raise SearchException(f"Search API error: {data['error'].get('message', 'Unknown error')}")
            
        return data.get('items', [])
        
    except RequestException as e:
        logger.error(f"Request failed: {str(e)}")
        raise SearchException(f"Failed to connect to search service: {str(e)}")
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse API response: {str(e)}")
        raise SearchException("Invalid response from search service")
    except Exception as e:
        logger.exception("Unexpected error in perform_google_search")
        raise SearchException(f"Search failed: {str(e)}")

def process_search_results(person: Person, results: List[Dict], search_query: str) -> List[Dict]:
    """Process and save search results with enhanced scoring"""
    processed_results = []
    
    for result in results:
        try:
            url = result.get('link', '')
            domain = extract_domain(url)
            source_type = categorize_source(domain)
            
            # Calculate match scores
            result_text = f"{result.get('title', '')} {result.get('snippet', '')}"
            name_score = calculate_name_match_score(person.name, result_text)
            desc_score = calculate_description_match_score(person.description, result_text)
            content_score = calculate_content_relevance_score(result, source_type)
            overall_score = calculate_overall_score(name_score, desc_score, content_score)
            
            # Only process results with minimum relevance
            if overall_score < 0.2:  # Adjust threshold as needed
                logger.info(f"Skipping low-relevance result: {url} (score: {overall_score})")
                continue
            
            # Create or update profile with scores
            profile, created = Profile.objects.update_or_create(
                person=person,
                url=url,
                defaults={
                    'source': source_type,
                    'title': result.get('title', ''),
                    'snippet': result.get('snippet', ''),
                    'search_query': search_query,
                    'name_match_score': name_score,
                    'description_match_score': desc_score,
                    'content_relevance_score': content_score,
                    'overall_score': overall_score
                }
            )
            
            # Log profile creation/update with score
            action = "Created" if created else "Updated"
            logger.info(f"{action} profile for {person.name}: {url} (score: {overall_score})")
            
            processed_results.append(result)
            
        except Exception as e:
            logger.error(f"Error processing result: {str(e)}, Result: {result}")
            continue
    
    return processed_results

def extract_domain(url: str) -> str:
    """Extract and normalize domain from URL"""
    try:
        parsed = urlparse(url)
        return parsed.netloc.lower()
    except Exception:
        return "unknown"

def categorize_source(domain: str) -> str:
    """Categorize the source based on domain"""
    try:
        source = Source.objects.filter(domain__icontains=domain).first()
        return source.name if source else domain
    except Exception as e:
        logger.error(f"Error categorizing source for domain {domain}: {str(e)}")
        return domain