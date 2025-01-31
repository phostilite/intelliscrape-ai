from django.urls import path, include
from .views import HomeView, JobDetailView, export_job_data

app_name = 'scraper'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('job/<int:job_id>/', JobDetailView.as_view(), name='job_detail'),
    path('job/<int:job_id>/export/', export_job_data, name='export_job_data'),
]
