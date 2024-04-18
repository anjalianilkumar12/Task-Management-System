from django.shortcuts import render
from rest_framework.response import Response
from .serializers import CreateTaskSerializer, TaskLogSerializer, ProjectSerializer, TeamSerializer
from . models import Task, TaskLog, Project, Team
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView, UpdateAPIView, RetrieveAPIView
from rest_framework import viewsets
from rest_framework.decorators import action
from django.db.models import Sum
# Create your views here.


class CreateTaskView(CreateAPIView):
    queryset = Task.objects.all()
    serializer_class = CreateTaskSerializer

    def post(self,request):
        serializer = CreateTaskSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                {"status": True, "message": "Task Created Successfully", "data": serializer.data}
            )


class ListTaskView(ListAPIView):
    serializer_class = CreateTaskSerializer

    def get_queryset(self):
        user = self.request.user.id
        queryset = Task.objects.filter(user=user)
        date = self.request.query_params.get('date', '')
        status=self.request.query_params.get('status', '')

        if date:
            queryset = Task.objects.filter(user=user,estimated_start_date=date)
        
        if status:
            queryset = Task.objects.filter(user=user,status__icontains=status)
            
        return queryset
    

class TaskUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = CreateTaskSerializer
    lookup_field = 'id'

    def retrieve(self, request, *args, **kwargs):
        user = self.request.user
        instance = self.get_object()

        if user != instance.user:
            return Response({"message": "You can't view this Task."}, status=403)
        
        serializer = self.get_serializer(instance)
        return Response({"message": "Task details retrieved successfully.", "data": serializer.data})

    def update(self, request, *args, **kwargs):
        user = self.request.user
        instance = self.get_object()

        if user != instance.user:
            return Response({"message": "You can't update this Task."}, status=403)

        response = super().update(request, *args, **kwargs)
        serializer = self.get_serializer(instance)
        return Response({"message": "Task successfully updated.", "data": serializer.data})

    def destroy(self, request, *args, **kwargs):
        user = self.request.user
        instance = self.get_object()

        if user != instance.user:
            return Response({"message": "You can't delete this Task."}, status=403)

        response = super().destroy(request, *args, **kwargs)
        serializer = self.get_serializer(instance)
        return Response({"message": "Task successfully deleted.", "data": serializer.data})
    

class StartTaskView(CreateAPIView):
    queryset = TaskLog.objects.all()
    serializer_class = TaskLogSerializer


class ResumeTaskView(UpdateAPIView):
    queryset = TaskLog.objects.all()
    serializer_class = TaskLogSerializer
    lookup_field = 'id'
 
    def update(self, request, *args, **kwargs):
        user = self.request.user
        instance = self.get_object()
        task_detail=TaskLog.objects.filter(task__user=user,task=instance.task,start_time=instance.start_time)
        if task_detail:
            
            instance.resume_timer()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        else :
            return Response({"message": "You can't update task on this id."}, status=403)
    

class ExpiredTaskView(ListAPIView):
    queryset = TaskLog.objects.all()
    serializer_class = TaskLogSerializer

    def get_queryset(self):
        user = self.request.user
        query_set = TaskLog.objects.filter(task__user=user, is_expired=True).order_by('task').distinct('task')
        return query_set
    

class TaskLogListAPIView(RetrieveAPIView):
    queryset = TaskLog.objects.all()
    serializer_class = TaskLogSerializer
    lookup_field = 'id'

    def retrieve(self, request, *args, **kwargs):
        task_id = self.kwargs.get('id')
        user = self.request.user.id
        task_logs = TaskLog.objects.filter(task__user=user, task=task_id, start_time__isnull=False, end_time__isnull=False)
        
        if task_logs:

            total_work_hours = task_logs.aggregate(total_hours=Sum('working_hours'))['total_hours'] 
            working_hours = [
                {'start_time': log.start_time, 'end_time': log.end_time, 'hours': log.working_hours}
                for log in task_logs
            ]
            return Response({'task_id': task_id, 'working_hours': working_hours, 'total_working_hours': total_work_hours})
        else :
            return Response({"message": "You can't get this Tasklog."}, status=403)
        

class ProjectCreateTaskView(CreateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    
    def post(self,request):
        user = self.request.user
        if user.user_type!='TeamLead':
            return Response({"message":"Only Team Lead can create Project"},status=403)
        
        serializer = ProjectSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                {"status": True, "message": "Project Created Successfully", "data": serializer.data}
            )
        

class TeamCreateTaskView(CreateAPIView):
    queryset = Team.objects.all()
    serializer_class = ProjectSerializer
    
    def post(self,request):
        user = self.request.user
        if user.user_type!='TeamLead':
            return Response({"message":"Only Team Lead can create Team"},status=403)
        
        serializer = TeamSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                {"status": True, "message": "Team Created Successfully", "data": serializer.data}
            )