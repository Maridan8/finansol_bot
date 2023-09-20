from typing import Dict, Optional
from django.contrib import admin
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import render
from .models import (
    SessionConfig,
    IntentConfig,
    CustomQueryConfig,
    ClientConfig,
    LeadConfig,
    SessionList,
    CustomTrain,
    Ticket,
    MeetingConfig,
    ProductConfig,
    ChatAnalysis,
    StateConfig,
    IntentAnalysis,
)
from django.utils.html import mark_safe
import json
import csv
from django.http import FileResponse
from django.http import HttpResponse
from django_object_actions import DjangoObjectActions, action
from import_export.admin import ImportExportModelAdmin
from import_export import resources


@admin.action(description="Backup to CSV file")
def make_published(modeladmin, request, queryset):
    # dict_list = []
    # for query in queryset:
    #     data = {}
    #     data["session_id"] = query.session_id
    #     data["country_code"] = query.country_code
    #     data["city"] = query.city
    #     data["os_family"] = query.os_family
    #     data["device"] = query.device
    #     data["browser"] = query.browser
    #     data["query"] = query.query
    #     data["answer"] = query.answer
    #     data["intent"] = query.intent
    #     data["confidence"] = query.confidence

    #     dict_list.append(data)

    # json_data = json.dumps(dict_list)

    # with open("data.json", "w") as file:
    #     file.write(json_data)

    # response = FileResponse(open("data.json", "rb"), content_type="application/json")
    # response["Content-Disposition"] = 'attachment; filename="data.json"'

    header = [
        "session_id",
        "query",
        "answer",
        "intent",
        "confidence",
    ]

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="data.csv"'

    writer = csv.writer(response)
    writer.writerow(header)
    for query in queryset:
        writer.writerow(
            [
                query.session_id,
                query.query,
                query.answer,
                query.intent,
                query.confidence,
            ]
        )
    return response


class SessionConfigAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ["session_id", "query", "answer", "intent", "confidence", "datetime"]
    search_fields = ["session_id"]
    actions = [make_published]


class IntentConfigAdmin(admin.ModelAdmin):
    list_display = ["intent_name", "response"]
    # actions = [make_published]


class CustomeQueryConfigAdmin(admin.ModelAdmin):
    list_display = ["to_address", "name", "number", "email", "company", "content"]
    # actions = [make_published]


class LeadConfigAdmin(admin.ModelAdmin):
    list_display = ["to_address", "name", "number", "email", "company", "file_id"]


class ClientConfigAdmin(admin.ModelAdmin):
    list_display = [
        "to_address",
        "is_message_selected",
        "is_meeting_selected",
        "is_query_selected",
    ]


class ChildInline(admin.TabularInline):
    model = SessionConfig


class SessionListAdmin(admin.ModelAdmin):
    list_display = [
        "session_id",
        "ip_address",
        "device",
        "browser",
        "country",
        "latitude",
        "longitude",
        "num_messages",
        "datetime",
        "os",
    ]
    search_fields = ["session_id", "ip_address"]
    inlines = [
        ChildInline,
    ]


class CustomTrainAdmin(DjangoObjectActions, admin.ModelAdmin):
    list_display = ["model_name", "date"]
    search_fields = ["model_name"]
    change_form_template = "upload_form.html"


class TicketAdmin(DjangoObjectActions, admin.ModelAdmin):
    # readonly_fields = ("ticket_number",)
    list_display = ["ticket_number", "subject", "issue"]
    change_form_template = "ticket.html"


class MeetingConfigAdmin(admin.ModelAdmin):
    list_display = ["name", "number", "email", "company", "datetime"]


class ProductConfigAdmin(DjangoObjectActions, admin.ModelAdmin):
    list_display = [
        "product_name",
        "info",
        "file_1",
        "file_2",
        "file_3",
        "rank",
        # "intent",
        # "domain",
    ]

    # def domain(self, obj):
    #     return mark_safe('<a href="%s">%s</a>')

    # actions = ["activate", "deactivate"]
    change_list_template = "products.html"

    def changelist_view(self, request, extra_context=None):
        if extra_context is None:
            extra_context = {}

        # Add your extra context variables here
        extra_context["intent_list"] = []
        extra_context["selected_intent"] = "None"
        extra_context["selected_response"] = ""
        intents = IntentConfig.objects.all()
        for intent in intents:
            extra_context["intent_list"].append(intent.intent_name)
            if intent.is_product:
                extra_context["selected_intent"] = intent.intent_name
                extra_context["selected_response"] = intent.response

        return super().changelist_view(request, extra_context=extra_context)


class ChatAnalysisAdmin(admin.ModelAdmin):
    list_display = []
    change_list_template = "chat.html"


class StateConfigAdmin(admin.ModelAdmin):
    list_display = ["session_id", "state"]


class IntentAnalysisAdmin(admin.ModelAdmin):
    list_display = []
    change_list_template = "intentanalysis.html"


admin.site.register(SessionConfig, SessionConfigAdmin)
admin.site.register(IntentConfig, IntentConfigAdmin)
admin.site.register(CustomQueryConfig, CustomeQueryConfigAdmin)
admin.site.register(ClientConfig, ClientConfigAdmin)
admin.site.register(LeadConfig, LeadConfigAdmin)
admin.site.register(SessionList, SessionListAdmin)
admin.site.register(CustomTrain, CustomTrainAdmin)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(MeetingConfig, MeetingConfigAdmin)
admin.site.register(ProductConfig, ProductConfigAdmin)
admin.site.register(ChatAnalysis, ChatAnalysisAdmin)
admin.site.register(StateConfig, StateConfigAdmin)
admin.site.register(IntentAnalysis, IntentAnalysisAdmin)
# Register your models here.
