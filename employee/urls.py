from django.contrib import admin
from django.urls import path,include
from employee.views import DepartmentViewSet,EmployeeCreateUpdateListDeleteView,EmployeeBulkUpload,Dashboard
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("department",DepartmentViewSet)

urlpatterns = [
    path("employee/<int:pk>",EmployeeCreateUpdateListDeleteView.as_view()),
    path("employee/",EmployeeCreateUpdateListDeleteView.as_view()),
    path("employee/download-bulk-upload-sheet",EmployeeBulkUpload.as_view()),
    path("employee/bulk-upload",EmployeeBulkUpload.as_view()),
    path("employee/dashboard",Dashboard.as_view()),
    path("",include(router.urls)),
]