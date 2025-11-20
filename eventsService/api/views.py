from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions, status
from rest_framework.exceptions import PermissionDenied
from django.db import models
from base.models import Event
from .serializers import EventSerializer
from .permissions import IsAdmin, IsStudent, IsStaff, IsOwnerOrAdmin

@api_view(['GET'])
def getEvents(request):
    events = Event.objects.all().order_by('event_end_date')
    serializer = EventSerializer(events, many=True)
    return Response(serializer.data)


@api_view(['GET'])
# @permission_classes([permissions.AllowAny])
def getEvent(request, eventID):
    try:
        event = Event.objects.get(eventID=eventID)
    except Event.DoesNotExist:
        return Response({'error': 'Event not found'}, status=404)
    
    serializer = EventSerializer(event)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsStudent])
def createEvent(request):
    serializer = EventSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(creator_id=request.user.id)
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@api_view(['PUT'])
@permission_classes([IsStudent])
def updateEvent(request, eventID):
    try:
        event = Event.objects.get(eventID=eventID)
        perm = IsOwnerOrAdmin()
        if not perm.has_object_permission(request, view=updateEvent, obj=event):
            raise PermissionDenied("You are not allowed to access this event.")
    except PermissionDenied :
        return Response({"Update": "Not allow"}, status=status.HTTP_404_NOT_FOUND)
    except Event.DoesNotExist:
        return Response({'error': 'Event not found'}, status=404)
    
    serializer = EventSerializer(event, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)

@api_view(['DELETE'])
@permission_classes([IsStudent])
def deleteEvent(request, eventID):
    print("eventid: ", eventID)
    try:
        event = Event.objects.get(eventID=eventID)
        perm = IsOwnerOrAdmin()
        if not perm.has_object_permission(request, view=deleteEvent, obj=event):
            raise PermissionDenied("You are not allowed to access this event.")
    except PermissionDenied :
        return Response({"Delete": "Not allow"}, status=status.HTTP_404_NOT_FOUND)
    except Event.DoesNotExist:
        return Response({'error': 'Event not found'}, status=404)
    
    event.delete()
    return Response(status=204)

@api_view(['POST'])
@permission_classes([IsStudent])
def registerStudent(request, eventID):
    try:
        event = Event.objects.get(eventID=eventID)
    except Event.DoesNotExist:
        return Response({'error': 'Event not found'}, status=404)
    
    student_id = request.data.get('student_id')
    if not student_id:
        return Response({'error': 'Student ID is required'}, status=400)
    
    if student_id in event.registered_students:
        return Response({'error': 'Student already registered'}, status=400)
    
    event.registered_students.append(student_id)
    event.save()
    
    serializer = EventSerializer(event)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsStudent])
def unregisterStudent(request, eventID):
    try:
        event = Event.objects.get(eventID=eventID)
    except Event.DoesNotExist:
        return Response({'error': 'Event not found'}, status=404)
    
    student_id = request.data.get('student_id')
    if not student_id:
        return Response({'error': 'Student ID is required'}, status=400)
    
    if student_id not in event.registered_students:
        return Response({'error': 'Student not registered'}, status=400)
    
    event.registered_students.remove(student_id)
    event.save()
    
    serializer = EventSerializer(event)
    return Response(serializer.data)

@api_view(['GET'])
def getRegisteredStudents(request, eventID):
    try:
        event = Event.objects.get(eventID=eventID)
    except Event.DoesNotExist:
        return Response({'error': 'Event not found'}, status=404)
    
    return Response({'registered_students': event.registered_students})

@api_view(['GET'])
def getEventsByCreator(request, creator):
    events = Event.objects.filter(creator=creator)
    serializer = EventSerializer(events, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getEventsByType(request, eventType):
    events = Event.objects.filter(eventType=eventType)
    serializer = EventSerializer(events, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getEventsByDateRange(request):
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    
    if not start_date or not end_date:
        return Response({'error': 'Start date and end date are required'}, status=400)
    
    events = Event.objects.filter(event_start_date__gte=start_date, event_end_date__lte=end_date)
    serializer = EventSerializer(events, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def healthCheck(request):
    return Response({'status': 'API is running'}) 

@api_view(['GET'])
def apiInfo(request):
    info = {
        'name': 'Events Service API',
        'version': '1.0',
        'description': 'API for managing events, including creation, retrieval, updating, deletion, and student registrations.'
    }
    return Response(info)

@api_view(['GET'])
def getEventCount(request):
    count = Event.objects.count()
    return Response({'event_count': count})

@api_view(['GET'])
def getUpcomingEvents(request):
    from django.utils import timezone
    now = timezone.now()
    events = Event.objects.filter(event_start_date__gte=now).order_by('event_start_date')
    serializer = EventSerializer(events, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getPastEvents(request):
    from django.utils import timezone
    now = timezone.now()
    events = Event.objects.filter(event_end_date__lt=now).order_by('-event_end_date')
    serializer = EventSerializer(events, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getEventsByLocation(request, location):
    events = Event.objects.filter(location__icontains=location)
    serializer = EventSerializer(events, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getEventsByCapacity(request, min_capacity):
    events = Event.objects.filter(capacity__gte=min_capacity)
    serializer = EventSerializer(events, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getRecentEvents(request, days):
    from django.utils import timezone
    from datetime import timedelta
    now = timezone.now()
    past_date = now - timedelta(days=days)
    events = Event.objects.filter(created_at__gte=past_date).order_by('-created_at')
    serializer = EventSerializer(events, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getEventsByHost(request, host):
    events = Event.objects.filter(hosted_by__icontains=host)
    serializer = EventSerializer(events, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getEventsWithLinks(request):
    events = Event.objects.exclude(link__isnull=True).exclude(link__exact='')
    serializer = EventSerializer(events, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getEventsWithZoomLinks(request):
    events = Event.objects.exclude(zoom_link__isnull=True).exclude(zoom_link__exact='')
    serializer = EventSerializer(events, many=True)
    return Response(serializer.data)        

@api_view(['GET'])
def getEventsByKeyword(request):
    keyword = request.query_params.get('keyword')
    if not keyword:
        return Response({'error': 'Keyword is required'}, status=400)
    
    events = Event.objects.filter(models.Q(title__icontains=keyword) | models.Q(description__icontains=keyword))
    serializer = EventSerializer(events, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getFullEvents(request): 
    events = Event.objects.filter(registered_students__length=models.F('capacity'))
    serializer = EventSerializer(events, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getAvailableEvents(request):
    events = Event.objects.filter(registered_students__length__lt=models.F('capacity'))
    serializer = EventSerializer(events, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getEventsSortedByCreationDate(request):
    events = Event.objects.all().order_by('-created_at')
    serializer = EventSerializer(events, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getEventsSortedByUpdateDate(request):
    events = Event.objects.all().order_by('-updated_at')
    serializer = EventSerializer(events, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getEventsSortedByStartDate(request):
    events = Event.objects.all().order_by('event_start_date')
    serializer = EventSerializer(events, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getEventsSortedByEndDate(request):
    events = Event.objects.all().order_by('event_end_date')
    serializer = EventSerializer(events, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getEventsByMultipleFilters(request):
    creator = request.query_params.get('creator')
    eventType = request.query_params.get('eventType')
    location = request.query_params.get('location')
    host = request.query_params.get('host')
    min_capacity = request.query_params.get('min_capacity')
    max_capacity = request.query_params.get('max_capacity')
    events = Event.objects.all()
    if creator:
        events = events.filter(creator=creator)
    if eventType:
        events = events.filter(eventType=eventType)
    if location:
        events = events.filter(location__icontains=location)
    if host:
        events = events.filter(hosted_by__icontains=host)
    if min_capacity:
        events = events.filter(capacity__gte=min_capacity)
    if max_capacity:
        events = events.filter(capacity__lte=max_capacity)
    serializer = EventSerializer(events, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def apiOverview(request):
    endpoints = {
        'getEvents': '/api/events/',
        'getEvent': '/api/events/<eventID>/',
        'createEvent': '/api/events/create/',
        'updateEvent': '/api/events/update/<eventID>/',
        'deleteEvent': '/api/events/delete/<eventID>/',
        'registerStudent': '/api/events/register/<eventID>/',
        'unregisterStudent': '/api/events/unregister/<eventID>/',
        'getRegisteredStudents': '/api/events/registered_students/<eventID>/',
        # Add other endpoints as needed
    }
    return Response(endpoints)
@api_view(['GET'])
def welcome(request):
    return Response({'message': 'Welcome to the Events Service API'})

@api_view(['GET'])
def searchEvents(request):
    query = request.query_params.get('q', '')
    events = Event.objects.filter(models.Q(title__icontains=query) | models.Q(description__icontains=query))
    serializer = EventSerializer(events, many=True)
    return Response(serializer.data)
