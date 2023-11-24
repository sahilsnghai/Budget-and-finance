from django.forms import (
    ModelForm,
    EmailField,
    Textarea,
    TextInput,
    DateInput,
    Select,
    ModelChoiceField,
)
from django.contrib.auth.forms import UserCreationForm
from .models import (
    TmSourceInfo,
    TmTaskType,
    TmUser,
    TmStatus,
    TmProject,
    TmPriority,
    TmTask,
    TmTaskInfo,
)

from django.utils.timezone import now


# User registration form
class UserRegistrationForm(UserCreationForm):
    email = EmailField()

    class Meta:
        model = TmUser
        fields = ("email", "username", "password1", "password2")


class TmProjectForm(ModelForm):
    class Meta:
        model = TmProject
        fields = ("project_name", "project_description", "start_date", "end_date")
        widgets = {
            "project_description": Textarea(attrs={"rows": 2, "cols": 35}),
            "start_date": DateInput(attrs={"type": "date"}),
            "end_date": DateInput(attrs={"type": "date"}),
        }


class TmTypeForm(ModelForm):
    class Meta:
        model = TmTaskType
        fields = ("task_type_name",)


class TmStatusForm(ModelForm):
    class Meta:
        model = TmStatus
        fields = ("status_name",)


class TmPriorityForm(ModelForm):
    class Meta:
        model = TmPriority
        fields = ("priority_name",)


# Ticket creation form
class TmTaskForm(ModelForm):
    class Meta:
        model = TmTask
        fields = "__all__"

    tm_status = ModelChoiceField(
        queryset=TmStatus.objects.all(),
        label="Status",
    )

    tm_project = ModelChoiceField(
        queryset=TmProject.objects.all(),
        label="Project",
    )

    tm_priority = ModelChoiceField(
        queryset=TmPriority.objects.all(),
        label="Priority",
    )

    tm_user = ModelChoiceField(queryset=TmUser.objects.all(), label="User")

    tm_source_info = ModelChoiceField(
        queryset=TmSourceInfo.objects.all(),
        label="Source Info",
        required=False,
    )

    tm_task_type = ModelChoiceField(
        queryset=TmTaskType.objects.all(),
        label="Task Type",
    )

    def __init__(self, *args, **kwargs):
        included_fields = kwargs.pop("fields", None)
        super().__init__(*args, **kwargs)
        if included_fields:
            for field_name in self.fields.copy():
                if field_name not in included_fields:
                    del self.fields[field_name]


class TmTaskInfoForm(ModelForm):
    class Meta:
        model = TmTaskInfo
        fields = (
            "task_title",
            "task_description",
            "created_by",
            "modified_by",
            "end_date",
            "start_date",
            "close_date",
        )
        widgets = {
            "task_title": Textarea(
                attrs={"rows": 3, "cols": 40}
            ),
            "task_description": Textarea(
                attrs={"rows": 3, "cols": 0}
            ),
            "start_date": DateInput(attrs={"type": "date"}),
            "created_by": Select(),
            "modified_by": Select(),
            "end_date": DateInput(attrs={"type": "date"}),
            "close_date": DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        included_fields = kwargs.pop("fields", None)
        super().__init__(*args, **kwargs)

        if included_fields:
            for field_name in self.fields.copy():
                if field_name not in included_fields:
                    del self.fields[field_name]
