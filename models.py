from django.db import models
from django.contrib.auth.models import AbstractUser
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from slugify import slugify


class User(AbstractUser):
    USER_TYPE_CHOICES = (
        (1, 'Manager'),
        (2, 'Sub_Manager'),
        (3, 'Employee'),
        (4, 'Customer'),
    )

    GENDER_CHOICES = (
        (1, 'Мужской'),
        (2, 'Женский'),
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя',
        blank=True
    )
    last_name = models.CharField(
        max_length=150, 
        verbose_name='Фамилия', 
        blank=True
    )
    middle_name = models.CharField(
        max_length=150,
        verbose_name='Отчество', 
        blank=True
    )
    user_type = models.PositiveSmallIntegerField(
        choices=USER_TYPE_CHOICES, 
        blank=True, null=True,
        verbose_name="Тип пользователя"
    )
    birthdate = models.DateField(
        blank=True, null=True, 
        verbose_name="Дата рождения"
    )
    avatar = models.ImageField(
        upload_to="user_avatars/%Y/%m/%d", 
        blank=True, null=True, 
        verbose_name="Аватар"
    )
    gender = models.PositiveSmallIntegerField(
        choices=GENDER_CHOICES, 
        blank=True, null=True, 
        verbose_name="Пол"
    )
    # company = models.ManyToManyField(
    #     to='company.Company',
    #     related_name='users',
    #     verbose_name="Компания"
    # )
    phone = models.CharField(
        max_length=20, 
        blank=True, null=True,
        verbose_name="Телефон"
    )
    is_online = models.BooleanField(default=False)


class WorkDay(models.Model):

    DAYS_OF_THE_WEEK = (
        (1, 'ПН'),
        (2, 'ВТ'),
        (3, 'СР'),
        (4, 'ЧТ'),
        (5, 'ПТ'),
        (6, 'СБ'),
        (7, 'ВС')
    )

    DAY_TYPES = (
        (1, 'weekday'),
        (2, 'holiday'),
    )
    day_of_the_week = models.IntegerField(
        verbose_name='day of the week',
        choices=DAYS_OF_THE_WEEK
    )
    working_hours = models.IntegerField(
        validators= [
            MinValueValidator(0),
            MaxValueValidator(24)
        ]
    )
    day_type = models.PositiveSmallIntegerField(
        verbose_name='day type',
        choices=DAY_TYPES
    )

    def __str__(self) -> str:
        days = dict(self.DAYS_OF_THE_WEEK)
        return str(days[self.day_of_the_week])


class EmployeeProfile(models.Model):
    user = models.OneToOneField(
        to=get_user_model(),
        on_delete=models.CASCADE, 
        verbose_name='Пользователь'
    )
    category = models.ForeignKey(
        to='EmployeeCategory', 
        on_delete=models.CASCADE, 
        related_name="employee_category",
        verbose_name="Категория сотрудников"
    )
    company = models.ForeignKey(
        to='company.Company', 
        on_delete=models.CASCADE, 
        related_name="employees",
        verbose_name="Компания"
    )
    work_schedule = models.ManyToManyField(
        to=WorkDay, 
        verbose_name="График работы",
        related_name='employees'
    )

    def __str__(self):
        return " %s" % self.user.username

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"
    

class EmployeeSalary(models.Model):
    SALARY_TYPE_CHOICES = (
        (1, 'за день'),
        (2, 'за месяц')
    )
    employee = models.OneToOneField(
        to=EmployeeProfile,
        on_delete=models.CASCADE,
        related_name='salary',
        verbose_name='Сотрудник'
    )
    type = models.IntegerField(
        default=2, 
        choices=SALARY_TYPE_CHOICES,
        null=True, blank=True    
    )
    salary = models.PositiveIntegerField(
        null=True, blank=True
    )
    percentage_of_income = models.IntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ],
        null=True, blank=True
    )

    class Meta:
        verbose_name = "Оклад сотрудника"
        verbose_name_plural = "Оклады сотрудников"


class EmployeeCategory(models.Model):
    name = models.CharField(
        default="Врач", 
        max_length=100, 
        verbose_name="Наименование категории сотрудников"
    )
    slug = models.SlugField(
        unique=True, 
        max_length=200, 
        blank=True
    )
    company = models.ForeignKey(
        to='company.Company', 
        on_delete=models.CASCADE, 
        related_name="employee_categories",
        verbose_name="Компания"
    )

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name + str(self.company.id))
        super(EmployeeCategory, self).save(*args, **kwargs)

    def __str__(self):
        return "%s" % self.name

    class Meta:
        verbose_name = "Категория сотрудников"
        verbose_name_plural = "Категории сотрудников"


class CustomerProfile(models.Model):
    user = models.OneToOneField(
        get_user_model(), 
        on_delete=models.CASCADE, 
        verbose_name='Клиент'
    )
    creator = models.ForeignKey(
        to='ManagerProfile', 
        verbose_name=("менеджер"), 
        blank=True, 
        on_delete=models.PROTECT, 
        related_name='customer_creator'
    )
    address = models.CharField(
        max_length=255,
        verbose_name='Адрес проживания'
    )
    company = models.ForeignKey(
        to='company.Company',
        on_delete=models.PROTECT,
        related_name='customers',
        verbose_name='Компания'
    )
    
    def __str__(self):
        return " %s Клиент" % self.user

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"


class ManagerProfile(models.Model):
    CLINIC_TYPE_CHOICES = (
        (1, 'Частный кабинет'),
        (2, 'Клиника'),
        (3, 'Медицинский центр'),
    )
    user = models.OneToOneField(
        get_user_model(), 
        on_delete=models.CASCADE, 
        verbose_name='Пользователь',
        related_name="manager_profile"
    )
    speciality = models.CharField(
        default="Системный администратор", 
        max_length=100, 
        null=True, blank=True,
        verbose_name="Специальность"
    )
    company = models.ManyToManyField(
        to='company.Company',
        related_name='managers',
        verbose_name='Компания'
    )

    def __str__(self):
        return "Профиль менеджера %s" % self.user.username

    class Meta:
        verbose_name = "Менеджер"
        verbose_name_plural = "Менеджеры"


class SubManagerProfile(models.Model):
    user = models.OneToOneField(
        to=get_user_model(), 
        on_delete=models.CASCADE, 
        verbose_name='Пользователь'
    )
    company = models.ManyToManyField(
        to='company.Company',
        related_name='sub_managers',
        verbose_name='Компания'
    )

    def __str__(self):
        return "Профиль суб-менеджера %s" % self.user.username

    class Meta:
        verbose_name = "Суб-менеджер"
        verbose_name_plural = "Суб-менеджеры"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if sender.user_type == 1:
            ManagerProfile.objects.create(user=instance)
            instance.managerprofile.save()
        elif sender.user_type == 2:
            SubManagerProfile.objects.create(user=instance)
            instance.submanagerprofile.save()
        else:
            sender.user_type == 4


@receiver(user_logged_in)
def got_online(sender, user, request, **kwargs):
    user_id = request.user.id
    if User.objects.filter(id=user_id).exists():
        user.is_online = True
        user.save()


@receiver(user_logged_out)
def got_offline(sender, user, request, **kwargs):
    user_id = request.user.id
    if User.objects.filter(id=user_id).exists():
        user.is_online = False
        user.save()
