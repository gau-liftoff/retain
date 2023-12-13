from django.db import models
from django.core.validators import MinLengthValidator, RegexValidator


class EmployeeDepartment(models.Model):
    dept_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    REQUIRED_FIELDS = ["dept_name"]

    class Meta:
        app_label = "employee"
        db_table = "department"

    def __str__(self) -> str:
        return f"DepartMent Name {self.dept_name}"


# # Create your models here.
class Employee(models.Model):
    emp_id = models.CharField(max_length=255, unique=True, blank=False, null=False)
    employee_name = models.CharField(max_length=50, blank=False, null=False)
    email = models.EmailField(blank=False, null=False, unique=True)
    mobile = models.CharField(
        max_length=10,
        unique=True,
        blank=False,
        null=False,
        validators=[
            MinLengthValidator(limit_value=10),
            RegexValidator(regex="^[0-9]*$", message="Only Digits Allowed"),
        ],
    )
    date_of_joining = models.DateField()
    date_of_leaving = models.DateField(null=True)
    reports_to = models.ForeignKey("self", on_delete=models.CASCADE, null=True)
    dept_id = models.ForeignKey(EmployeeDepartment, on_delete=models.CASCADE)
    experience = models.IntegerField()  # experience in years
    salary = models.IntegerField()  # salary in ruppes
    is_manager = models.BooleanField(default=False, blank=False)
    position = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    REQUIRED_FIELDS = [
        "emp_id",
        "employee_name",
        "email",
        "mobile",
        "emp_id",
        "date_of_joining",
        "dept_id",
    ]

    class Meta:
        app_label = "employee"
        db_table = "employee"

    def __str__(self):
        return f"Employee {self.dept_id} employee_name {self.employee_name}"
