import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def remove_incompatible_records(apps, schema_editor):
    apps.get_model("prediction", "LoanApplication").objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("prediction", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(remove_incompatible_records, migrations.RunPython.noop),
        migrations.DeleteModel(name="LoanApplication"),
        migrations.CreateModel(
            name="CarEvaluation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("buying", models.CharField(choices=[("vhigh", "Very High"), ("high", "High"), ("med", "Medium"), ("low", "Low")], max_length=5)),
                ("maint", models.CharField(choices=[("vhigh", "Very High"), ("high", "High"), ("med", "Medium"), ("low", "Low")], max_length=5)),
                ("doors", models.CharField(choices=[("2", "2 Doors"), ("3", "3 Doors"), ("4", "4 Doors"), ("5more", "5 or More Doors")], max_length=5)),
                ("persons", models.CharField(choices=[("2", "2 People"), ("4", "4 People"), ("more", "More Than 4")], max_length=4)),
                ("lug_boot", models.CharField(choices=[("small", "Small"), ("med", "Medium"), ("big", "Big")], max_length=5)),
                ("safety", models.CharField(choices=[("low", "Low"), ("med", "Medium"), ("high", "High")], max_length=4)),
                ("prediction", models.CharField(choices=[("Unacceptable", "Unacceptable"), ("Acceptable", "Acceptable"), ("Good", "Good"), ("Very Good", "Very Good")], max_length=12)),
                ("confidence", models.FloatField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
