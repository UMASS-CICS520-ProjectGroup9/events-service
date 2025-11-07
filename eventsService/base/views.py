from django.shortcuts import render, get_object_or_404
from .models import Event


# Render a simple HTML page listing all events
def events_list(request):
	events = Event.objects.all().order_by('event_start_date')
	return render(request, 'base/events_list.html', {'events': events})


# Render a detail page for a single event
def event_detail(request, eventID):
	event = get_object_or_404(Event, eventID=eventID)
	return render(request, 'base/event_detail.html', {'event': event})
