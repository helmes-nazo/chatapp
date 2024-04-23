from django.contrib import messages
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Q, Subquery, OuterRef
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic import ListView

from .forms import (
    TalkForm,
    ChangeUsernameForm,
    ChangeEmailForm,
    ChangeIconForm,
    ChangePasswordForm
)

from .models import CustomUser, Talk


User = get_user_model()


def index(request):
    return render(request, "myapp/index.html")


# class SignUpView(generic.CreateView):
#     form_class = SignUpForm
#     model = CustomUser
#     success_url = reverse_lazy('index')
#     template_name = 'myapp/signup.html'


# class LoginView(LoginView):
#     form_class = LoginForm
#     template_name = 'myapp/login.html'


# ヒント：自分以外を抜き出す→annotateでユーザーごとにTalkの最新のものをひっつける→order_byでソート
# 現在のものはorder_byを二重に用いているため計算量が多そう
@login_required
def friends(request):
    user = request.user    

    latest_messages_subquery = (
        Talk.objects.filter(
            Q(talk_from=OuterRef('pk'), talk_to=user) | Q(talk_from=user, talk_to=OuterRef('pk'))
        ).order_by('-time').values('talk', 'time')[:1]
    )

    friends = (
        User.objects.exclude(id=user.id)
        .annotate(
            latest_talk=Subquery(latest_messages_subquery.values('talk')),
            latest_talk_time=Subquery(latest_messages_subquery.values('time'))
        )
        .order_by('-latest_talk_time')
    )

    return render(request, "myapp/friends.html", {"friends": friends})

class TalkRoom(LoginRequiredMixin, ListView):
    model = Talk
    template_name = 'myapp/talk_room.html'
    context_object_name = 'talk'

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        queryset = Talk.objects.filter(talk_from=user_id, talk_to=self.request.user.id) | Talk.objects.filter(talk_from=self.request.user.id, talk_to=user_id)
        return queryset.order_by('time')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.kwargs['user_id']
        context['form'] = TalkForm()
        context['friend'] = User.objects.get(id=user_id).username
        return context

    def post(self, request, user_id):
        form = TalkForm(request.POST)
        if form.is_valid():
            talk = form.cleaned_data['talk']
            Talk.objects.create(talk=talk, talk_from=request.user, talk_to_id=user_id)
            return redirect('talk_room', user_id=user_id)
        else:
            context = {'form': form}
            return render(request, self.template_name, context)

@login_required
def setting(request):
    return render(request, 'myapp/setting.html')

@login_required
def change_username(request):
    if request.method == 'POST':
        form = ChangeUsernameForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('setting')
    else:
        form = ChangeUsernameForm(instance=request.user)
    return render(request, 'myapp/change_username.html', {'form': form})

@login_required
def change_email(request):
    user_email = request.user.email

    if request.method == 'POST':
        form = ChangeEmailForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, request.user)
            return redirect('setting')
    else:
        form = ChangeEmailForm(instance=request.user, initial={'email': '', 'email_confirm': ''})
    
    return render(request, 'myapp/change_email.html', {'form': form, 'user_email': user_email})

@login_required
def change_icon(request):
    if request.method == 'POST':
        form = ChangeIconForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('setting')
    else:
        form = ChangeIconForm(instance=request.user)
    
    return render(request, 'myapp/change_icon.html', {'form': form})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'パスワードが変更されました。')
            return redirect('setting')
    else:
        form = ChangePasswordForm(request.user)
    return render(request, 'myapp/change_password.html', {'form': form})


class CustomLogoutView(LogoutView):
    next_page = ''
