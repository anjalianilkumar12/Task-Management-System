from django.shortcuts import render
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView, UpdateAPIView
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.validators import ValidationError
from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserDetailSerializer, ChangePasswordSerializer, SendResetPasswordEmailSerializer, ResetPasswordSerializer
from .models import User
from django.db.models import Q
# Create your views here.

class UserRegistrationView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]


class UserLoginView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]    

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data, context={"request" : request})
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(request, username=username, password=password)
        
        if not user:
             return Response({'error': 'Invalid Username or Password'}, status=status.HTTP_401_UNAUTHORIZED)

        if serializer.is_valid(raise_exception=True):
            return Response(serializer.data)
        

class UserDetailsListView(ListAPIView):
    serializer_class=UserDetailSerializer

    def get_queryset(self):
        user_id=self.request.user.id
        queryset=User.objects.filter(id=user_id)
        return queryset
    

class UserDetailsView(RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    lookup_field = 'id'

    def retrieve(self, request, *args, **kwargs):
        user=self.request.user
        instance = self.get_object()

        if user != instance:
           return Response({"message": "You can't view this profile."}, status=403)

        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        user=self.request.user
        instance = self.get_object()
        
        if user != instance:
            return Response({"message": "You can't  update this profile."}, status=403)

        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        user=self.request.user
        instance = self.get_object()

        if user != instance:
            return Response({"message": "You can't delete this profile."}, status=403)

        return super().destroy(request, *args, **kwargs)
    

class ChangePasswordView(CreateAPIView):
    
    def post(self,request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                {"status": True, "message": "Password changed successfully", "data": {}}
            )
    

class SendResetPasswordEmailView(CreateAPIView):

    def post(self,request):
        serializer = SendResetPasswordEmailSerializer(data = request.data)

        if serializer.is_valid(raise_exception=True):
            
            return Response(
                {"status": True, "message": "Password reset link sent to the registered email ", "data": {}}
            )
        

class ResetPasswordView(CreateAPIView):
    serializer_class = ResetPasswordSerializer

    def post(self,request,uid,token,url_path=r"reset_password/(?P<uid>\w+)/(?P<token>\w+)", url_name="reset_password",):
        serializer = ResetPasswordSerializer(data=request.data, context={"uid": uid, "token": token})

        if serializer.is_valid(raise_exception=True):
            return Response( 
                {"status": True, "message": "Password changed successfully", "data": {}})
               

    
              

    

        