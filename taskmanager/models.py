from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)

class Role(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class UserProfileManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password):
        user = self.create_user(username, email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)   
        return user


class UserProfile(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=100, help_text="Required. Enter your full name.")
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    objects = UserProfileManager()

    def __str__(self):
        return self.name


# Model for ticket status
class Status(models.Model):
    ticket_statusid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20, default="To be started")

    def __str__(self):
        return self.name


# Model for ticket type
class Type(models.Model):
    ticket_typeid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20, default="Bug")

    def __str__(self):
        return self.name


# Model for ticket priority
class Priority(models.Model):
    ticket_priorityid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20, default="Low")
    
    def __str__(self):
        return self.name


class Project(models.Model):
    ticket_projectid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    owner = models.ForeignKey(
        UserProfile, on_delete=models.SET_NULL, related_name="project_owner", null=True
    )

    def __str__(self):
        return self.name


# Ticket model
class Ticket(models.Model):
    ticketid = models.AutoField(primary_key=True, )
    title = models.CharField(max_length=200)
    description = models.TextField()
    reporter = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="reported_tickets"
    )
    assignee = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="assigned_tickets"
    )
    type = models.ForeignKey(Type, on_delete=models.CASCADE)
    priority = models.ForeignKey(Priority, on_delete=models.CASCADE)
    start_date = models.DateField(null=True)
    end_date = models.DateField()
    updated_time = models.DateTimeField(auto_now=True)
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    project = models.ForeignKey(
        Project, on_delete=models.SET_NULL, null=True, related_name="project_name"
    )

    def __str__(self):
        return self.title
