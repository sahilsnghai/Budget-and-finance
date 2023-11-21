from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Ticket, Project, UserProfile
from django.http import HttpResponse
from .forms import (
    UserRegistrationForm,
    TicketForm,
    ProjectForm,
)
from django.utils import timezone
# from djangoproject.main_logger import set_up_logging

# logger = set_up_logging()


@login_required(login_url="login")
def update(req, task, pk):
    match task:
        case "ticket":
            obj = Ticket.objects.get(ticketid=pk)
            username = obj.reporter.username
            form_class = TicketForm
            id = obj.ticketid
        case "project":
            obj = Project.objects.get(ticket_projectid=pk)
            form_class = ProjectForm
            username = obj.owner.username
            id = obj.ticket_projectid

    if req.user.username != username:
        return HttpResponse("Your are not allowed here!!")

    form = form_class(instance=obj)
    if req.method == "POST":
        form_instance = form_class(req.POST, instance=obj)
        if form_instance.is_valid():
            form_instance = form_instance.save(commit=False)
            if task == "ticket":
                form_instance.updated_time = timezone.now()
            form_instance.save()
        return redirect("home")
    context = {"obj": obj, "form": form, "id": id}
    html = f"create_{task}.html"
    return render(req, html, context)


@login_required(login_url="login")
def delete(req, task, pk):
    match task:
        case "ticket":
            obj = Ticket.objects.get(ticketid=pk)
            username = obj.reporter.username
            id = obj.ticketid
        case "project":
            obj = Project.objects.get(ticket_projectid=pk)
            username = obj.owner.username
            id = obj.ticket_projectid
    print(req.POST)
    if req.user.username != username:
        return HttpResponse("Your are not allowed here!!")

    if req.method == "POST":
        obj.delete()
        return redirect("home")
    return render(req, "delete.html", {"obj": obj, "id": id})


### Home


# @login_required
def home(req):
    tickets = Ticket.objects.all()
    projects = Project.objects.all()
    projectform = ProjectForm()

    if not req.user.is_authenticated:
        return redirect("login")

    # logger.info(f"context {req.context}")

    if req.method == "POST":
        handle_post_req(req)

    ticketform = TicketForm(
        fields=[
            "title",
            "description",
            "reporter",
            "assignee",
            "project",
            "type",
            "priority",
            "status",
            "end_date",
        ]
    )

    if "edit" in req.POST:
        ticketform = handle_edit_req(req, ticketform)

    context = {
        "tickets": tickets,
        "projects": projects,
        "ticketform": ticketform,
        "projectform": projectform,
    }
    return render(req, "home.html", context)


def handle_post_req(req):
    req.POST._mutable = True
    value = req.POST.pop("save", None)
    value = value[0] if value is not None else None
    if value == "project":
        create_project(req)
    elif value == "ticket":
        req.POST["start_date"] = timezone.now().strftime("%Y-%m-%d")
        create_ticket(req)
    elif value:
        handle_ticket_update(req, value)


def handle_ticket_update(req, value):
    ticket = get_object_or_404(Ticket, ticketid=value)
    post_data = req.POST.copy()
    ticketform = TicketForm(
        post_data,
        instance=ticket,
        fields=[
            "title",
            "description",
            "reporter",
            "assignee",
            "project",
            "type",
            "priority",
            "status",
            "end_date",
        ],
    )
    if ticketform.is_valid():
        ticketform.save()


def handle_edit_req(req, ticketform):
    id = req.POST.pop("edit", None)
    if id:
        ticket = Ticket.objects.get(ticketid=id[0])
        ticketform = TicketForm(
            fields=[
                "title",
                "description",
                "reporter",
                "assignee",
                "project",
                "type",
                "priority",
                "status",
                "end_date",
            ],
            instance=ticket,
        )
    return ticketform


### Login, Logout and Register


def register(req):
    if req.method == "POST":
        form = UserRegistrationForm(req.POST)
        if form.is_valid():
            new_user = form.save()
            login(req, new_user)
            return redirect("home")
    else:
        form = UserRegistrationForm()
    return render(req, "register.html", {"form": form})


def login_view(req):
    # logger.info(f"{req.context}")
    # logger.info(f"{req.headers}")
    # logger.info(f"{req.POST}")

    if req.method == "POST":
        form = AuthenticationForm(data=req.POST)
        # logger.info(f"{form.is_valid()=}")
        if form.is_valid():
            user = form.get_user()
            login(req, user)
            return redirect("home")
    else:
        form = AuthenticationForm()
        # logger.info("not authenticate")
    return render(req, "login.html", {"form": form})


@login_required
def logout_view(req):
    logout(req)
    return redirect("login")


### Create Project and Ticket


@login_required
def create_project(req):
    if req.method == "POST":
        form = ProjectForm(req.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = UserProfile.objects.get(username=req.user.username)
            project.save()
            return redirect("projects")
    else:
        form = ProjectForm()
    return render(req, "create_project.html", {"form": form})


@login_required
def create_ticket(req):
    # insert(req)
    if req.method == "POST":
        form = TicketForm(req.POST)
        print(req.POST)
        print(form.is_valid())
        if form.is_valid():
            try:
                form.save()
                return redirect("ticket-list")
            except Exception as e:
                return render(
                    req,
                    "create_ticket.html",
                    {"form": form, "error_message": str(e)},
                )

    else:
        form = TicketForm()

    return render(
        req,
        "create_ticket.html",
        {
            "form": form,
        },
    )


### Single Ticket


@login_required
def ticket(req, pk):
    ticket = (
        Ticket.objects.filter(ticketid=pk)
        .values(
            "ticketid",
            "title",
            "description",
            "reporter__username",
            "reporter__name",
            "assignee__name",
            "type__name",
            "priority__name",
            "start_date",
            "end_date",
            "status__name",
            "project__name",
        )
        .first()
    )
    print(ticket)
    return render(req, "ticket.html", {"ticket": ticket})


### Ticket lists


@login_required
def ticket_list(req):
    tickets = Ticket.objects.all()
    return render(req, "ticket_list.html", {"tickets": tickets})


### Project list


@login_required
def project_list(req):
    projects = Project.objects.all().values(
        "owner__name", "ticket_projectid", "name", "description"
    )
    return render(req, "project_list.html", {"projects": projects})


### Single Project


@login_required
def project(req, pk):
    project = (
        Project.objects.filter(ticket_projectid=pk)
        .values("owner__name", "ticket_projectid", "name", "description")
        .first()
    )
    return render(req, "project.html", {"project": project})


# def insert(req):
#     list1 = [
#         Status(name="To be started"),
#         Status(name="In progress"),
#         Status(name="Completed"),
#     ]
#     list2 = [
#         Type(name="Bug"),
#         Type(name="Task"),
#         Type(name="Issue"),
#     ]
#     list3 = [
#         Priority(name="Low"),
#         Priority(name="Medium"),
#         Priority(name="High"),
#     ]

#     Status.objects.bulk_create(list1)
#     Type.objects.bulk_create(list2)
#     Priority.objects.bulk_create(list3)

#     types = Type.objects.all()
#     status = Status.objects.all()
#     priority = Priority.objects.all()

#     print(f"type{types}")
#     print(f"status{status}")
#     print(f"priority{priority}")

#     return HttpResponse("Everything fine")
