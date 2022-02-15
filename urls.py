from django.urls import path, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()

router.register('users', views.UserViewSet)
router.register('managers', views.ManagerViewSet)
# router.register('employee', views.EmployeeViewSet, basename='employees')
# router.register('company', views.CompanyViewSet)
# router.register('employee-category', views.EmployeeCategoryViewSet)

urlpatterns = [
    # employees endpemployees/<int:pk>/oints
    path('employees/', views.EmployeeListView.as_view()),
    path('employees/add/', views.EmployeeAddView.as_view()),
    path('employees/<int:pk>/', views.EmployeeDetailView.as_view()),
    path('employees/<int:pk>/salary/', views.EmployeeSalaryView.as_view()),
    path('employees/category/', views.EmployeeCategoryListCreateView.as_view()),
    path('employees/events/', views.EmployeeEventsListView.as_view()),

    # customers endpoints
    path('customers/', views.CustomersListView.as_view()),
    path('customers/add/', views.CustomerAddView.as_view())
]

urlpatterns += router.urls