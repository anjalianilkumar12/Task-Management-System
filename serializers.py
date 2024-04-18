from rest_framework import serializers
from .models import Task, TaskLog, Project, Team
from user.models import User
from django.utils import timezone
from django.db.models import Sum

class CreateTaskSerializer(serializers.ModelSerializer):
    total_working_hours = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = ['id','user','title','description','status','project_name','estimated_start_date','estimated_end_date','estimated_hour','total_working_hours']
        
    def validate(self, attrs):
        estimated_start_date = attrs.get('estimated_start_date')
        estimated_end_date = attrs.get('estimated_end_date')

        if estimated_start_date > estimated_end_date:
            raise serializers.ValidationError(" Estimated end date should not be earlier than the estimated start date")
        
        return attrs
    
    def get_total_working_hours(self, id):
        
        task_id=id.id
        task_logs = TaskLog.objects.filter(task=task_id, start_time__isnull=False, end_time__isnull=False)
        total_working_hours = task_logs.aggregate(Sum('working_hours'))['working_hours__sum']
        return total_working_hours

    
class TaskLogSerializer(serializers.ModelSerializer):
    total_working_hours = serializers.SerializerMethodField()

    class Meta:
        model = TaskLog
        fields = ['id','task','start_time','end_time','total_working_hours','is_expired']
        read_only_fields = [ 'end_time',  'is_expired','total_working_hours']

    def create(self, validated_data):
        task_id = validated_data.pop('task', None)
        task = Task.objects.get(pk=task_id.id)
        ongoing_task_log = TaskLog.objects.filter(task=task, end_time__isnull=True).first()
    
        if ongoing_task_log:
            raise serializers.ValidationError("Cannot start a new task. Finish the ongoing task first.")

        start_task = TaskLog.objects.create(task=task, **validated_data)
        start_task.start_timer()

        return start_task
    
    def get_total_working_hours(self, obj):
        return obj.calculate_total_working_hours()
    

class ProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = ['id','name','duration','team','project_lead']


class TeamSerializer(serializers.ModelSerializer):

    class Meta:
        model = Team
        fields = ['id','team_lead','name']