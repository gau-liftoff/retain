# Generated by Django 4.2.8 on 2023-12-07 12:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EmployeeDepartment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dept_name', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'department',
            },
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('emp_id', models.CharField(max_length=255)),
                ('employee_name', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('mobile', models.CharField(max_length=10, unique=True)),
                ('date_of_joining', models.DateField(auto_now_add=True)),
                ('date_of_leaving', models.DateField(auto_now_add=True)),
                ('experience', models.IntegerField()),
                ('salary', models.IntegerField()),
                ('position', models.CharField(max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=True)),
                ('dept_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='deptname', to='employee.employeedepartment')),
                ('reports_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='employee.employee')),
            ],
            options={
                'db_table': 'employee',
            },
        ),
    ]
