from django.contrib import admin
from .models import (
    TmUser,
    TmProject,
    TmPriority,
    TmSourceInfo,
    TmStatus,
    TmTaskInfo,
    TmTask,
    TmTaskType
)

# Register your models here.


admin.site.register(TmUser)
admin.site.register(TmProject)
admin.site.register(TmTask)
admin.site.register(TmTaskType)
admin.site.register(TmPriority)
admin.site.register(TmSourceInfo)
admin.site.register(TmStatus)
admin.site.register(TmTaskInfo)