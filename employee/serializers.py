from rest_framework import serializers
from .models import Employee,EmployeeDepartment


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeDepartment
        fields = '__all__'

class EmployeeReadOnlySerializer(serializers.ModelSerializer):
    department = serializers.SlugRelatedField(source="dept_id",read_only=True,slug_field="dept_name")
    manager = serializers.SlugRelatedField(source="reports_to",read_only=True,slug_field='employee_name')
    class Meta:
        model = Employee
        fields = ("id","emp_id","email","mobile","employee_name","date_of_joining","reports_to","salary","experience","position","department","is_manager",'manager')
        read_only_fields = ("id",)
        
class EmployeeWriteOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ("emp_id","email","mobile","employee_name","date_of_joining","reports_to","salary","experience","position","dept_id","is_manager")
        read_only_fields = ("id",)
        

