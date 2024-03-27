from rest_framework import serializers
from .models import Student
from django import forms

class StudentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Student 
        fields = ('pk', 'name', 'birthdate', 'score', 'grade')
        widgets = {
            'date_field': forms.DateInput(format='%d/%m/%Y', attrs={'type': 'date'}),
        }