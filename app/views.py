# views.py

from django.shortcuts import render, get_object_or_404
from .models import Contact
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json




def customer_contacts(request, customer_id):
    # Retrieve the primary contact for the customer
    primary_contact = get_object_or_404(Contact, id=customer_id, linkPrecedence='primary')

    # Retrieve all secondary contacts linked to the primary contact
    secondary_contacts = Contact.objects.filter(linkedId=primary_contact)

    return render(request, 'customer_contacts.html', {'primary_contact': primary_contact, 'secondary_contacts': secondary_contacts})

@csrf_exempt
def identify_contact(request):
    if request.method == 'POST':
        try:
            # Parse JSON from the request body
            data = json.loads(request.body)

            # Retrieve or create the primary contact based on email or phoneNumber
            primary_contact = None
            if 'email' in data:
                primary_contact = Contact.objects.filter(email=data['email'], linkPrecedence='primary').first()
            elif 'phoneNumber' in data:
                primary_contact = Contact.objects.filter(phoneNumber=data['phoneNumber'], linkPrecedence='primary').first()

            # If no primary contact exists, create a new one
            if not primary_contact:
                primary_contact = Contact.objects.create(
                    email=data.get('email'),
                    phoneNumber=data.get('phoneNumber'),
                    linkPrecedence='primary'
                )

            # Check for new information and update the primary contact to secondary if needed
            if primary_contact and (
                    (data.get('email') and data['email'] != primary_contact.email) or
                    (data.get('phoneNumber') and data['phoneNumber'] != primary_contact.phoneNumber)
            ):
                # Change the linkPrecedence of the existing primary contact to secondary
                primary_contact.linkPrecedence = 'secondary'
                primary_contact.save()

                # Create a new secondary contact
                secondary_contact = Contact.objects.create(
                    email=data.get('email'),
                    phoneNumber=data.get('phoneNumber'),
                    linkedId=primary_contact,
                    linkPrecedence='secondary'
                )

            # Get all secondary contacts linked to the primary contact
            secondary_contacts = Contact.objects.filter(linkedId=primary_contact)

            # Consolidate contact information
            consolidated_contact = {
                "primaryContactId": primary_contact.id,
                "emails": [contact.email for contact in [primary_contact] + list(secondary_contacts)],
                "phoneNumbers": [contact.phoneNumber for contact in [primary_contact] + list(secondary_contacts)],
                "secondaryContactIds": [contact.id for contact in secondary_contacts]
            }

            response_data = {"contact": consolidated_contact}
            return JsonResponse(response_data, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format in the request body"}, status=400)

    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)
