from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('generate_frames/', views.generate_frames, name='generate_video'),
]
