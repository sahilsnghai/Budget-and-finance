from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, Ticket, Status, Type, Priority, Project


# User registration form
class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField()
    name = forms.CharField(max_length=100)

    class Meta:
        model = UserProfile
        fields = ("name", "email", "username", "password1", "password2")


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('name', 'description')
        widgets = {
          'description': forms.Textarea(attrs={'rows':2, 'cols':35}),
        }


class TypeForm(forms.ModelForm):
    class Meta:
        model = Type
        fields = ['name']

class StatusForm(forms.ModelForm):
    class Meta:
        model = Status
        fields = ['name']

class PriorityForm(forms.ModelForm):
    class Meta:
        model = Priority
        fields = ('name',)
        
# Ticket creation form
class TicketForm(forms.ModelForm):

    class Meta:
        model = Ticket
        fields = (
            "title",
            "description",
            "reporter",
            "assignee",
            "type",
            "priority",
            "start_date",
            "end_date",
            "status",
            "project",
        )
        widgets = {
          'description': forms.Textarea(attrs={'rows':2, 'cols':35}),
        }

    status = forms.ModelChoiceField(queryset=Status.objects.all() ,label="Status")
    type = forms.ModelChoiceField(queryset=Type.objects.all(), label="Type")
    priority = forms.ModelChoiceField(queryset=Priority.objects.all(), label="Priority")
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    project = forms.ModelChoiceField(queryset=Project.objects.all(), label="Project")

    def __init__(self, *args, **kwargs):
        included_fields = kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)

        if included_fields:
            for field_name in self.fields.copy():
                if field_name not in included_fields:
                    del self.fields[field_name]
