from django.db.models import (
    Model,
    AutoField,
    CharField,
    EmailField,
    DateTimeField,
    IntegerField,
    BooleanField,
    TextField,
    ForeignKey,
    SET_DEFAULT,
    SET_NULL,
    CASCADE

) 
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.contrib.auth import get_user_model
from django.utils.timezone import now


class TmUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email or not username:
            raise ValueError("The Email/Username field must be set")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password):
        user = self.create_user(username, email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class TmUser(AbstractBaseUser, PermissionsMixin):
    tm_user_id = AutoField(primary_key=True)
    username = CharField(max_length=255, unique=True)
    email = EmailField(max_length=255, unique=True)
    created_on = DateTimeField(default=now, editable=False)
    modified_by = IntegerField(null=True, blank=True)
    modified_on = DateTimeField(null=True, blank=True)
    is_active = BooleanField(default=True)
    is_staff = BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = TmUserManager()

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        """On save, update timestamps"""
        if not self.tm_user_id:
            self.created = now()
        self.modified = now()
        return super(TmUser, self).save(*args, **kwargs)


class TmSourceInfo(Model):
    tm_source_info_id = AutoField(primary_key=True)
    source_info_name = CharField(max_length=255)
    created_on = DateTimeField(default=now, editable=False)
    modified_on = DateTimeField(default=now)
    is_active = BooleanField(default=True)

    def __str__(self):
        return self.source_info_name


class TmTaskInfo(Model):
    default_user = get_user_model().objects.get(username="ssjain")
    tm_task_info_id = AutoField(primary_key=True)
    task_title = CharField(max_length=255)
    task_description = TextField(null=True, blank=True)
    start_date = DateTimeField(default=now)
    end_date = DateTimeField(default=now)
    close_date = DateTimeField(default=now, blank=True)
    label = CharField(max_length=255, null=True, blank=True)
    created_by = ForeignKey(
        TmUser,
        on_delete=SET_DEFAULT,
        default=default_user,
        null=True,
        related_name="reporter",
    )
    created_on = DateTimeField(default=now, editable=False)
    modified_by = ForeignKey(
        TmUser,
        on_delete=SET_DEFAULT,
        default=default_user,
        null=True,
        blank=True,
        related_name="assignee",
    )
    modified_on = DateTimeField(default=now, blank=True)
    is_active = BooleanField(default=True)

    def __str__(self):
        return self.task_title

    def save(self, *args, **kwargs):
        """On save, update timestamps"""
        if not self.tm_task_info_id:
            self.created = now()
        self.modified = now()
        return super(TmTaskInfo, self).save(*args, **kwargs)


class TmTaskType(Model):
    tm_task_type_id = AutoField(primary_key=True)
    task_type_name = CharField(max_length=250)
    task_type_description = TextField()
    created_on = DateTimeField(default=now, editable=False)
    modified_on = DateTimeField(default=now)
    is_active = BooleanField(default=True)

    def __str__(self):
        return self.task_type_name


class TmStatus(Model):
    tm_status_id = AutoField(primary_key=True)
    status_name = CharField(max_length=255, null=True, blank=True)
    colour = CharField(max_length=255, default="green")
    created_on = DateTimeField(default=now, editable=False)
    modified_on = DateTimeField(default=now)
    is_active = BooleanField(default=True)

    def __str__(self):
        return self.status_name

    def save(self, *args, **kwargs):
        """On save, update timestamps"""
        if not self.tm_status_id:
            self.created = now()
        self.modified = now()
        return super(TmStatus, self).save(*args, **kwargs)


class TmProject(Model):
    tm_project_id = AutoField(primary_key=True)
    project_name = CharField(max_length=255)
    project_description = TextField()
    start_date = DateTimeField(null=True, blank=True, default=now)
    end_date = DateTimeField(null=True, blank=True)
    created_by = ForeignKey(
        TmUser, on_delete=SET_NULL, null=True, related_name="project_created_by"
    )
    created_on = DateTimeField(default=now, editable=False)
    modified_by = ForeignKey(
        TmUser, on_delete=SET_NULL, null=True, related_name="project_modified_by"
    )
    modified_on = DateTimeField(default=now)

    def __str__(self):
        return self.project_name

    def save(self, *args, **kwargs):
        """On save, update timestamps"""
        if not self.tm_project_id:
            self.created = now()
        self.modified = now()
        return super(TmProject, self).save(*args, **kwargs)


class TmPriority(Model):
    tm_priority_id = AutoField(primary_key=True)
    priority_name = CharField(max_length=255, null=True, blank=True)
    created_on = DateTimeField(default=now, editable=False)
    modified_on = DateTimeField(default=now)
    is_active = BooleanField(default=True)

    def __str__(self):
        return self.priority_name


class TmTask(Model):
    tm_task_id = AutoField(primary_key=True)
    tm_task_info = ForeignKey(
        TmTaskInfo, on_delete=CASCADE, null=True, blank=True
    )
    tm_status = ForeignKey(TmStatus, on_delete=CASCADE)
    tm_project = ForeignKey(TmProject, on_delete=CASCADE)
    tm_priority = ForeignKey(TmPriority, on_delete=CASCADE)
    tm_user = ForeignKey(TmUser, on_delete=CASCADE, null=True, blank=True)
    tm_source_info = ForeignKey(
        TmSourceInfo, on_delete=CASCADE, null=True, blank=True
    )
    tm_task_type = ForeignKey(TmTaskType, on_delete=CASCADE)
    created_on = DateTimeField(default=now, editable=False)
    modified_on = DateTimeField(auto_now=True)
    is_active = BooleanField(default=True)

    def __str__(self):
        return f"{self.tm_task_info.task_title} - {self.tm_project.project_name}"
