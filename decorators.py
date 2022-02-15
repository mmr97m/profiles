from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseRedirect, Http404

from profiles.models import ManagerProfile, CompanyProfile


def sub_manager_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='login'):
    '''
    Decorator for views that checks that the logged in user is a student,
    redirects to the log-in page if necessary.
    '''
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.user_type == 2,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def manager_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='login'):
    '''
    Decorator for views that checks that the logged in user is a teacher,
    redirects to the log-in page if necessary.
    '''
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.user_type == 1,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def queryset_to_dict(queryset):
    b = []
    for i in queryset:
        b.append(i.pk)
    return b


def company_required(function):
    def wrap(request, *args, **kwargs):

        user = request.user
        manager = ManagerProfile.objects.get(user_id=user.id)
        manager_compnaies = CompanyProfile.objects.filter(manager_id=manager.id)
        manager_companies_id_list = queryset_to_dict(manager_compnaies)

        if kwargs["id"] in manager_companies_id_list:
            return function(request, *args, **kwargs)
        else:
            raise Http404("Нет доступа к событию {0}".format(kwargs["id"]))

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
