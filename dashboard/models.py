from django.db import models
from django.contrib import admin
from django.core.validators import EmailValidator
from django import forms
from django.forms.fields import FileField
from django.core.files.uploadedfile import UploadedFile


class FeedFile(models.Model):
    file = models.FileField(upload_to="static/product/")


class IntentConfig(models.Model):
    intent_name = models.CharField(max_length=100, db_index=True)
    response = models.CharField(max_length=1000, blank=True)
    is_product = models.BooleanField(default=False)


class CustomQueryConfig(models.Model):
    to_address = models.EmailField(
        validators=[EmailValidator(message="Please enter a valid email address.")]
    )
    name = models.CharField(max_length=20)
    number = models.CharField(max_length=15)
    email = models.EmailField(
        validators=[EmailValidator(message="Please enter a valid email address.")]
    )
    company = models.CharField(max_length=40)
    content = models.CharField(max_length=500)


class LeadConfig(models.Model):
    to_address = models.EmailField(
        validators=[EmailValidator(message="Please enter a valid email address.")]
    )
    name = models.CharField(max_length=20)
    number = models.CharField(max_length=15)
    email = models.EmailField(
        validators=[EmailValidator(message="Please enter a valid email address.")]
    )
    company = models.CharField(max_length=40)
    file_id = models.CharField(max_length=500)


class ClientConfig(models.Model):
    to_address = models.EmailField(
        validators=[EmailValidator(message="Please enter a valid email address.")]
    )
    is_message_selected = models.BooleanField(default=True)
    is_meeting_selected = models.BooleanField(default=False)
    is_query_selected = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.is_meeting_selected:
            # Set all other records to False
            ClientConfig.objects.exclude(pk=self.pk).update(is_meeting_selected=False)
        super().save(*args, **kwargs)


class SessionList(models.Model):
    session_id = models.CharField(max_length=50, primary_key=True)
    datetime = models.DateTimeField()
    num_messages = models.IntegerField()
    ip_address = models.CharField(max_length=15)
    device = models.CharField(max_length=10)
    browser = models.CharField(max_length=10)
    country = models.CharField(max_length=20)
    latitude = models.CharField(max_length=10)
    longitude = models.CharField(max_length=10)
    os = models.CharField(max_length=15)


class SessionConfig(models.Model):
    # session_id = models.CharField(max_length=50)
    session_id = models.ForeignKey(SessionList, on_delete=models.CASCADE)
    intent = models.CharField(max_length=20)
    query = models.CharField(max_length=100)
    answer = models.CharField(max_length=500)
    confidence = models.CharField(max_length=15)
    datetime = models.DateTimeField()


class MeetingConfig(models.Model):
    name = models.CharField(max_length=20)
    number = models.CharField(max_length=15)
    email = models.EmailField(
        validators=[EmailValidator(message="Please enter a valid email address.")]
    )
    company = models.CharField(max_length=20)
    datetime = models.DateTimeField()


class CustomTrain(models.Model):
    model_name = models.CharField(max_length=20)
    date = models.DateField()


class Ticket(models.Model):
    ticket_number = models.CharField(max_length=40)
    subject = models.CharField(max_length=40)
    issue = models.TextField()


class ProductConfig(models.Model):
    product_name = models.CharField(max_length=40)
    info = models.TextField()
    file_1 = models.FileField(upload_to="static/product/", null=True, blank=True)
    file_2 = models.FileField(upload_to="static/product/", null=True, blank=True)
    file_3 = models.FileField(upload_to="static/product/", null=True, blank=True)
    rank = models.IntegerField(unique=True)


class ChatAnalysis(models.Model):
    name = models.CharField(max_length=15)


class StateConfig(models.Model):
    session_id = models.CharField(max_length=40)
    state = models.CharField(max_length=15, null=True)
    name = models.CharField(max_length=20, null=True)
    email = models.CharField(max_length=30, null=True)
    company = models.CharField(max_length=20, null=True)
    number = models.CharField(max_length=15, null=True)
    lead_state = models.BooleanField(default=False, null=True)
    meeting_state = models.BooleanField(default=False, null=True)
    bug = models.BooleanField(default=False, null=True)
    msg = models.CharField(max_length=200, null=True)


class IntentAnalysis(models.Model):
    datetime = models.DateTimeField()
