from django.db import models
from django.contrib.auth.models import AbstractUser,UserManager as AbstractUserManager
from django.utils import timezone
# Create your models here.


class UserManager(AbstractUserManager):
    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given  email, and password.
        """
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
     
    def create_user(self,email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user( email=email, password=password, **extra_fields)
    
    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):

    USER_TYPE = [
        ('USER', 'user'),
        ('ProjectManager', 'project manager'),
        ('TeamLead', 'team lead'),
    ]
    address = models.CharField(max_length=50)
    user_type= models.CharField(max_length=20, choices=USER_TYPE,null=True,blank=True)
    phone_number = models.CharField(max_length=15,unique=True)
    date_of_joining = models.DateField(blank=True,null=True)
    date_of_birth = models.DateField(blank=True,null=True)
    department = models.CharField(max_length=30)
    designation = models.CharField(max_length=30)
    email=models.EmailField(unique=True)
    username=models.CharField(unique=False,blank=True,null=True,default=None)

    objects=UserManager()

    USERNAME_FIELD='email'
    REQUIRED_FIELDS=['phone_number']

    def __str__(self):
        return "{}-{}".format(self.id,self.email)
