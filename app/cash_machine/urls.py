from django.urls import path

from .views import cash_machine, return_pdf

urlpatterns = [
    path('api/cash_machine/', cash_machine, name='cash_machine'),
    path('media/<path:filepath>/', return_pdf, name='return_pdf'),
]
