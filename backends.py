from django.contrib.auth.backends import  ModelBackend
from django.db.models import Q

from . models import User


class UsernameBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None):
        try:
            user = User.objects.filter(Q(email=username) | Q(phone_number=username)).first()
            
            if user:
                if user.check_password(password):
                  return user
        except User.DoesNotExist:
            return None

    # def get_user(self, user_id):
    #     try:
    #         return User.objects.get(pk=user_id)
    #     except User.DoesNotExist:
    #         return None

    # def get_user_by_username(self, username):
    #     try:
    #         return User.objects.get(
    #             Q(email=username) | Q(phone_number=username) | Q(membership_number=username)
    #         )
    #     except User.DoesNotExist:
    #         return None