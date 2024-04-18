from rest_framework import serializers
from . models import User
from rest_framework.validators import ValidationError
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from django.db.models import Q
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from .emails import send_email
from django.conf import settings


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name','last_name','email','phone_number','address','user_type','date_of_joining','date_of_birth','department','designation']


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        style={"input_type": "password"},
        write_only=True,
        required=True,
        validators=[validate_password],
    )
    confirm_password = serializers.CharField(
        style={"input_type": "password"}, write_only=True
    )
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields=['id','first_name','last_name','email','password','confirm_password','address','user_type','phone_number','date_of_joining','date_of_birth','department','designation']

    def validate(self, attrs):
        password = attrs.get("password")
        phone_number = attrs.get("phone_number")
        email = attrs.get("email")
        confirm_password = attrs.pop("confirm_password")

        if password != confirm_password:
            raise serializers.ValidationError("Passwords doesn't match")
        
        self.user = User.objects.filter(phone_number=phone_number)
        self.email=User.objects.filter(email=email)
       
        if self.email:
            raise ValidationError("Email is already exist")
        if self.user:
            raise ValidationError("User with this credentials already exist")
        
        return attrs 
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name','last_name','phone_number','user_type']


class UserLoginSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField()
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    user = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['username', 'password', 'token' , 'user']

    def get_token(self, instance: dict) -> dict:
        """
        Returns refresh and access tokens
        """
        username = instance.get('username')
        user = User.objects.filter(Q(email=username)|Q(phone_number=username)).first()
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        return {"refresh": str(refresh)
               , "access": access_token}

    def validate(self, attrs: dict):
        username= attrs.get("username")
        password = attrs.get("password")
        self.request = self.context.get("request")
        self.user = User.objects.filter(Q(email=username)|Q(phone_number=username)).first()
        
        if not self.user:
            raise ValidationError("User with this username does not exist")
            
        return attrs

    def get_user(self, instance):
        if self.user:
            return UserSerializer(self.user, context={"request": self.request}).data
        

class ChangePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(style = {'input_type':'password'}, write_only = True, required = True)
    new_password = serializers.CharField(style = {'input_type':'password'}, write_only = True, required = True, validators = [validate_password])
    confirm_password = serializers.CharField(style = {'input_type':'password'}, write_only = True, required = True)
    
    class Meta:
        model = User
        fields = ['old_password', 'new_password', 'confirm_password']

    def validate(self,attrs):
        old_password = attrs.pop('old_password')
        new_password = attrs.pop('new_password')
        confirm_password = attrs.pop('confirm_password')
        user = self.context.get("request").user
        print(user)

        if old_password == new_password:
            raise serializers.ValidationError("Please enter a new password")
        if new_password != confirm_password:
            raise serializers.ValidationError("Passwords doesn't match")
        
        if not user.check_password(old_password):
            raise serializers.ValidationError("Old Password is wrong")
            
        attrs['password'] = new_password
        return attrs
    
    def create(self, validate_data: dict) -> dict:
        """
        create user with the details provided
        """
        user = self.context.get("request").user
        user.set_password(validate_data.get('password'))
        user.save()
            
        return user
    

class SendResetPasswordEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

    class Meta:
        fields = ['email']

    def validate(self, attrs: dict) -> dict:
        user = User.objects.filter(email=attrs.get('email')).last()
        if user is not None:
            uid = urlsafe_base64_encode(force_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            link = settings.CHANGE_PASSWORD_URL+uid+'/'+token

            # Send EMail
            body = 'Click Following Link to Reset Your Password '+link
            data = {
                    'subject': 'Reset Your Password',
                    'body': body,
                    'to_email': user.email
                }
            print(data)
            send_email(data)
        else:
            raise serializers.ValidationError("You are not a registered user")
            
        return attrs
    

class ResetPasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style = {"input" : "password"}, write_only = True, required = True, validators = [validate_password])
    confirm_password = serializers.CharField(style = {"input" : "password"}, write_only = True, required = True) 

    class Meta:
        model = User
        fields = ['password', 'confirm_password']
    
    def validate(self,attrs):
       
            password = attrs.get('password')
            confirm_password = attrs.get('confirm_password')
            uid = self.context.get('uid')
            token = self.context.get('token')

            if password != confirm_password:
                raise serializers.ValidationError("Password and Confirm Password doesn't match")
            id = smart_str(urlsafe_base64_decode(uid))
            user = User.objects.get(id=id)
          
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError('Token is not Valid or Expired')
            user.set_password(password)
            user.save()
            return attrs

        
        
        
        
        
