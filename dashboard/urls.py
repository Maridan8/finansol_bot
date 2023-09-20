from django.urls import path
from . import views

urlpatterns = [
    path("main", views.homepage, name="homepage"),
    # path('data_input', views.data_input),
    # path("spell_check", views.spell_check),
    path("sendmail", views.sendmail),
    # path("lead", views.lead),
    path("intent", views.intent),
    path("utter_response", views.utter_response),
    path("session_register", views.session_register),
    path("free_timeslot", views.free_timeslot),
    path("meeting_book", views.meeting_book),
    path("save_lead", views.save_lead),
    path("upload_file", views.custom_train, name="upload_file"),
    path("ticket", views.ticket, name="ticket_generate"),
    path("analysis", views.analysis, name="analysis"),
    path("upload_product", views.upload_product, name="upload_product"),
    path("action_info", views.action_info, name="action_info"),
    path("product_register", views.product_register, name="product_register"),
    path("intent_analysis", views.intent_analysis, name="intent_analysis"),
]
