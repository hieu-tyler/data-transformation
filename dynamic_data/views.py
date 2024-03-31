from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.http import JsonResponse
import csv
import pandas as pd
from datetime import datetime
import re

from .models import Student
from .serializers import *

DATE_FORMATS = [
        '%Y-%m-%d',     # Year-Month-Day (ISO 8601)
        '%m/%d/%Y',     # Month/Day/Year
        '%Y%m%d',       # YearMonthDay
        '%m-%d-%Y',     # Month-Day-Year
        '%d-%m-%Y',     # Day-Month-Year
        '%d/%m/%Y',     # Day/Month/Year
        '%Y/%m/%d',     # Year/Month/Day
        '%d-%b-%Y',     # Day-MonthAbbreviation-Year (e.g., 01-Jan-2022)
        '%d %b %Y',     # Day MonthAbbreviation Year (e.g., 01 Jan 2022)
        '%b %d, %Y',    # MonthAbbreviation Day, Year (e.g., Jan 01, 2022)
        '%B %d, %Y',    # Month Day, Year (e.g., January 01, 2022)
        '%d %B %Y',     # Day Month Year (e.g., 01 January 2022)
        '%Y-%m-%d %H:%M:%S',  # Year-Month-Day Hour:Minute:Second (ISO 8601)
        '%m/%d/%Y %H:%M:%S',  # Month/Day/Year Hour:Minute:Second
        '%Y%m%d %H:%M:%S',    # YearMonthDay Hour:Minute:Second
        '%m-%d-%Y %H:%M:%S',  # Month-Day-Year Hour:Minute:Second
        '%d-%m-%Y %H:%M:%S',  # Day-Month-Year Hour:Minute:Second
        '%d/%m/%Y %H:%M:%S',  # Day/Month/Year Hour:Minute:Second
        '%Y/%m/%d %H:%M:%S',  # Year/Month/Day Hour:Minute:Second
        '%m/%d/%y'       # Month/Day/Year (2-digit year)
    ]


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
        df = pd.DataFrame(reader)
        print(df)
        try:
            data = handle_data(df)
            print(data)
            for index, row in data.iterrows():                
                Student.objects.create(
                    name=row['name'],
                    birthdate=row['birthdate'],
                    score=row['score'],
                    grade=row['grade']
                )

            return JsonResponse({'message': 'CSV data imported successfully'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'No file provided'}, status=400)


def handle_data(df):
    for column in df.columns:
        most_common_datatype = get_datatype(df[column])
        convert_to_correct_datatype(df, column, most_common_datatype)
    return df

def is_valid_date(date_str):
    """lambda function for checking date validation

    Args:
        date_str (str): Date String

    Returns:
        Bool: is_valid_date
    """
    for date_format in DATE_FORMATS:
        try:
            datetime.strptime(date_str, date_format)
            return True
        except ValueError:
            continue
    return False

def check_type(obj):
    """Check the type of the input object."""
    if is_valid_date(obj):
        return 'date'
    elif re.match(r'^-?\d+$', obj):
        return 'int'
    elif re.match(r'^-?\d+\.\d+$', obj):
        return 'float64'
    elif obj.lower() in ('true', 'false'):
        return 'bool'
    else:
        return 'object'
    
def convert_to_correct_datatype(df, column, datatype):
    if datatype == 'category':
        df[column] = df[column].astype('category')
    elif datatype == 'date':
        df[column] = pd.to_datetime(df[column], errors='coerce')
    elif datatype == 'int':
        df[column] = pd.to_numeric(df[column], errors='coerce').astype('Int64').fillna(0)
    elif datatype == 'float64':
        df[column] = pd.to_numeric(df[column], errors='coerce').fillna(0.0)
    elif datatype == 'bool':
        df[column] = df[column].map(lambda x: x.lower() == 'true')
    elif datatype == 'object':
        df[column] = df[column].fillna('')

def get_datatype(series):
    """Get the most common datatype for a pandas Series"""
    types_count = {
        'datetime64': 0,
        'category': 0,
        'date': 0,
        'int': 0,
        'float64': 0,
        'bool': 0,
        'object': 0
    }

    for val in series:
        if val.strip() == '':
            types_count['object'] += 1
        else:
            data_type = check_type(val)
            types_count[data_type] += 1

    return max(types_count, key=types_count.get)