
from django.urls import path
from .views import customer_contacts, identify_contact

urlpatterns = [
    path('customer/<int:customer_id>/contacts/', customer_contacts, name='customer_contacts'),
    path('identify/', identify_contact, name='identify_contact'),
    # Add other URLs as needed
]
