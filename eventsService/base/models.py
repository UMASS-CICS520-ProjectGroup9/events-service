from django.db import models

# Create your models here.
class Event(models.Model):
    eventID = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    creator = models.CharField(max_length=100)
    eventType = models.CharField(max_length=50)
    location = models.CharField(max_length=200)
    capacity = models.IntegerField()
    image_url = models.URLField(blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    zoom_link = models.URLField(blank=True, null=True)
    hosted_by = models.CharField(max_length=100)
    registered_students = models.JSONField(default=list)  # List of student IDs
    event_start_date = models.DateTimeField()
    event_end_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 

    def __repr__(self):
        return f"Event({self.eventID}, {self.title}, {self.creator})"