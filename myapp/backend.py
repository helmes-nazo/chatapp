from django.contrib.auth.backends import ModelBackend

class CustomAuthenticationBackend(ModelBackend):
    def user_can_access_friends(self, user):
        return user.is_authenticated and user.email_verified

    def authenticate(self, request, username=None, password=None, **kwargs):
        user = super().authenticate(request, username, password, **kwargs)
        if user and self.user_can_access_friends(user):
            return user
        return None