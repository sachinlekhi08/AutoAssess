from django.contrib import admin

from .models import CarEvaluation


@admin.register(CarEvaluation)
class CarEvaluationAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "buying", "maint", "doors", "persons", "lug_boot", "safety", "prediction", "created_at"]
    list_filter = ["prediction", "buying", "maint", "safety", "created_at"]
    search_fields = ["user__username", "user__email"]
    ordering = ["-created_at"]
    readonly_fields = ["created_at"]
