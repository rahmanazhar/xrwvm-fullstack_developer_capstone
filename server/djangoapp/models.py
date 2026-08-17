from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


# Create your models here.

# Car Make model
class CarMake(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    country = models.CharField(max_length=100, default="Unknown")

    def __str__(self):
        return self.name


# Car Model model, many-to-one with CarMake
class CarModel(models.Model):
    SEDAN = 'Sedan'
    SUV = 'SUV'
    WAGON = 'Wagon'
    COUPE = 'Coupe'
    HATCHBACK = 'Hatchback'
    CAR_TYPES = [
        (SEDAN, 'Sedan'),
        (SUV, 'SUV'),
        (WAGON, 'Wagon'),
        (COUPE, 'Coupe'),
        (HATCHBACK, 'Hatchback'),
    ]

    car_make = models.ForeignKey(
        CarMake, on_delete=models.CASCADE, related_name='car_models')
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=CAR_TYPES, default=SUV)
    year = models.IntegerField(
        default=2023,
        validators=[MaxValueValidator(2023), MinValueValidator(2015)])

    def __str__(self):
        return f"{self.car_make.name} {self.name} ({self.year})"
