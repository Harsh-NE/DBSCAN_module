from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('generate_frames/', views.generate_frames, name='generate_video'),
]
