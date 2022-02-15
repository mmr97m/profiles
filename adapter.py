from allauth.account.adapter import DefaultAccountAdapter
from django.http import Http404
from profiles.models import EmployeeProfile, ManagerProfile
from django.urls import reverse

class MyAccountAdapter(DefaultAccountAdapter):

    def get_login_redirect_url(self, request):
        user_type = request.user.user_type
        if user_type == 1:
            return reverse('profiles:edit')
        elif user_type == 2:
            return reverse('staff:index')
        elif user_type == 3:
            return reverse('staff:index')
        else:
            raise Http404("Ошибка авторизации! Повторите еще раз")
        
