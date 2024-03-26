from django.db import models

# Create your models here.
class Student(models.Model):
    name = models.CharField("Name", max_length=255)
    birthdate = models.DateField("Birthdate")
    score = models.IntegerField("Score")
    grade = models.CharField("Grade", max_length=5)
    
