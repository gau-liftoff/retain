from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import authentication, permissions, status, viewsets, pagination
from rest_framework.views import APIView
from django.http import HttpResponse
from .serializers import (
    DepartmentSerializer,
    EmployeeReadOnlySerializer,
    EmployeeWriteOnlySerializer,
)
from employee.models import EmployeeDepartment, Employee
from django.db.models import F, Sum, fields, Count, ExpressionWrapper
from django.db.models.functions import Cast
import csv
import json
import os
import requests as req
import sys
from services.email import send_email


# using APIVIEW
class EmployeeCreateUpdateListDeleteView(APIView):
    """
    employee CRUD
    """

    pagination_class = pagination.PageNumberPagination
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = EmployeeWriteOnlySerializer(data=request.data)
        result = {}
        if serializer.is_valid():
            serializer.save()
            result["data"] = serializer.data
            result["message"] = "Successfully created!"
            return Response(result, status=status.HTTP_201_CREATED)

        result["message"] = "Validation Error"
        result["errors"] = serializer.errors
        return Response(result, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            # check if the employee exists
            employee_instance = Employee.objects.get(pk=pk)
            serializer = EmployeeReadOnlySerializer(
                employee_instance, data=request.data
            )
            result = {}
            if serializer.is_valid():
                serializer.save()
                result["data"] = serializer.data
                result["message"] = "Successfully updated!"
                return Response(result, status=status.HTTP_200_OK)
            result["message"] = "Validation Error"
            result["errors"] = serializer.errors
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        except Employee.DoesNotExist:
            result["message"] = "Employee Doesnot Exists"
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            result["message"] = str(error)
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk=None):
        result = {"message": "Successfully Fetched"}
        filter_type = request.query_params.get("filter_type")
        try:
            if pk:
                employee_instance = Employee.objects.get(pk=pk, is_active=True)
                print(employee_instance)
                serializer = EmployeeReadOnlySerializer(instance=employee_instance)
            else:
                filter_condition = {"is_active": True}
                if filter_type and filter_type == "manager":
                    filter_condition["is_manager"] = True
                paginated_instance = self.pagination_class()
                queryset = (
                    Employee.objects.select_related("dept_id")
                    .filter(**filter_condition)
                    .order_by("id")
                )
                paginated_queryset = paginated_instance.paginate_queryset(
                    queryset, request
                )
                serializer = EmployeeReadOnlySerializer(
                    instance=paginated_queryset, many=True
                )
                result["next"] = paginated_instance.get_next_link()
                result["previous"] = paginated_instance.get_previous_link()
                result["count"] = paginated_instance.page.paginator.count
            result["data"] = serializer.data
            return Response(result, status=status.HTTP_200_OK)
        except Employee.DoesNotExist:
            result["message"] = "Employee Doesnot Exists"
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            result["message"] = str(error)
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        result = {}
        try:
            # check if the employee exists
            employee = Employee.objects.get(pk=pk, is_active=True)
            # if employee exists soft delete
            employee.is_active = False
            employee.save()
            result[
                "message"
            ] = f"Successfully deleted Employee {employee.employee_name}"
            return Response(result, status=status.HTTP_200_OK)
        except Employee.DoesNotExist:
            result["message"] = "Employee Doesnot Exists"
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            result["message"] = str(e)
            return Response(result, status=status.HTTP_400_BAD_REQUEST)


class EmployeeBulkUpload(APIView):
    permission_classes = [permissions.IsAuthenticated]
    BULK_UPLOAD_JSON_PATH = "constants/bulk-upload.json"

    def get_csv_headers(self, relative_file_path, with_code=False):
        # get csv headers
        file_path = os.path.join(os.path.dirname(__file__), relative_file_path)
        with open(file_path, "r") as fp:
            data = json.load(fp)
        # if with_code key is true send whole each header row object along with header row code.
        if with_code == True:
            return data["headers"]  # csv headers

        headers = []
        for row_obj in data["headers"]:
            if row_obj["is_mandatary"]:
                headers.append(f'{row_obj["name"]}*')
            else:
                headers.append(row_obj["name"])
        return headers

    def convert_value_to_correct_type(self, header_column, value=""):
        if header_column["type"] == "int":
            converted_value = int(value)
        elif header_column["type"] == "bool":
            converted_value = bool(value)
        else:
            converted_value = value
        return converted_value

    def get(self, request):
        response = HttpResponse(content_type="text/csv")
        response[
            "Content-Disposition"
        ] = '"attachment;filename="EmployeeBulkUpload.csv"'
        csv_writer = csv.writer(response)
        # get csv headers
        headers = self.get_csv_headers(self.BULK_UPLOAD_JSON_PATH)
        csv_writer.writerow(headers)

        return response

    def post(self, request):
        csv_file = request.FILES.get("employee_csv")
        try:
            if not csv_file:
                raise ValueError("Csv File is required")
            # convert csv to json
            decoded_file = csv_file.read().decode("utf-8").splitlines()
            csv_reader = csv.DictReader(decoded_file)
            headers = self.get_csv_headers(self.BULK_UPLOAD_JSON_PATH, True)

            result = {"total": 0, "success": 0, "failed": 0, "errors": []}
            for csv_data in csv_reader:
                employee_data = {}
                for header_column in headers:
                    employee_data[
                        header_column["code"]
                    ] = self.convert_value_to_correct_type(
                        header_column,
                        csv_data[
                            f'{header_column["name"]}*'
                            if header_column["is_mandatary"]
                            else header_column["name"]
                        ],
                    )
                print(employee_data)
                # create a employee by calling post employee api
                auth_token = request.headers.get("Authorization").split(" ")[1]
                res = req.post(
                    f'{os.environ.get("STAGING_URL")}/api/v1/employee/',
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {auth_token}",
                    },
                    json=employee_data,
                )
                result["total"] += 1
                if res.status_code != 201:
                    result["failed"] += 1
                    data = res.json()
                    result["errors"].append(
                        {
                            "employee Id": employee_data["emp_id"],
                            "message": data["message"],
                            "errors": data["errors"],
                        }
                    )
                else:
                    result["success"] += 1

            send_email(email_data=result, recepient="patilgautam728@gmail.com")
            return Response(
                {
                    "message": "Employees will be created shortly. You will be notified by email"
                },
                status=status.HTTP_200_OK,
            )
        except Exception as error:
            return Response({"message": str(error)}, status=status.HTTP_400_BAD_REQUEST)


class Dashboard(APIView):
    # gets the averge lifespan of a all employees throughout organisation as well as dept and manager wise if filterkey is sent

    permission_classes = [permissions.IsAuthenticated]

    def get_avg_lifespan_query_result(self, filter_type):
        average_lifespan = []
        if filter_type:
            group_key = (
                ["reports_to", "reports_to__employee_name"]
                if filter_type == "manager"
                else ["dept_id", "dept_id__dept_name"]
            )
            results = Employee.objects.values(*group_key).annotate(
                total_seconds=Sum(
                    ExpressionWrapper(
                        F("date_of_leaving") - F("date_of_joining"),
                        output_field=fields.DurationField(),
                    )
                ),
                total_employees=Count("id"),
            )
            for result in results:
                data_object = {}
                average_lifespan_seconds = (
                    result["total_seconds"] / result["total_employees"]
                )
                data_object["life_span"] = average_lifespan_seconds / (
                    365 * 24 * 60 * 60
                )
                if filter_type == "manager":
                    data_object["manager_name"] = result["reports_to__employee_name"]
                else:
                    data_object["department_name"] = result["dept_id__dept_name"]
                average_lifespan.append(data_object)
        else:
            # Total average lifespan to employees
            total_average_lifespan = Employee.objects.values("dept_id").aggregate(
                total_days=Sum(
                    Cast(
                        F("date_of_leaving") - F("date_of_joining"),
                        output_field=fields.DurationField(),
                    )
                ),
                total_employees=Count("id"),
            )
            # Calculate the average lifespan in years
            if (
                total_average_lifespan["total_days"]
                and total_average_lifespan["total_employees"]
            ):
                average_lifespan = (
                    total_average_lifespan["total_days"]
                    / total_average_lifespan["total_employees"]
                ).total_seconds() / (
                    365 * 24 * 3600
                )  # Convert seconds to years
            else:
                average_lifespan = 0
        return average_lifespan

    def get(self, request):
        response = {
            "message": "Successfully fetched",
        }
        try:
            supported_filter_types = ["manager", "department"]
            filter_type = request.query_params.get("filter_type")
            if filter_type and filter_type not in supported_filter_types:
                raise ValueError("Invalid filterType provided")
            result = self.get_avg_lifespan_query_result(filter_type)
            response["data"] = result
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            response["message"] = str(e)
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


# using viewsets Note: To Try Out using different Ways
class DepartmentViewSet(viewsets.ModelViewSet):
    """
    defines the department CRUD
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DepartmentSerializer
    queryset = EmployeeDepartment.objects.all()
