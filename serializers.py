from django.contrib.auth.hashers import make_password

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from company.models import Company
from events.serializers import EventSerializer
from profiles.models import CustomerProfile, User, ManagerProfile, EmployeeProfile, EmployeeCategory, WorkDay


class TokenObtainLifetimeSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        user_type = self.user.user_type

        try:
            manager = ManagerProfile.objects.get(user_id=self.user.id)
            company = Company.objects.filter(manager=manager)
            data['company_id'] = company[0].id
            data['company_name'] = company[0].name
        except:
            try:
                employee = EmployeeProfile.objects.get(user_id=self.user.id)
                data['company_id'] = employee.company.id
                data['company_name'] = employee.company.name
            except:
                data['company_id'] = None
                data['company_name'] = 'Компания'
        data['lifetime'] = int(refresh.access_token.lifetime.total_seconds())
        data['username'] = self.user.username
        data['user_type'] = self.user.user_type
        data['user_id'] = self.user.id
        return data


class TokenRefreshLifetimeSerializer(TokenRefreshSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = RefreshToken(attrs['refresh'])
        data['lifetime'] = int(refresh.access_token.lifetime.total_seconds())
        return data


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'username', 'password', 'email', 'phone', 'birthdate', 'avatar', 'gender', 'user_type')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class ManagerSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=True)

    class Meta:
        model = ManagerProfile
        fields = ['id', 'user', 'speciality']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        gender = user_data.pop('get_gender_display')
        user_type = user_data.pop('get_user_type_display')
        user_data['gender'] = gender
        user_data['user_type'] = user_type
        user = UserSerializer.create(UserSerializer(), validated_data=user_data)
        manager = ManagerProfile.objects.create(user=user, **validated_data)
        return manager


class WorkDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkDay
        fields = ['id', 'day_of_the_week', 'working_hours', 'day_type']


class EmployeeSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=True)
    category = serializers.SlugRelatedField(queryset=EmployeeCategory.objects.all(), slug_field='id')
    company = serializers.SlugRelatedField(queryset=Company.objects.all(), slug_field='id')
    work_schedule = WorkDaySerializer(many=True, required=False)

    class Meta:
        model = EmployeeProfile
        fields = ['id', "user", "category", "company", "work_schedule"]

    def create(self, validated_data):
        print(validated_data)
        user_data = validated_data.pop('user')
        gender_data = user_data.pop('gender')
        user_type_data = user_data.pop('user_type')
        work_schedules = validated_data.pop('work_schedule')
        result_schedule_ids = []
        user = User.objects.create(password=make_password(user_data.pop('password')), gender=gender_data,
                                   user_type=user_type_data, **user_data)
        employee = EmployeeProfile.objects.create(
            user=user,
            **validated_data)
        for work_schedule in work_schedules:
            work_day = WorkDay.objects.create(**work_schedule)
            result_schedule_ids.append(work_day.id)

        for work_day_id in result_schedule_ids:
            employee.work_schedule.add(work_day_id)
        instance = employee 
        return instance


class EmployeeCategorySerializer(serializers.ModelSerializer):
    company = serializers.SlugRelatedField(queryset=Company.objects.all(), slug_field='id')

    class Meta:
        model = EmployeeCategory
        fields = ('id', 'name', 'slug', 'company')


class EmployeeEventsSerializer(serializers.ModelSerializer):
    events = EventSerializer(many=True)

    class Meta:
        model = EmployeeProfile
        fields = ('id', 'user', 'category', 'company', 'events')


class CustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=True)
    creator = serializers.SlugRelatedField(queryset=ManagerProfile.objects.all(), slug_field='id')
    company = serializers.SlugRelatedField(queryset=Company.objects.all(), slug_field='id')

    class Meta:
        model = CustomerProfile
        fields = ('id', 'user', 'creator', 'company', 'address')

    def create(self, validated_data):
        print(validated_data)
        user_data = validated_data.pop('user')
        gender_data = user_data.pop('gender')
        user_type_data = 4

        user = User.objects.create(
            password=make_password(user_data.pop('password')),
            gender=gender_data,
            user_type=user_type_data,
            **user_data
        )

        customer = CustomerProfile.objects.create(
            user=user,
            **validated_data
        )
        instance = customer
        
        return instance
