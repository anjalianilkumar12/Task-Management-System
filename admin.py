from django.contrib import admin
from .models import Task, TaskLog, Project,Team
# Register your models here.

admin.site.register(Task)
admin.site.register(TaskLog)
admin.site.register(Project)
admin.site.register(Team)