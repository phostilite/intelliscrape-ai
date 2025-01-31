from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView
from django.contrib import messages
from django.http import HttpResponse
from .models import ScrapingJob, ScrapedContent
from .services.scraper_service import WebScraper
from .services.excel_exporter import ExcelExporter

class HomeView(TemplateView):
    template_name = 'scraper/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recent_jobs'] = ScrapingJob.objects.order_by('-created_at')[:10]
        return context

    def post(self, request, *args, **kwargs):
        url = request.POST.get('url')
        if url:
            try:
                # Create a new scraping job
                job = ScrapingJob.objects.create(url=url)
                
                # Start the scraping process
                scraper = WebScraper(job.id)
                scraper.start_scraping()
                
                messages.success(request, 'Scraping job started successfully!')
                return redirect('scraper:job_detail', job_id=job.id)
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
        return self.render_to_response(self.get_context_data())

class JobDetailView(ListView):
    template_name = 'scraper/results.html'
    context_object_name = 'scraped_contents'
    paginate_by = 10

    def get_queryset(self):
        self.job = ScrapingJob.objects.get(id=self.kwargs['job_id'])
        return ScrapedContent.objects.filter(job=self.job).order_by('-scraped_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['job'] = self.job
        return context

def export_job_data(request, job_id):
    try:
        exporter = ExcelExporter(job_id)
        excel_file = exporter.export()
        
        response = HttpResponse(
            excel_file.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename=scraping_job_{job_id}.xlsx'
        return response
    except Exception as e:
        messages.error(request, f'Error exporting data: {str(e)}')
        return redirect('scraper:job_detail', job_id=job_id)