# urls.py
from django.urls import path
from .views import paste_data
from django.views.generic import TemplateView
from .views import upload_excel, ConfirmationView
from . import views

app_name = 'ex_upload'  # Add this line to define the app namespace

urlpatterns = [
    path('', TemplateView.as_view(template_name='ex_upload/h.html'), name='home'),
    path('paste/', paste_data, name='paste_data'),
    path('upload/', views.upload_excel.as_view(), name='upload'),
    path('confirmation/', views.ConfirmationView.as_view(), name='confirmation'),
    path('input/', views.input_feedbackView.as_view(), name='input'),
    path('delete/', views.DeleteView.as_view(), name='delete'),
]
