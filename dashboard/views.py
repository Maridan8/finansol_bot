from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django_user_agents.utils import get_user_agent
from textblob import TextBlob
import os
import uuid
import json
import csv
import pytz
import string
import re
import random
from datetime import datetime, timedelta
import calendar

# import openai
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import requests
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from pychartjs import BaseChart, ChartType, Color

# for encoding/decoding messages in base64
from base64 import urlsafe_b64decode, urlsafe_b64encode

# for dealing with attachement MIME types
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from mimetypes import guess_type as guess_mime_type


from .models import (
    ClientConfig,
    IntentConfig,
    SessionConfig,
    CustomQueryConfig,
    LeadConfig,
    SessionList,
    CustomTrain,
    Ticket,
    MeetingConfig,
    ProductConfig,
    StateConfig,
)


def get_ip():
    response = requests.get("https://api64.ipify.org?format=json").json()
    return response["ip"]


@csrf_exempt
def free_timeslot(request):
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    try:
        to_messages = ClientConfig.objects.get(is_meeting_selected=True).to_address
    except:
        return JsonResponse({"res": "Error"})

    SCOPES = ["https://www.googleapis.com/auth/calendar"]
    if os.path.exists("meeting/" + to_messages + "/token.json"):
        # if os.path.exists("meeting/free/token.json"):
        creds = Credentials.from_authorized_user_file(
            "meeting/" + to_messages + "/token.json",
            SCOPES
            # "meeting/free/token.json",
            # SCOPES,
        )
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                to_messages + "/credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("meeting/" + to_messages + "/token.json", "w") as token:
            # with open("meeting/free/token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)

        # Call the Calendar API
        tz = pytz.timezone("Europe/Paris")

        time_zone = "Europe/Paris"
        current_date_time = datetime.now()

        # Set the time zone
        tz = pytz.timezone(time_zone)

        # Convert the time zone
        current_date_time = current_date_time.astimezone(tz)

        datetime_after_2_hours = current_date_time + timedelta(hours=2)

        if datetime_after_2_hours.hour >= 17:
            next_day = datetime_after_2_hours + timedelta(days=1)
            start_datetime = datetime(next_day.year, next_day.month, next_day.day, 9)
        elif datetime_after_2_hours.hour <= 9:
            start_datetime = datetime(
                datetime_after_2_hours.year,
                datetime_after_2_hours.month,
                datetime_after_2_hours.day,
                9,
            )
        else:
            start_datetime = datetime(
                datetime_after_2_hours.year,
                datetime_after_2_hours.month,
                datetime_after_2_hours.day,
                datetime_after_2_hours.hour,
            )

        start_of_week = datetime_after_2_hours.date() - timedelta(
            days=datetime_after_2_hours.weekday()
        )
        end_of_week = start_of_week + timedelta(days=5)

        end_datetime = datetime(
            end_of_week.year, end_of_week.month, end_of_week.day, 17
        )

        free_time = []
        free_number = 0

        print("end", end_datetime)
        print("start", start_datetime)
        if end_datetime > start_datetime:
            for n in range(int((end_datetime - start_datetime).days) + 1):
                current_date = start_datetime + timedelta(n)
                if n != 0:
                    current_date = datetime(
                        current_date.year, current_date.month, current_date.day, 9
                    )

                the_datetime1 = tz.localize(current_date)
                the_datetime2 = tz.localize(
                    datetime(
                        current_date.year, current_date.month, current_date.day, 17
                    )
                )
                id = "harryporter319193@gmail.com"
                body = {
                    "timeMin": the_datetime1.isoformat(),
                    "timeMax": the_datetime2.isoformat(),
                    "timeZone": "Europe/Paris",
                    "items": [{"id": id}],
                }

                eventsResult = service.freebusy().query(body=body).execute()
                cal_dict = eventsResult["calendars"]
                print(cal_dict[id]["busy"])

                s_time = current_date
                step_size = timedelta(minutes=30)
                for cal in cal_dict[id]["busy"]:
                    b_start = datetime(
                        int(cal["start"].split("-")[0]),
                        int(cal["start"].split("-")[1]),
                        int(cal["start"].split("T")[0].split("-")[2]),
                        int(cal["start"].split("T")[1].split(":")[0]),
                        int(cal["start"].split("T")[1].split(":")[1]),
                    )
                    b_end = datetime(
                        int(cal["end"].split("-")[0]),
                        int(cal["end"].split("-")[1]),
                        int(cal["end"].split("T")[0].split("-")[2]),
                        int(cal["end"].split("T")[1].split(":")[0]),
                        int(cal["end"].split("T")[1].split(":")[1]),
                    )

                    if s_time + timedelta(minutes=30) <= b_start:
                        c_time = s_time
                        while c_time <= b_end - timedelta(minutes=30):
                            d_time = c_time + step_size
                            free_time.append(
                                {
                                    "start": f"{c_time.year},{c_time.month},{c_time.day},{c_time.hour},{c_time.minute}",
                                    "end": f"{d_time.year},{d_time.month},{d_time.day},{d_time.hour},{d_time.minute}",
                                }
                            )
                            c_time = d_time
                            free_number += 1
                    if free_number >= 3:
                        break

                if free_number >= 3:
                    break
        print(free_time)
        return JsonResponse({"res": free_time})
    except HttpError as error:
        return JsonResponse({"res": "Error"})


@csrf_exempt
def session_register(request):
    if request.method == "POST":
        user_agent = get_user_agent(request)
        req_headers = request.META
        x_forwarded_for_value = req_headers.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for_value:
            ip_addr = x_forwarded_for_value.split(",")[-1].strip()
        else:
            ip_addr = req_headers.get("REMOTE_ADDR")

        request_url = "https://geolocation-db.com/jsonp/" + ip_addr
        response = requests.get(request_url)
        result = response.content.decode()
        result = result.split("(")[1].strip(")")
        result = json.loads(result)

        user_msg = request.POST.get("user_msg")
        bot_msg = request.POST.get("bot_msg")
        intent = request.POST.get("intent")
        confidence = request.POST.get("confidence")

        session_info = SessionList.objects.filter(
            ip_address=ip_addr,
            device=user_agent.device.family,
            browser=user_agent.browser.family,
            os=user_agent.os.family,
        )

        if session_info:
            session_id = session_info[0].session_id
        else:
            session_id = str(uuid.uuid4())
            new_s_list = SessionList(
                session_id=session_id,
                ip_address=ip_addr,
                device=user_agent.device.family,
                browser=user_agent.browser.family,
                os=user_agent.os.family,
                country=result["country_code"],
                num_messages=0,
                latitude=result["latitude"],
                longitude=result["longitude"],
                datetime=datetime.now(),
            )

            new_s_list.save()

        res = SessionList.objects.get(session_id=session_id).num_messages
        res += 1

        parent = SessionList.objects.get(session_id=session_id)
        session_reg = SessionConfig(
            session_id=parent,
            query=user_msg,
            answer=bot_msg,
            intent=intent,
            confidence=confidence,
            datetime=datetime.now(),
        )

        session_reg.save()

        res = SessionList.objects.get(session_id=session_id).num_messages
        res += 1
        SessionList.objects.filter(session_id=session_id).update(num_messages=res)

        return JsonResponse({"res": "Good"})


def custom_train(request):
    if request.method == "POST":
        # Handle the file upload
        file = request.FILES["file"]
        with open("static/train_data/" + file.name, "wb+") as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        with open("static/train_data/" + file.name, "r") as f:
            reader = csv.reader(f)
            rows = list(reader)

        nlus = []
        for index, line in enumerate(rows):
            if index == 0:
                intent_list = line
                for intent in intent_list:
                    nlus.append([])
            else:
                for order, lis in enumerate(line):
                    nlus[order].append(lis)

        print(intent_list)
        train_data = open("train.txt", "r")
        contents = train_data.read()

        # inents add
        contents += "intents:\n"
        for intent in intent_list:
            contents += "- " + intent + "\n"

        # nlu add
        contents += "nlu:\n"
        for index, nlu in enumerate(nlus):
            contents += "- intent: " + intent_list[index] + "\n" + "  examples: |\n"

            for sentence in nlu:
                if sentence != "":
                    contents += "    - " + sentence + "\n"

        # rule add
        contents += "rules:\n"

        for intent in intent_list:
            contents += (
                "- rule: customized "
                + intent
                + "\n  steps:\n    - intent: "
                + intent
                + "\n    - action: utter_"
                + intent
                + "\n"
            )

        # response add
        contents += "responses:\n"
        for intent in intent_list:
            contents += "  utter_" + intent + ":\n  - text: '" + intent + "'\n"

        # Do something with the file
        url = "http://localhost:5005/model/train"

        headers = {"Content-Type": "application/json"}

        print(contents)
        response = requests.request(
            "POST", url, headers=headers, data=contents.encode("utf-8")
        )

        if response.status_code == 200:
            train_instance = CustomTrain(
                model_name=response.headers["filename"], date=datetime.now()
            )
            train_instance.save()

            r_url = "http://localhost:5005/model"

            payload = json.dumps(
                {"model_file": "models/" + response.headers["filename"]}
            )
            headers = {"Content-Type": "application/json"}

            res = requests.request("PUT", r_url, data=payload)
            print(res.status_code)
            os.remove("static/train_data/" + file.name)

            IntentConfig.objects.all().delete()

            for intent in intent_list:
                new_record = IntentConfig(intent_name=intent, response=intent)
                new_record.save()

            previous_url = request.META.get("HTTP_REFERER")
            return HttpResponseRedirect(previous_url)

        else:
            os.remove("static/train_data/" + file.name)
            url = reverse("upload_file")
            return HttpResponseRedirect(url)
    else:
        return HttpResponse("Training is failed.")


def homepage(request):
    # mails = ClientConfig.objects.all()
    # mail_list = {}
    # for mail in mails:
    #     mail_list[mail.to_address] = mail.to_address

    # user_agent = get_user_agent(request)
    # session_info = {}
    # session_info["browser"] = user_agent.browser.family
    # session_info["os"] = user_agent.os.family
    # session_info["device"] = user_agent.device.family

    # req_headers = request.META
    # x_forwarded_for_value = req_headers.get("HTTP_X_FORWARDED_FOR")
    # if x_forwarded_for_value:
    #     ip_addr = x_forwarded_for_value.split(",")[-1].strip()
    # else:
    #     ip_addr = req_headers.get("REMOTE_ADDR")
    # session_info["ip_address"] = ip_addr

    # intent_list = {}
    # intents = IntentConfig.objects.all()
    # for item in intents:
    #     intent_list[item.intent_name] = item.response

    # request_url = "https://geolocation-db.com/jsonp/" + ip_addr
    # response = requests.get(request_url)
    # result = response.content.decode()
    # result = result.split("(")[1].strip(")")
    # result = json.loads(result)

    # return render(
    #     request,
    #     "index.html",
    #     {"leads": mail_list, "session_info": session_info, "intents": intent_list},
    # )

    return render(request, "index.html")

    # return HttpResponse("asdf")


# Create your views here.

# @csrf_exempt
# def spell_check(request):
#     if request.method == "POST":
#         message = request.POST.get("msg")
#         openai.api_key = "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"
#         res = openai.Completion.create(
#             model="text-davinci-003",
#             prompt="""Check spelling of following french sentence.""" + message,
#             temperature=0.1
#         )

#         return JsonResponse({"res": res['choices'][0]['text']})
#         # return JsonResponse({"res": "Hello"})


@csrf_exempt
def utter_response(request):
    if request.method == "POST":
        intent = request.POST.get("msg")
        if intent == "fallback":
            intent = "random"
        data = IntentConfig.objects.get(intent_name=intent)
        if not data:
            data = IntentConfig.objects.get(intent_name="random")
        product_list = []
        if data.is_product:
            print("Yes")
            products = ProductConfig.objects.order_by("rank")
            for product in products:
                datas = {}
                datas["name"] = product.product_name
                datas["info"] = product.info
                datas["file"] = product.file
                datas["rank"] = product.rank
                product_list.append(datas)
        print(product_list)
        return JsonResponse({"res": data.response, "product": product_list})


@csrf_exempt
def meeting_book(request):
    SCOPES = ["https://www.googleapis.com/auth/calendar"]
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    to_messages = ClientConfig.objects.get(is_meeting_selected=True).to_address
    if os.path.exists("meeting/" + to_messages + "/token.json"):
        # if os.path.exists("meeting/free/token.json"):
        creds = Credentials.from_authorized_user_file(
            "meeting/" + to_messages + "/token.json",
            SCOPES
            # "meeting/free/token.json",
            # SCOPES,
        )
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                to_messages + "/credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("meeting/" + to_messages + "/token.json", "w") as token:
            token.write(creds.to_json())

    to_messages = "harryporter319193@gmail.com"
    try:
        service = build("calendar", "v3", credentials=creds)
        time = request.POST.get("time")
        name = request.POST.get("name")
        email = request.POST.get("email")
        number = request.POST.get("number")
        company = request.POST.get("company")

        # Call the Calendar API

        start_time = (
            time.split("-")[0].split(",")[0]
            + "-"
            + time.split("-")[0].split(",")[1]
            + "-"
            + time.split("-")[0].split(",")[2]
            + "T"
            + time.split("-")[0].split(",")[3]
            + ":"
            + time.split("-")[0].split(",")[4]
            + ":00"
        )

        end_time = (
            time.split("-")[1].split(",")[0]
            + "-"
            + time.split("-")[1].split(",")[1]
            + "-"
            + time.split("-")[1].split(",")[2]
            + "T"
            + time.split("-")[1].split(",")[3]
            + ":"
            + time.split("-")[1].split(",")[4]
            + ":00"
        )

        req_headers = request.META
        x_forwarded_for_value = req_headers.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for_value:
            ip_addr = x_forwarded_for_value.split(",")[-1].strip()
        else:
            ip_addr = req_headers.get("REMOTE_ADDR")

        # res =

        event = {
            "summary": "Finansol meeting",
            # "location": "800 Howard St., San Francisco, CA 94103",
            # "description": "A chance to hear more about Google's developer products.",
            "start": {
                "dateTime": start_time,
                "timeZone": "Europe/Paris",
            },
            "end": {
                "dateTime": end_time,
                "timeZone": "Europe/Paris",
            },
            "recurrence": ["RRULE:FREQ=DAILY;COUNT=1"],
            "attendees": [
                {"email": to_messages},
                {"email": email},
            ],
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "email", "minutes": 24 * 60},
                    {"method": "popup", "minutes": 10},
                ],
            },
        }

        event = service.events().insert(calendarId="primary", body=event).execute()

        res = MeetingConfig(
            name=name, email=email, number=number, company=company, datetime=time
        )

        res.save()
        return JsonResponse({"res": "Meeting is booked."})

    except HttpError as error:
        return JsonResponse({"res": "Error"})


@csrf_exempt
def intent(request):
    if request.method == "POST":
        intents = IntentConfig.objects.all()
        answer = {}
        for item in intents:
            answer[item.intent_name] = item.response
        return JsonResponse({"res": answer})


@csrf_exempt
def save_lead(request):
    if request.method == "POST":
        file_id = request.POST.get("file_id")
        name = request.POST.get("name")
        number = request.POST.get("number")
        email = request.POST.get("email")
        company = request.POST.get("company")

        to_message = ClientConfig.objects.filter(is_message_selected=True)

        for message in to_message:
            lead_data = LeadConfig(
                to_address=message.to_address,
                name=name,
                number=number,
                email=email,
                company=company,
                file_id=file_id,
            )

            lead_data.save()
        return JsonResponse({"res": "Good!"})


def gmail_authenticate():
    SCOPES = ["https://mail.google.com/"]
    creds = None
    # the file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    # if there are no (valid) credentials availablle, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
    return build("gmail", "v1", credentials=creds)


def add_attachment(message, filename):
    content_type, encoding = guess_mime_type(filename)
    if content_type is None or encoding is not None:
        content_type = "application/octet-stream"
    main_type, sub_type = content_type.split("/", 1)
    if main_type == "text":
        fp = open(filename, "rb")
        msg = MIMEText(fp.read().decode(), _subtype=sub_type)
        fp.close()
    elif main_type == "image":
        fp = open(filename, "rb")
        msg = MIMEImage(fp.read(), _subtype=sub_type)
        fp.close()
    elif main_type == "audio":
        fp = open(filename, "rb")
        msg = MIMEAudio(fp.read(), _subtype=sub_type)
        fp.close()
    else:
        fp = open(filename, "rb")
        msg = MIMEBase(main_type, sub_type)
        msg.set_payload(fp.read())
        fp.close()
    filename = os.path.basename(filename)
    msg.add_header("Content-Disposition", "attachment", filename=filename)
    message.attach(msg)


def build_message(destination, obj, body, attachments=[]):
    our_email = "harryporter319193@gmail.com"
    if not attachments:  # no attachments given
        message = MIMEText(body)
        message["to"] = destination
        message["from"] = our_email
        message["subject"] = obj
    else:
        message = MIMEMultipart()
        message["to"] = destination
        message["from"] = our_email
        message["subject"] = obj
        message.attach(MIMEText(body))
        for filename in attachments:
            add_attachment(message, filename)
    return {"raw": urlsafe_b64encode(message.as_bytes()).decode()}


def send_message(service, destination, obj, body, attachments=[]):
    return (
        service.users()
        .messages()
        .send(userId="me", body=build_message(destination, obj, body, attachments))
        .execute()
    )


@csrf_exempt
def sendmail(request):
    if request.method == "POST":
        content = request.POST.get("content")
        name = request.POST.get("name")
        number = request.POST.get("number")
        email = request.POST.get("email")
        company = request.POST.get("company")

        message = name + " " + email + " " + number + " " + company + " " + content

        print(message)
        service = gmail_authenticate()

        to_message = ClientConfig.objects.filter(is_query_selected=True)
        for messaget in to_message:
            send_message(
                service,
                messaget.to_address,
                "Notification",
                message,
                [],
            )

            query_data = CustomQueryConfig(
                to_address=messaget.to_address,
                name=name,
                number=number,
                email=email,
                company=company,
                content=content,
            )

            query_data.save()
        return JsonResponse({"res": "Hello"})


def ticket(request):
    service = gmail_authenticate()
    ticket_id = str(uuid.uuid4())
    subject = request.POST.get("subject")
    issue = request.POST.get("issue")
    send_message(
        service,
        "shubham@thefinansol.com",
        "Notification",
        subject + " " + issue,
        [],
    )

    tickets = Ticket(ticket_number=ticket_id)
    tickets.save()

    previous_url = request.META.get("HTTP_REFERER")
    return HttpResponseRedirect(previous_url)


def upload_product(request):
    product_name = request.POST.get("product_name")
    info = request.POST.get("info")
    rank = request.POST.get("rank")
    images = request.FILES.getlist("images")
    intent = request.POST.get("intent")

    file = ""
    os.makedirs("static/product/" + product_name, exist_ok=True)
    for image in images:
        with open(
            "static/product/" + product_name + "/" + image.name, "wb+"
        ) as destination:
            for chunk in image.chunks():
                destination.write(chunk)
        file += image.name + "\n"

    file = file.rstrip()

    product = ProductConfig(product_name=product_name, info=info, rank=rank, file=file)
    product.save()

    intent_exist = IntentConfig.objects.get(intent_name=intent)
    if intent_exist:
        products = ProductConfig.objects.all()
        for product in products:
            product.intent = intent
            product.save()

            intent_exist.is_product = True
            intent_exist.save()

    previous_url = request.META.get("HTTP_REFERER")
    return HttpResponseRedirect(previous_url)


class MyBarGraph(BaseChart):
    type = ChartType.Bar

    class options:
        title = {"display": False}


class MyPieGraph(BaseChart):
    type = ChartType.Pie

    class options:
        title = {"display": False}


class MyLineGraph(BaseChart):
    type = ChartType.Line

    class options:
        title = {"display": False}


def analysis(request):
    color_list = [
        "yellow",
        "cyan",
        "pink",
        "lightgreen",
        "gold",
        "lightblue",
        "aqua",
        "brown",
        "white",
        "purple",
        "magenta",
    ]
    Intent = MyBarGraph()
    IntentPie = MyPieGraph()

    intents = IntentConfig.objects.all()
    intent_list = []
    intent_data = []
    max_intent_num = 0
    total_num = 0
    max_intent_name = ""
    for intent in intents:
        intent_list.append(intent.intent_name)
        intent_num = SessionConfig.objects.filter(intent=intent.intent_name).count()
        total_num += intent_num
        intent_data.append(intent_num)

        if intent.intent_name != "random" and intent_num >= max_intent_num:
            max_intent_name = intent.intent_name
            max_intent_num = intent_num
    Intent.labels.group = intent_list
    Intent.data.data = intent_data
    Intent.data.backgroundColor = color_list[: len(intent_list)]
    Intent.data.label = "Number of times each intent is called."

    IntentPie.labels.group = intent_list
    intentpie_data = []
    for intent in intent_data:
        intentpie_data.append(intent * 100 / total_num)
    IntentPie.data.data = intentpie_data
    IntentPie.data.backgroundColor = color_list[: len(intent_list)]
    IntentPie.data.label = "Number of times each intent is called."

    IntentJSON = Intent.get()
    IntentPie = IntentPie.get()

    Session = MyBarGraph()
    SessionConfidence = MyBarGraph()

    sessions = SessionList.objects.all()
    session_list = []
    session_data = []
    sessionconfidence_data = []
    for index, session in enumerate(sessions):
        session_list.append(session.session_id)

        session_datas = SessionConfig.objects.filter(session_id=session.session_id)

        session_data.append(session_datas.count())

        sum = 0
        for session_data_item in session_datas:
            sum += float(session_data_item.confidence)

        sessionconfidence_data.append(sum / session_datas.count())

    Session.labels.group = session_list
    Session.data.data = session_data
    Session.data.label = "Number of messages of Session."
    Session.options.indexAxis = "y"
    SessionJSON = Session.get()

    SessionConfidence.labels.group = session_list
    SessionConfidence.data.data = sessionconfidence_data
    SessionConfidence.data.label = "Avg confidence"
    SessionConfidenceJSON = SessionConfidence.get()

    Country = MyBarGraph()

    countries = SessionList.objects.values("country").distinct()
    country_list = []
    country_data = []
    for country in countries:
        country_list.append(country["country"])
        country_data.append(
            SessionList.objects.filter(country=country["country"]).count()
        )

    Country.labels.group = country_list
    Country.data.data = country_data
    Country.data.label = "Country"
    CountryJSON = Country.get()

    Ip = MyBarGraph()

    ips = SessionList.objects.values("ip_address").distinct()
    ip_list = []
    ip_data = []
    for ip in ips:
        ip_list.append(ip["ip_address"])
        ip_data.append(SessionList.objects.filter(ip_address=ip["ip_address"]).count())

    Ip.labels.group = ip_list
    Ip.data.data = ip_data
    Ip.data.label = "ip"
    IpJSON = Ip.get()

    Device = MyBarGraph()

    devices = SessionList.objects.values("device").distinct()
    device_list = []
    device_data = []
    for device in devices:
        device_list.append(device["device"])
        device_data.append(SessionList.objects.filter(device=device["device"]).count())

    Device.labels.group = device_list
    Device.data.data = device_data
    Device.data.backgroundColor = color_list[: len(device_list)]
    Device.data.label = "Device"
    DeviceJSON = Device.get()

    Browser = MyBarGraph()

    browsers = SessionList.objects.values("browser").distinct()
    browser_list = []
    browser_data = []
    for browser in browsers:
        browser_list.append(browser["browser"])
        browser_data.append(
            SessionList.objects.filter(browser=browser["browser"]).count()
        )

    Browser.labels.group = browser_list
    Browser.data.data = browser_data
    Browser.data.label = "Browser"
    BrowserJSON = Browser.get()

    Os = MyBarGraph()

    oss = SessionList.objects.values("os").distinct()
    os_list = []
    os_data = []
    for os in oss:
        os_list.append(os["os"])
        os_data.append(SessionList.objects.filter(os=os["os"]).count())

    Os.labels.group = os_list
    Os.data.data = os_data
    Os.data.label = "Os"
    OsJSON = Os.get()

    start_date = SessionConfig.objects.order_by("datetime")[0].datetime.date()
    end_date = datetime.today().date()

    day_list = []
    week_list = []
    month_list = []

    start_date = datetime(start_date.year, start_date.month, start_date.day, 0, 0, 0)
    end_date = datetime(end_date.year, end_date.month, end_date.day, 0, 0, 0)
    # print(string(start_date.year()))
    current_date = start_date
    while current_date <= end_date:
        day_list.append(current_date.strftime("%Y-%m-%d-00-00-00"))
        current_date += timedelta(days=1)

    current_date = start_date
    while current_date <= end_date:
        week_list.append(current_date.strftime("%Y-%m-%d-00-00-00"))
        current_date += timedelta(weeks=1)

    current_date = start_date
    while current_date <= end_date:
        month_list.append(current_date.strftime("%Y-%m-%d-00-00-00"))
        current_date += timedelta(
            days=calendar.monthrange(current_date.year, current_date.month)[1]
        )

    Day = MyLineGraph()
    label_day_list = []
    for day in day_list:
        label_day_list.append(day[2:10])
    Day.labels.group = label_day_list
    day_data = []
    for index, day_item in enumerate(day_list):
        if index != len(day_list) - 1:
            start = datetime.strptime(day_list[index], "%Y-%m-%d-%H-%M-%S")
            end = datetime.strptime(day_list[index + 1], "%Y-%m-%d-%H-%M-%S")
            day_data.append(
                SessionConfig.objects.filter(
                    datetime__gte=start, datetime__lte=end
                ).count()
            )
        else:
            start = datetime.strptime(day_list[index], "%Y-%m-%d-%H-%M-%S")
            day_data.append(SessionConfig.objects.filter(datetime__gte=start).count())

    Day.data.data = day_data
    Day.data.label = "Daily report"
    DayJSON = Day.get()

    Week = MyLineGraph()
    label_week_list = []
    for week in week_list:
        label_week_list.append(week[2:10])
    Week.labels.group = label_week_list
    week_data = []
    for index, day_item in enumerate(week_list):
        if index != len(week_list) - 1:
            start = datetime.strptime(week_list[index], "%Y-%m-%d-%H-%M-%S")
            end = datetime.strptime(week_list[index + 1], "%Y-%m-%d-%H-%M-%S")
            week_data.append(
                SessionConfig.objects.filter(
                    datetime__gte=start, datetime__lte=end
                ).count()
            )
        else:
            start = datetime.strptime(week_list[index], "%Y-%m-%d-%H-%M-%S")
            week_data.append(SessionConfig.objects.filter(datetime__gte=start).count())
    Week.data.data = week_data
    Week.data.label = "Weekly report"
    WeekJSON = Week.get()

    Month = MyLineGraph()
    label_month_list = []
    for month in month_list:
        label_month_list.append(month[2:10])
    Month.labels.group = label_month_list
    month_data = []
    for index, day_item in enumerate(month_list):
        if index != len(month_list) - 1:
            start = datetime.strptime(month_list[index], "%Y-%m-%d-%H-%M-%S")
            end = datetime.strptime(month_list[index + 1], "%Y-%m-%d-%H-%M-%S")
            month_data.append(
                SessionConfig.objects.filter(
                    datetime__gte=start, datetime__lte=end
                ).count()
            )
        else:
            start = datetime.strptime(month_list[index], "%Y-%m-%d-%H-%M-%S")
            month_data.append(SessionConfig.objects.filter(datetime__gte=start).count())
    Month.data.data = month_data
    Month.data.label = "Weekly report"
    MonthJSON = Month.get()

    return render(
        request=request,
        template_name="analysis.html",
        context={
            "IntentJSON": IntentJSON,
            "IntentPie": IntentPie,
            "SessionJSON": SessionJSON,
            "SessionConfidenceJSON": SessionConfidenceJSON,
            "CountryJSON": CountryJSON,
            "IpJSON": IpJSON,
            "DeviceJSON": DeviceJSON,
            "BrowserJSON": BrowserJSON,
            "OsJSON": OsJSON,
            "DayJSON": DayJSON,
            "WeekJSON": WeekJSON,
            "MonthJSON": MonthJSON,
            "max_intent_name": max_intent_name,
            "max_intent_num": max_intent_num,
        },
    )


@csrf_exempt
def action_info(request):
    text = request.POST.get("msg")

    user_agent = get_user_agent(request)
    req_headers = request.META
    x_forwarded_for_value = req_headers.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for_value:
        ip_addr = x_forwarded_for_value.split(",")[-1].strip()
    else:
        ip_addr = req_headers.get("REMOTE_ADDR")

    # request_url = "https://geolocation-db.com/jsonp/" + ip_addr
    # response = requests.get(request_url)
    # result = response.content.decode()
    # result = result.split("(")[1].strip(")")
    # result = json.loads(result)

    session_info = SessionList.objects.filter(
        ip_address=ip_addr,
        device=user_agent.device.family,
        browser=user_agent.browser.family,
        os=user_agent.os.family,
    )

    if session_info:
        print("Session exist.")
        session_id = session_info[0].session_id
    else:
        print("Session doesn't exist.")
        session_id = str(uuid.uuid4())
        new_s_list = SessionList(
            session_id=session_id,
            ip_address=ip_addr,
            device=user_agent.device.family,
            browser=user_agent.browser.family,
            os=user_agent.os.family,
            # country=result["country_code"],
            country="RU",
            num_messages=0,
            # latitude=result["latitude"],
            # longitude=result["longitude"],
            latitude="58",
            longitude="45",
            datetime=datetime.now(),
        )
        new_s_list.save()

        statedb = StateConfig(
            session_id=session_id,
            state="init",
            name="",
            email="",
            number="",
            company="",
            msg="",
            bug=False,
            meeting_state=False,
            lead_state=False,
        )
        statedb.save()

    state_config = StateConfig.objects.get(session_id=session_id)
    state = state_config.state
    email = state_config.email
    number = state_config.number
    name = state_config.name
    company = state_config.company
    lead_state = state_config.lead_state
    meeting_state = state_config.meeting_state
    bug = state_config.bug
    confidence = random.uniform(0.7, 1)

    if text.lower() == "/cancel":
        msg = "All steps are cancelled"
        StateConfig.objects.filter(session_id=session_id).update(
            state="init", lead_state=False, meeting_state=False
        )
        return JsonResponse([{"text": msg}], safe=False)

    if state == "progress_select" and text.lower() == "/forward":
        if lead_state:
            file_id = str(uuid.uuid4())
            response = (
                "Thank you for your interest, your details are forwarded to our backend. Your file number is "
                + file_id
                + " and you will soon receive soon email on your email id for further process"
            )

            message_payload = {
                "purpose": "lead",
                "content": {
                    "name": name,
                    "email": email,
                    "number": number,
                    "company": company,
                    "file_id": file_id,
                    "response": response,
                },
            }

            StateConfig.objects.filter(session_id=session_id).update(
                state="init", bug=False, lead_state=False
            )
            return JsonResponse([{"custom": message_payload}], safe=False)
        elif meeting_state:
            message_payload = {
                "purpose": "meeting",
                "content": {
                    "name": name,
                    "email": email,
                    "number": number,
                    "company": company,
                },
            }

            StateConfig.objects.filter(session_id=session_id).update(
                state="init", bug=False, meeting_state=False
            )
            return JsonResponse([{"custom": message_payload}], safe=False)
        else:
            msg = "Please type your query."
            StateConfig.objects.filter(session_id=session_id).update(
                state="progress_msg", bug=False
            )
            return JsonResponse([{"text": msg}], safe=False)
    if state == "progress_select" and text.lower() == "/new":
        msg = "What is your name?"
        StateConfig.objects.filter(session_id=session_id).update(
            state="progress_name", name="", number="", email="", company=""
        )
        return JsonResponse([{"text": msg}], safe=False)

    if (
        state == "progress_select"
        and text.lower() != "/new"
        and text.lower() != "/forward"
    ):
        if bug:
            msg = "Please rephrase your response in correct format. If you are stuck, type '/cancel'"
            return JsonResponse([{"text": msg}], safe=False)
        else:
            msg = "Please rephrase your response in correct format."
            StateConfig.objects.filter(session_id=session_id).update(bug=True)
            return JsonResponse([{"text": msg}], safe=False)

    if state == "init":
        url = "http://localhost:5005/model/parse"
        letters = string.ascii_lowercase
        payload = json.dumps({"text": text})
        headers = {"Content-Type": "application/json"}

        respond = requests.request("POST", url, headers=headers, data=payload)
        res = respond.json()
        last_intent = res["intent"]["name"]
        print(last_intent)
        # url = "http://localhost:5005/webhooks/rest/webhook"
        # letters = string.ascii_lowercase
        # sender = "".join(random.choice(letters) for i in range(3))
        # payload = json.dumps({"message": text, "sender": sender})
        # headers = {"Content-Type": "application/json"}

        # response = requests.request("POST", url, headers=headers, data=payload)
        # res = json.loads(response.text)
        # last_intent = res[0]["text"]
        # print(last_intent)
        if last_intent == "input":
            if name and email and number and company:
                msg = "If you want to use existing details, type '/forward', and if you want to type new information type '/new'."
                StateConfig.objects.filter(session_id=session_id).update(
                    state="progress_select"
                )
                return JsonResponse([{"text": msg}], safe=False)
            else:
                msg = "What is your name?"
                StateConfig.objects.filter(session_id=session_id).update(
                    state="progress_name", name="", number="", email="", company=""
                )
                return JsonResponse([{"text": msg}], safe=False)
        elif last_intent == "lead":
            if name and email and number and company:
                msg = "If you want to use existing details, type '/forward', and if you want to type new information type '/new'."
                StateConfig.objects.filter(session_id=session_id).update(
                    state="progress_select", lead_state=True
                )
                return JsonResponse([{"text": msg}], safe=False)
            else:
                msg = "What is your name?"
                StateConfig.objects.filter(session_id=session_id).update(
                    state="progress_name", lead_state=True
                )
                return JsonResponse([{"text": msg}], safe=False)

        elif text.lower() == "/meeting":
            if name and email and number and company:
                msg = "If you want to use existing details, type '/forward', and if you want to type new information type '/new'."
                StateConfig.objects.filter(session_id=session_id).update(
                    state="progress_select", meeting_state=True
                )
                return JsonResponse([{"text": msg}], safe=False)

            else:
                msg = "What is your name?"
                StateConfig.objects.filter(session_id=session_id).update(
                    state="progress_name", meeting_state=True
                )
                return JsonResponse([{"text": msg}], safe=False)

        else:
            message_payload = {
                "purpose": "utter",
                "content": {
                    "intent": last_intent,
                    "text": text,
                    "confidence": confidence,
                },
            }
            return JsonResponse([{"custom": message_payload}], safe=False)
    elif state == "progress_name":
        if len(text) > 10 or re.search(r"\s", text):
            if bug:
                msg = "Please rephrase your response in correct format. If you are stuck, type '/cancel'"
                return JsonResponse([{"text": msg}], safe=False)
            else:
                msg = "Please rephrase your response in correct format."
                StateConfig.objects.filter(session_id=session_id).update(bug=True)
                return JsonResponse([{"text": msg}], safe=False)
        else:
            msg = "What is your contact number?"
            StateConfig.objects.filter(session_id=session_id).update(
                state="progress_number", name=text, bug=False
            )
            return JsonResponse([{"text": msg}], safe=False)

    elif state == "progress_number":
        if len(text) > 9 and len(text) < 13 and text.isdigit():
            msg = "What is your email address?"
            StateConfig.objects.filter(session_id=session_id).update(
                state="progress_email", number=text, bug=False
            )
            return JsonResponse([{"text": msg}], safe=False)
        else:
            if bug:
                msg = "Please rephrase your response in correct format. If you are stuck, type '/cancel'."
                return JsonResponse([{"text": msg}], safe=False)
            else:
                msg = "Please rephrase your response in correct format."
                StateConfig.objects.filter(session_id=session_id).update(bug=True)
                return JsonResponse([{"text": msg}], safe=False)

    elif state == "progress_email":
        regex = "^[a-z0-9]+[@]\w+[.]\w{2,3}$"
        if re.search(regex, text):
            msg = "What is your company?"
            StateConfig.objects.filter(session_id=session_id).update(
                state="progress_company", email=text, bug=False
            )
            return JsonResponse([{"text": msg}], safe=False)

        else:
            if bug:
                msg = "Please rephrase your response in correct format. If you are stuck, type '/cancel'"
                return JsonResponse([{"text": msg}], safe=False)
            else:
                msg = "Please rephrase your response in correct format."
                StateConfig.objects.filter(session_id=session_id).update(bug=True)
                return JsonResponse([{"text": msg}], safe=False)

    elif state == "progress_company":
        if lead_state:
            file_id = str(uuid.uuid4())
            msg = (
                "Thank you for your interest, your details are forwarded to our backend. Your file number is "
                + file_id
                + " and you will soon receive soon email on your email id for further process"
            )

            message_payload = {
                "purpose": "lead",
                "content": {
                    "name": name,
                    "email": email,
                    "number": number,
                    "company": company,
                    "file_id": file_id,
                    "response": msg,
                },
            }

            StateConfig.objects.filter(session_id=session_id).update(
                bug=False, state="init", company=text, lead_state=False
            )
            return JsonResponse([{"custom": message_payload}], safe=False)

        elif meeting_state:
            message_payload = {
                "purpose": "meeting",
                "content": {
                    "name": name,
                    "email": email,
                    "number": number,
                    "company": text,
                },
            }
            StateConfig.objects.filter(session_id=session_id).update(
                bug=False, state="init", company=text, meeting_state=False
            )
            return JsonResponse([{"custom": message_payload}], safe=False)

        else:
            msg = "Thanks for your sharing information. Please type your query."
            StateConfig.objects.filter(session_id=session_id).update(
                bug=False, state="progress_msg", company=text
            )
            return JsonResponse([{"text": msg}], safe=False)

    elif state == "progress_msg":
        msg = "Thank you for your query. Your query has been forwarded to our team member. You will shortly receive a reply on your email."
        message_payload = {
            "purpose": "message",
            "content": {
                "name": name,
                "email": email,
                "number": number,
                "company": company,
                "content": text,
            },
        }
        StateConfig.objects.filter(session_id=session_id).update(
            bug=False, state="init", msg=text
        )
        return JsonResponse([{"text": msg}, {"custom": message_payload}], safe=False)

    # return JsonResponse({"text": "asdf"})


def correct_sentence_spelling(sentence):
    sentence = TextBlob(sentence)
    result = sentence.correct()
    return result


def intent_analysis(request):
    file = request.FILES["file"]
    with open("static/analysis/" + file.name, "wb+") as destination:
        for chunk in file.chunks():
            destination.write(chunk)

    with open("static/analysis/" + file.name, "r") as f:
        reader = csv.reader(f)
        rows = list(reader)

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="data.csv"'
    for index, line in enumerate(rows):
        text = line[0]

        writer = csv.writer(response)

        url = "http://localhost:5005/model/parse"
        letters = string.ascii_lowercase
        payload = json.dumps({"text": text})
        headers = {"Content-Type": "application/json"}

        respond = requests.request("POST", url, headers=headers, data=payload)
        res = respond.json()

        writer.writerow(
            [
                text,
                correct_sentence_spelling(text),
                res["intent"]["name"],
                res["intent"]["confidence"],
                respond.elapsed.total_seconds(),
            ]
        )

    return response


@csrf_exempt
def product_register(request):
    if request.method == "POST":
        intent = request.POST.get("intent")

        intents = IntentConfig.objects.all()
        intents.update(is_product=False)

        intents = IntentConfig.objects.filter(intent_name=intent)
        intents.update(is_product=True)

        previous_url = request.META.get("HTTP_REFERER")
        return HttpResponseRedirect(previous_url)
