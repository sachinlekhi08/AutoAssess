from django.conf import settings
from django.db import models


BUYING_CHOICES = [("vhigh", "Very High"), ("high", "High"), ("med", "Medium"), ("low", "Low")]
MAINT_CHOICES = BUYING_CHOICES
DOOR_CHOICES = [("2", "2 Doors"), ("3", "3 Doors"), ("4", "4 Doors"), ("5more", "5 or More Doors")]
PERSON_CHOICES = [("2", "2 People"), ("4", "4 People"), ("more", "More Than 4")]
LUG_BOOT_CHOICES = [("small", "Small"), ("med", "Medium"), ("big", "Big")]
SAFETY_CHOICES = [("low", "Low"), ("med", "Medium"), ("high", "High")]
PREDICTION_CHOICES = [
    ("Unacceptable", "Unacceptable"),
    ("Acceptable", "Acceptable"),
    ("Good", "Good"),
    ("Very Good", "Very Good"),
]


class CarEvaluation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    buying = models.CharField(max_length=5, choices=BUYING_CHOICES)
    maint = models.CharField(max_length=5, choices=MAINT_CHOICES)
    doors = models.CharField(max_length=5, choices=DOOR_CHOICES)
    persons = models.CharField(max_length=4, choices=PERSON_CHOICES)
    lug_boot = models.CharField(max_length=5, choices=LUG_BOOT_CHOICES)
    safety = models.CharField(max_length=4, choices=SAFETY_CHOICES)
    prediction = models.CharField(max_length=12, choices=PREDICTION_CHOICES)
    confidence = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.prediction} - {self.created_at:%Y-%m-%d %H:%M}"
