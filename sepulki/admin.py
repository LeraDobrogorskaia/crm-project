from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from sepulki import models


class BaseSepulkaProperty(admin.ModelAdmin):
    list_filter = ('is_active',)
    search_fields = ('name',)
    base_fieldsets = (
        (_("Additional"), {"fields": ("description", "is_active")}),
    )


@admin.register(models.Color)
class ColorAdmin(BaseSepulkaProperty):
    list_display = ('name', 'hex', 'is_active')
    fieldsets = (
        (None, {"fields": ("name", "hex")}),
        *BaseSepulkaProperty.base_fieldsets,
    )


@admin.register(models.Size)
class SizeAdmin(BaseSepulkaProperty):
    list_display = ('name', 'volume', 'is_active')
    fieldsets = (
        (None, {"fields": ("name", "volume")}),
        *BaseSepulkaProperty.base_fieldsets,
    )


@admin.register(models.Material)
class MaterialAdmin(BaseSepulkaProperty):
    list_display = ('name', 'density', 'cost', 'is_active')
    fieldsets = (
        (None, {"fields": ("name", "density", "cost")}),
        *BaseSepulkaProperty.base_fieldsets,
    )


@admin.register(models.PreparedPropertiesSet)
class PreparedPropertiesSetAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'material', 'size', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)

    fieldsets = (
        (None, {"fields": ("name", )}),
        (_("Properties"), {"fields": ("color", "material", "size")}),
        (_("Additional"), {"fields": ("description", "is_active")}),
    )

@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'is_rejected', 'status', 'created', 'modified')
    list_filter = ('created', 'modified', 'status', 'is_rejected')

    fieldsets = (
        (None, {"fields": ("client", "status")}),
        (_("Properties"), {"fields": ("color", "material", "size")}),
        (_("Reject"), {"fields": ("is_rejected", "reject_message")}),
    )


@admin.register(models.OrderReturn)
class OrderReturnAdmin(admin.ModelAdmin):
    list_display = ('order', 'solution', 'created', 'modified')
    list_filter = ('created', 'modified', 'solution')
