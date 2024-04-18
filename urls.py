from django.urls import path
from . import views
from rest_framework import routers
from .views import CreateTaskView, ListTaskView, TaskUpdateDeleteView, StartTaskView, ResumeTaskView, ExpiredTaskView, TaskLogListAPIView



urlpatterns=[
    path("create_task/",CreateTaskView.as_view(), name = 'create_task'),
    path("list_task/",ListTaskView.as_view(),name = 'list_task'),
    path("task_update_delete/<int:id>/",TaskUpdateDeleteView.as_view(),name = 'update_delete'),
    path("start_task/",StartTaskView.as_view(),name ='start_task'),
    path("resume_task/<int:id>/",ResumeTaskView.as_view(),name = 'resume_task'),
    path("expired_task/",ExpiredTaskView.as_view(),name = 'expired_task'),
    path("task_log_list/<int:id>/",TaskLogListAPIView.as_view(),name = 'task_log')
]
