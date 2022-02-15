from django.shortcuts import get_object_or_404
from rest_framework import generics, viewsets
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenViewBase
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from events.models import Event
from profiles import serializers

from profiles.serializers import (
    CustomerSerializer,
    EmployeeEventsSerializer,
    UserSerializer,
    ManagerSerializer, 
    EmployeeSerializer, 
    EmployeeCategorySerializer
)
from profiles.models import (
    CustomerProfile,
    User, 
    EmployeeProfile, EmployeeCategory, 
    SubManagerProfile, 
    ManagerProfile
)
from company.serializers import CompanySerializer
from company.models import Company

from profiles.serializers import TokenObtainLifetimeSerializer, TokenRefreshLifetimeSerializer
from .permissions import IsAdminOrReadOnly, IsManager, IsManagerOrReadOnly


class TokenObtainPairView(TokenViewBase):
    """
        Return JWT tokens (access and refresh) for specific user based on username and password.
    """
    serializer_class = TokenObtainLifetimeSerializer


class TokenRefreshView(TokenViewBase):
    """
        Renew tokens (access and refresh) with new expire time based on specific user's access token.
    """
    serializer_class = TokenRefreshLifetimeSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    permission_classes = [IsAuthenticated, IsManager]
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ManagerViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = ManagerProfile.objects.all()
    serializer_class = ManagerSerializer

    def get_queryset(self):  # added string
        try:
            if self.request.user.user_type == 1:
                return super().get_queryset().filter(user_id=self.request.user.id)
            else:
                raise Exception()
        except:
            return super().get_queryset().none()


class EmployeeAddView(generics.CreateAPIView):
    """
        Функция:
            Создает профиль нового сотрудника

        Возвращает:
            Данные сотрудника

        method: POST
    """
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated, IsManager]
    queryset = EmployeeProfile.objects.all()


class EmployeeListView(generics.ListAPIView):
    """
        Возвращает:
            Список сотрудников компании
            method: GET
    """
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated, IsManager]

    def get_queryset(self):  # added string
        company = Company.objects.filter(managers__user=self.request.user)
        return EmployeeProfile.objects.filter(category__company__in=company)


class EmployeeDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
            method: GET
            Возвращает:
                Все данные о конкретном сотруднике.
            
            method: PUT 
            Функция:
                Полное обновление данных
            Возвращает:
                Все данные о конкретном сотруднике.
            
            method: PATCH
            Функция:
                Частичное обновление данных
            Возвращает:
                Все данные о конкретном сотруднике.
            
            method: DELETE
            Функция:
                Удаление данных
    """
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated, IsManagerOrReadOnly]

    def get_queryset(self):
        company = Company.objects.filter(managers__user=self.request.user)
        return EmployeeProfile.objects.filter(category__company__in=company)


class EmployeeCategoryListCreateView(generics.ListCreateAPIView):
    """
        method: GET
        Возвращает:
            Список категории сотрудников компании
        
        method: POST
        Функция:
            Создает новую категории сотрудников
        Возвращает:
            Список категории сотрудников компании с новой категорией        
    """
    serializer_class = EmployeeCategorySerializer
    permission_classes = [IsAuthenticated, IsManagerOrReadOnly]

    def get_queryset(self):
        company = Company.objects.filter(managers__user=self.request.user)
        return EmployeeCategory.objects.filter(company__in=company)


class EmployeeEventsListView(generics.ListAPIView):
    """
        method: GET
        Возвращает:
            Список сотрудников и записей прикрепленных к ним
    """
    serializer_class = EmployeeEventsSerializer
    permission_classes = [IsAuthenticated, IsManager]

    def get_queryset(self):
        company = Company.objects.filter(managers__user=self.request.user)
        return EmployeeProfile.objects.filter(company__in=company)


class EmployeeSalaryView(generics.GenericAPIView):
    permission_class = [IsAuthenticated, IsManager]

    def get(self, request, pk):
        
        employee = get_object_or_404(EmployeeProfile, pk=pk)
        company = employee.company

        try:
            percentage = employee.salary.percentage_of_income
            percentage = 0 if percentage is None else percentage
        except:
            percentage = 0
        
        events = Event.objects.filter(company=company, employee=employee)

        employee_income = 0

        for event in events:
            event_income = event.service.price
            employee_income += (event_income / 100) * percentage

        try:
            employee_income += employee.salary.salary
        except:
            pass

        return Response({
            "employee_salary": employee_income
        })


class CustomerAddView(generics.CreateAPIView):
    """
        method: POST
        Функция:
            Создает профиль нового клиента
        Возвращает:
            Все данные созданного клиента
    """
    permission_classes = [IsAuthenticated, IsManager]
    serializer_class = CustomerSerializer
    queryset = CustomerProfile.objects.all()


class CustomersListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsManager]
    serializer_class = CustomerSerializer

    def get_queryset(self):
        company = Company.objects.filter(managers__user=self.request.user)
        return CustomerProfile.objects.filter(creator__company__in=company)


