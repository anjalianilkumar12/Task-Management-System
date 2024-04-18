from django.db import models
from user.models import User
from django.utils import timezone
from datetime import datetime
from django.db.models import Sum
import pytz
# Create your models here.



class Team(models.Model):
    team_lead= models.ForeignKey(User,on_delete = models.CASCADE)
    name = models.CharField(max_length=30)
   
        
class Project(models.Model):
    name = models.CharField(max_length=30)
    duration = models.CharField(max_length=30)
    team = models.ForeignKey(Team,on_delete=models.CASCADE)
    project_lead = models.ForeignKey(User,on_delete = models.CASCADE)


class Task(models.Model):
    STATUS_CHOICES = [
        ('TODO', 'To Do'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=30)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    project_name = models.ForeignKey(Project,on_delete = models.CASCADE)
    estimated_start_date = models.DateTimeField()
    estimated_end_date = models.DateTimeField()
    estimated_hour = models.TimeField()

    def __str__(self):
        return "{}-{}".format(self.id,self.title)
    

class TaskLog(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    working_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    is_expired = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.id} -{self.task}  - {self.start_time} to {self.end_time}"
    
    def calculate_total_working_hours(self):
        
        total_working_hours = TaskLog.objects.filter(task=self.task, start_time__isnull=False, end_time__isnull=False).aggregate(Sum('working_hours'))['working_hours__sum']
        return total_working_hours  
    
    def save(self, *args, **kwargs):
        
        if self.start_time and self.end_time:
            time_difference = self.end_time - self.start_time
            total_hours = (time_difference.total_seconds() / 3600)
            self.working_hours = round(total_hours, 2)
            
            estimated_hours = (
                    self.task.estimated_hour.hour * 3600 +
                    self.task.estimated_hour.minute * 60 +
                    self.task.estimated_hour.second
                ) / 3600
            
            task_id=self.task
            task_logs = TaskLog.objects.filter(task=task_id, start_time__isnull=False, end_time__isnull=False)
            total_working_hours = task_logs.aggregate(Sum('working_hours'))['working_hours__sum']
            
            if total_working_hours > estimated_hours:
                self.is_expired = True

        super().save(*args, **kwargs)
  
    def start_timer(self):
        self.start_time = timezone.now()
        self.end_time = None
        self.working_hours = None
        self.save()
   
    def resume_timer(self):
        
        if self.start_time and not self.end_time:
           
            self.end_time = timezone.now()
            self.save()
    