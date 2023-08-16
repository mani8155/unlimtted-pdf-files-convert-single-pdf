from django.urls import path
from . import views

urlpatterns = [
    path("", views.merge_pdfs, name="merge_pdfs"),
    path("get_pdf/", views.get_pdf, name="get-pdfs"),
    path('download_merged_pdf/', views.download_merged_pdf, name='download_merged_pdf'),

    path('clear/', views.clearTable, name='clear'),
]

