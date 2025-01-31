# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.PersonListView.as_view(), name='person-list'),
    path('person/<int:pk>/', views.PersonDetailView.as_view(), name='person-detail'),
    path('search/', views.search_person, name='search-person'),
]