from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import (
    TmTask,
    TmProject,
    TmUser,
    TmTaskInfo,
    TmStatus,
    TmPriority,
    TmTaskType,
)
from django.http import HttpResponse
from .forms import UserRegistrationForm, TmTaskForm, TmProjectForm, TmTaskInfoForm
from django.utils import timezone

from djangoproject.main_logger import set_up_logging

logger = set_up_logging()


@login_required(login_url="login")
def update(req, task, pk):
    logger.info(f"updating {task=} with {pk} {req.POST=}")
    match task:
        case "ticket":
            logger.info(f"Creating task form {pk}")
            tm_task = get_object_or_404(TmTask, tm_task_id=pk)
            task_info = TmTaskInfo.objects.get(
                tm_task_info_id=tm_task.tm_task_info.tm_task_info_id
            )
            username = {
                tm_task.tm_user.username,
                task_info.created_by.get_username, 
                task_info.modified_by.get_username,
            }
            logger.info("getting from instance ")
            task_form = TmTaskForm(instance=tm_task)
            task_info_form = TmTaskInfoForm(instance=tm_task.tm_task_info)
            id = task_form
            form = {"task_form": task_form, "task_info_form": task_info_form}

        case "project":
            logger.info("getting project")
            tm_project = TmProject.objects.get(tm_project_id=pk)
            project_form = TmProjectForm(instance=tm_project)
            username = {tm_project.created_by.username}
            form = {"project_form": project_form}
            id = project_form
            logger.info("got the project form")
    
    logger.info(f"username {username}")
    if req.user.username not in username:
        logger.info(f"{req.user.username} is not Authorize ")
        return redirect("ticket-list")

    if req.method == "POST":
        match task:
            case "project":
                logger.info(f"Upating project")
                project_instance = TmProjectForm(req.POST, instance=tm_project)
                return create_project(req, project_instance=project_instance)
            case "ticket":
                logger.info(f"Upating ticket")
                task_info_instance = TmTaskInfoForm(req.POST, instance=task_info)
                task_instance = TmTaskForm(req.POST, instance=tm_task)
                return create_ticket(req, task_info_instance, task_instance)

    context = {"form": form, "id": id}
    html = f"create_{task}.html"
    logger.info(f"rendering home")
    return render(req, html, context)


@login_required(login_url="login")
def delete(req, task, pk):
    logger.info(f"Deleting {task}")
    match task:
        case "ticket":
            obj = TmTask.objects.get(tm_task_id=pk)
            username = {obj.tm_task_info.created_by, obj.tm_task_info.modified_by}
            id = obj.tm_task_id
        case "project":
            obj = TmProject.objects.get(tm_project_id=pk)
            username = {obj.created_by.username}
            id = obj.tm_project_id

    if not (req.user.username not in username or req.user.is_staff):
        logger.info(f"{req.user.username} is not Authorize ")
        return redirect("home")

    if req.method == "POST":
        logger.info(f"Finally deleting")
        obj.delete()
        return redirect(f"{task}-list")
    logger.info(f"Asking finally")
    return render(req, "delete.html", {"obj": obj, "id": id})


### Home
@login_required(login_url="login")
def home(req):
    tm_tasks = TmTask.objects.all().order_by("tm_status")
    tm_task_form = TmTaskForm()
    tm_task_info_form = TmTaskInfoForm()
    users = TmUser.objects.all()

    if not req.user.is_authenticated:
        logger.info(f"User is not logged in")
        return redirect("login")

    logger.info(f"home {req.POST}")
    if req.method == "POST":
        handle_post_req(req)

    tm_task_form = TmTaskForm()

    if "edit" in req.POST:
        logger.info("request for edit")
        tm_task_form, tm_task_info_form = handle_edit_req(req, tm_task_form)
    
    logger.info(f"rendering home")
    context = {
        "tm_tasks": tm_tasks,
        "tm_task_form":tm_task_form,
        "tm_task_info_form":tm_task_info_form,
        "tm_tasks": tm_tasks,
        "users": users
    }
    return render(req, "home.html", context)


def handle_post_req(req):
    req.POST._mutable = True
    value = req.POST.pop("save", None)
    value = value[0] if value is not None else None

    logger.info(f"update home post request {value=}")
    if value == "ticket":
        req.POST["start_date"] = timezone.now().strftime("%Y-%m-%d")
        update(req, "ticket", req.POST.get("pk",None))


def handle_edit_req(req, tm_task_form):
    id = req.POST.pop("edit", None)
    logger.info(f"edit request {id=}")
    if id:
        tm_task = TmTask.objects.get(tm_task_id=id[0])
        tm_task_info = TmTaskInfo.objects.get(
            tm_task_info_id=tm_task.tm_task_info.tm_task_info_id)
        logger.info(f"got the object of tm_task and task_info")
        tm_task_info_form = TmTaskInfoForm(
            fields=[
                "task_title",
                "task_description",
                "created_by",
                "modified_by",
                "end_date",
                ],
                instance=tm_task_info)
        
        tm_task_form = TmTaskForm(
            fields=[
                "tm_status", 
                "tm_project", 
                "tm_priority", 
                "tm_user", 
                "tm_source_info", 
                "tm_task_type"
                ],
            instance=tm_task,
        )
        logger.info(f"returing with update forms")

    return tm_task_form, tm_task_info_form



### Login, Logout and Register
def register(req):
    logger.info(f"registing user.")
    logger.info(f"Welcome to lumenore task manager.")
    if req.method == "POST":
        form = UserRegistrationForm(req.POST)
        if form.is_valid():
            logger.info(f"User form is valied.")
            new_user = form.save()
            login(req, new_user)
            return redirect("home")
        else:
            logger.info(f"forms missed few things {form.errors}")
    else:
        form = UserRegistrationForm()
    return render(req, "register.html", {"form": form})


def login_view(req):
    logger.info(f"logging user")
    if req.method == "POST":
        form = AuthenticationForm(data=req.POST)
        if form.is_valid():
            user = form.get_user()
            login(req, user)
            return redirect("home")
        else:
            logger.info(f"forms missed few things {form.errors}")
    else:
        form = AuthenticationForm()
    logger.info(f"showing logging page")
    return render(req, "login.html", {"form": form})


@login_required(login_url="login")
def logout_view(req):
    logger.info(f"logging off")
    logger.info(f"Bye bye!")
    logout(req)
    return redirect("login")


### Create Project and Ticket


@login_required(login_url="login")
def create_project(req, project_instance=None):
    if req.method == "POST":
        if not project_instance:
            project_instance = TmProjectForm(req.POST)

        logger.info(f"create project {req.POST=} \n {project_instance.is_valid()=}")
        if project_instance.is_valid():
            project = project_instance.save(commit=False)
            project.created_by = TmUser.objects.get(username=req.user.username)
            project.save()
            return redirect("projects")
        logger.info(f"{project_instance.errors=}")
    else:
        project_form = TmProjectForm()
        form = {"project_form": project_form}
    return render(req, "create_project.html", {"form": form})


@login_required(login_url="login")
def create_ticket(req, task_info_instance=None, task_instance=None):
    
    
    task_form, task_info_form = TmTaskForm(), TmTaskInfoForm()
    form = {"task_form": task_form, "task_info_form": task_info_form}
    if req.method == "POST":
        if not (task_info_instance and task_instance):
            logger.info("creating instance")
            task_instance = TmTaskForm(req.POST)
            task_info_instance = TmTaskInfoForm(req.POST)

        logger.info(f"create ticket {req.POST=}")
        if task_instance.is_valid() and task_info_instance.is_valid():
            task_info_instance = task_info_instance.save(commit=False)
            task_info_instance.modified_on = timezone.now()
            task_info_instance.save()

            task_instance = task_instance.save(commit=False)
            task_instance.modified_on = timezone.now()
            task_instance.tm_task_info = task_info_instance
            task_instance.save()

            return redirect("home")
        logger.info(f"{task_instance.errors=} \n{task_info_instance.errors=}")

    return render(req, "create_ticket.html", {"form": form})


### Single Ticket
@login_required(login_url="login")
def ticket(req, pk):
    ticket = (
        TmTask.objects.filter(tm_task_id=pk)
        .values(
            "tm_task_id",
            "tm_task_info__task_title",
            "tm_task_info__task_description",
            "tm_task_info__created_by__username",
            "tm_task_info__modified_by__username",
            "tm_task_info__start_date",
            "tm_task_info__end_date",
            "tm_task_info__close_date",
            "tm_task_type__task_type_name",
            "tm_priority__priority_name",
            "tm_status__status_name",
            "tm_project__project_name",
        )
        .first()
    )
    logger.info(f"task fetch success")
    return render(req, "ticket.html", {"ticket": ticket})


### Ticket lists
@login_required(login_url="login")
def ticket_list(req):
    tickets = TmTask.objects.all()
    logger.info(f"task list fetch success")
    return render(req, "ticket_list.html", {"tickets": tickets})


### Project list
@login_required
def project_list(req):
    projects = TmProject.objects.all().values(
        "created_by__username", "tm_project_id", "project_name", "project_description","start_date","end_date"
    )
    logger.info(f"project list fetch success")
    return render(req, "project_list.html", {"projects": projects})


### Single Project


@login_required
def project(req, pk):
    logger.info(f"showing indivual project")
    project = (
        TmProject.objects.filter(tm_project_id=pk)
        .values(
            "created_by__username",
            "tm_project_id",
            "project_name",
            "project_description",
            "start_date",
            "end_date"
        )
        .first()
    )
    logger.info(f"project fetch success")
    return render(req, "project.html", {"project": project})


# def insert(req):
#     list1 = [
#         TmStatus(status_name="To be started",colour="blue"),
#         TmStatus(status_name="In progress",colour="yellow"),
#         TmStatus(status_name="Completed",colour="green"),
#     ]
#     list2 = [
#         TmTaskType(task_type_name="Bug",task_type_description="Its a bug"),
#         TmTaskType(task_type_name="Task",task_type_description="Its a task"),
#         TmTaskType(task_type_name="Issue",task_type_description="Its a issue"),
#     ]
#     list3 = [
#         TmPriority(priority_name="Low"),
#         TmPriority(priority_name="Medium"),
#         TmPriority(priority_name="High"),
#     ]

#     TmStatus.objects.bulk_create(list1)
#     TmTaskType.objects.bulk_create(list2)
#     TmPriority.objects.bulk_create(list3)

#     TmTaskTypes = TmTaskType.objects.all()
#     tmStatus = TmStatus.objects.all()
#     TmPriorityx = TmPriority.objects.all()

#     print(f"type{TmTaskTypes}")
#     print(f"status{tmStatus}")
#     print(f"TmPriority{TmPriorityx}")

#     return HttpResponse("Everything fine")
