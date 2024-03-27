from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.http import JsonResponse
from django.apps import apps
from django.db import models
import csv
import pandas as pd
from datetime import datetime
from dateutil import parser
import re

from .models import Student
from .serializers import *

@api_view(['GET', 'POST'])
def students_list(request):
    if request.method == 'GET':
        data = Student.objects.all()
        serializer = StudentSerializer(data, context={'request': request}, many=True)

        return Response(serializer.data)

    elif request.method == 'POST':
        print(request.data)
        serializer = StudentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT', 'DELETE'])
def students_detail(request, pk):
    try:
        student = Student.objects.get(pk=pk)
    except Student.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = StudentSerializer(student, data=request.data,context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        student.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# views.py
@api_view(['POST'])
def upload_csv(request):
    if request.method == 'POST' and request.FILES['file']:
        file = request.FILES['file']
        decoded_file = file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)
        file = pd.read_csv()
        try:
            # for row in reader:                
            #     # Convert birthdate to a datetime object
            #     birthdate = datetime.strptime(row['birthdate'], '%d/%m/%Y').date()

            #     # Convert empty string to None for score field
            #     score = int(row['score']) if row['score'].strip() else 0

            #     Student.objects.create(
            #         name=row['name'],
            #         birthdate=birthdate,
            #         score=score,
            #         grade=row['grade']
            #     )
            if file.name.endswith('.csv'):
                df = pd.read_csv(file, nrows=10)
            elif file.name.endswith('.xls') or file.name.endswith('.xlsx'):
                df = pd.read_excel(file, nrows=10)
            else:
                raise ValueError('Unsupported file format')

            # Get the table name from the file
            table_name = file.name.split('.')[0].replace(' ', '_').lower()
            table_name = table_name.capitalize().replace('_', ' ')
            
            if apps.all_models['dynamic_data'].get(table_name):
                model = apps.all_models['your_app_name'][table_name]
                existing_fields = [field.name for field in model._meta.get_fields()]

                for column in df.columns:
                    field_type = check_type(df[column].iloc[0])  # Check data type of first row
                    if column not in existing_fields:
                        field = getattr(models, field_type)(null=True, blank=True)
                        model.add_to_class(column, field)

                model.save()
            else:
                fields = {
                    column: getattr(models, check_type(df[column].iloc[0]))(null=True, blank=True)
                    for column in df.columns
                }
                new_model = type(table_name, (models.Model,), fields)
                new_model._meta.db_table = table_name.lower().replace(' ', '_')
                new_model.save()

            return JsonResponse({'message': 'CSV data imported successfully'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'No file provided'}, status=400)

def is_valid_date(date_str):
    """lambda function for checking date validation

    Args:
        date_str (str): Date String

    Returns:
        Bool: is_valid_date
    """
    try:
        parsed_date = parser.parse(date_str)
        return True if parsed_date else False
    except (ValueError, OverflowError):
        return False

def check_type(obj):
    """Check the type of the input object."""
    if is_valid_date(obj):
        return 'DateField'
    elif re.match(r'^-?\d+$', obj):
        return 'IntegerField'
    elif re.match(r'^-?\d+\.\d+$', obj):
        return 'FloatField'
    elif obj.lower() in ('true', 'false'):
        return 'BooleanField'
    else:
        return 'CharField'
