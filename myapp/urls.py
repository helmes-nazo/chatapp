from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path("login/", views.LoginView.as_view(), name="login"),
    path('friends/', views.friends, name="friends"),
    path("talk_room/<int:user_id>/", views.TalkRoom.as_view(), name="talk_room"),
    path("setting/", views.setting, name="setting"),
    path("setting/change_username/", views.change_username, name="change_username"),
    path("setting/change_email/", views.change_email, name="change_email"),
    path("setting/change_icon/", views.change_icon, name="change_icon"),
    path("setting/change_password/", views.change_password, name="change_password"),
    path('logout/', views.CustomLogoutView.as_view(), name='logout')
]