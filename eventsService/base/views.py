from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods
from django.conf import settings
from .models import Event
from datetime import datetime
import json
# import requests


# Render a simple HTML page listing all events
def events_list(request):
    events = Event.objects.all().order_by('event_start_date')
    return render(request, 'base/events_list.html', {'events': events})


# Render a detail page for a single event
def event_detail(request, eventID):
    event = get_object_or_404(Event, eventID=eventID)
    return render(request, 'base/event_detail.html', {'event': event})


@require_http_methods(["GET", "POST"])
def external_event_form(request):
    """
    Handle event form submission to external API service.
    GET: Display the form
    POST: Submit to external API
    """
    # Configuration for external API
    EXTERNAL_API_BASE_URL = "https://api.example.com/v1"  # Replace with actual API URL
    API_KEY = "your_api_key_here"  # Better to get from settings.py or environment variables
    
    if request.method == "POST":
        try:
            # Parse form data similar to our local implementation
            form_data = {
                'title': request.POST.get('title'),
                'description': request.POST.get('description'),
                'creator': request.POST.get('creator'),
                'eventType': request.POST.get('eventType'),
                'location': request.POST.get('location'),
                'capacity': int(request.POST.get('capacity', 0)),
                'link': request.POST.get('link') or None,
                'zoom_link': request.POST.get('zoom_link') or None,
                'hosted_by': request.POST.get('hosted_by'),
                'event_start_date': request.POST.get('event_start_date'),
                'event_end_date': request.POST.get('event_end_date'),
            }

            # Handle registered_students
            students_raw = request.POST.get('registered_students', '')
            if students_raw:
                form_data['registered_students'] = [
                    int(s.strip()) if s.strip().isdigit() else s.strip()
                    for s in students_raw.split(',')
                    if s.strip()
                ]
            else:
                form_data['registered_students'] = []

            # Headers for the external API
            headers = {
                'Authorization': f'Bearer {API_KEY}',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }

            # First, create the event using POST
            create_response = requests.post(
                f"{EXTERNAL_API_BASE_URL}/events",
                json=form_data,
                headers=headers
            )
            create_response.raise_for_status()  # Raise exception for 4XX/5XX status codes
            
            created_event = create_response.json()
            event_id = created_event.get('eventID')

            # If we need to update additional fields, we can use PUT
            if event_id and request.POST.get('additional_field'):
                update_data = {
                    'additional_field': request.POST.get('additional_field')
                }
                
                update_response = requests.put(
                    f"{EXTERNAL_API_BASE_URL}/events/{event_id}",
                    json=update_data,
                    headers=headers
                )
                update_response.raise_for_status()
                created_event = update_response.json()

            # Handle HTMX request
            if request.headers.get('HX-Request'):
                return HttpResponse(
                    render_to_string('base/partials/event_created.html',
                                   {'event': created_event}),
                    content_type='text/html'
                )

            # Handle regular form submission
            return JsonResponse(created_event)

        except requests.RequestException as e:
            error_message = f"API Error: {str(e)}"
            if hasattr(e.response, 'json'):
                try:
                    error_detail = e.response.json()
                    error_message = error_detail.get('detail', error_message)
                except ValueError:
                    pass

            if request.headers.get('HX-Request'):
                return HttpResponse(
                    render_to_string('base/partials/form_error.html',
                                   {'error': error_message}),
                    status=400,
                    content_type='text/html'
                )
            return JsonResponse({'error': error_message}, status=400)

        except ValueError as e:
            error_message = f"Validation error: {str(e)}"
            if request.headers.get('HX-Request'):
                return HttpResponse(
                    render_to_string('base/partials/form_error.html',
                                   {'error': error_message}),
                    status=400,
                    content_type='text/html'
                )
            return JsonResponse({'error': error_message}, status=400)

    # GET request - show the form
    return render(request, 'base/form.html')


@require_http_methods(["GET", "POST"])
def event_form(request):
    """Handle both form display and submission"""
    if request.method == "POST":
        try:
            # Parse form data
            data = {
                'title': request.POST.get('title'),
                'description': request.POST.get('description'),
                'creator': request.POST.get('creator'),
                'eventType': request.POST.get('eventType'),
                'location': request.POST.get('location'),
                'capacity': int(request.POST.get('capacity', 0)),
                'link': request.POST.get('link') or None,
                'zoom_link': request.POST.get('zoom_link') or None,
                'hosted_by': request.POST.get('hosted_by'),
                'event_start_date': datetime.fromisoformat(request.POST.get('event_start_date')),
                'event_end_date': datetime.fromisoformat(request.POST.get('event_end_date')),
            }

            # Handle registered_students as comma-separated list
            students_raw = request.POST.get('registered_students', '')
            if students_raw:
                data['registered_students'] = [
                    int(s.strip()) if s.strip().isdigit() else s.strip()
                    for s in students_raw.split(',')
                    if s.strip()
                ]
            else:
                data['registered_students'] = []

            # Create the event
            event = Event.objects.create(**data)

            # If this is an HTMX request, return a partial template
            if request.headers.get('HX-Request'):
                return HttpResponse(
                    render_to_string('base/partials/event_created.html', 
                                   {'event': event}),
                    content_type='text/html'
                )
            # For regular requests, redirect to the event detail page
            return redirect('base:event_detail', eventID=event.eventID)

        except Exception as e:
            error_message = str(e)
            if request.headers.get('HX-Request'):
                return HttpResponse(
                    render_to_string('base/partials/form_error.html',
                                   {'error': error_message}),
                    status=400,
                    content_type='text/html'
                )
            # For regular requests, re-render the form with errors
            return render(request, 'base/form.html',
                        {'error': error_message}, status=400)

    # GET request - just show the form
    return render(request, 'base/form.html')