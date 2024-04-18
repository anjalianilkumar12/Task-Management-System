from django.urls import path
from . import views
from . views import UserRegistrationView, UserLoginView, UserDetailsListView, UserDetailsView, ChangePasswordView, SendResetPasswordEmailView, ResetPasswordView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns=[
    path('refresh/', TokenRefreshView.as_view(), name ='token_refresh'),
    path('user_registration/', UserRegistrationView.as_view(), name = 'registration'),
    path('user_login/', UserLoginView.as_view(), name = 'login'),
    path('user_details_list/',UserDetailsListView.as_view(),name = 'detail_list'),
    path('user_details/<int:id>/',UserDetailsView.as_view(),name = 'details'),
    path('change_password/',ChangePasswordView.as_view(), name = 'change_password'),
    path('send_reset_password_email/',SendResetPasswordEmailView.as_view(),name = 'send_email'),
    path('reset_password/<uid>/<token>',ResetPasswordView.as_view(),name = 'reset_password'),
]