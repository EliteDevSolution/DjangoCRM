from django.contrib import admin

from .models import (AppData, CreditCard, Customer, ElectricPower, File, Lead,
                     Payment, Profile, Requirement, RoofType, Service,
                     ServiceNote, Storey, Supplier)


@admin.register(ServiceNote)
class ServiceNoteAdmin(admin.ModelAdmin):
    list_display = ('content',)


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'title',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'leads_from', 'sales_person', 'agm',
                    'date_signed', 'customer_address', 'customer_email', 'phone_number', 'follow_up', 'customer_notes', 'creator', 'created_date',)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('supplier_name', 'supplier_invoice',
                    'supplier_amount', 'supplier_notes', 'supplier_date_paid',)


@admin.register(RoofType)
class RoofTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Storey)
class StoreyAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(ElectricPower)
class ElectricPowerAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Requirement)
class RequirementAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'kw', 'panel', 'inverter', 'roof_type', 'storey', 'electric_power',
                    'installation_notes', 'extra_amount', 'total_price', 'deposit_amount', 'deposit_date_paid', 'last_amount', 'status', 'created_date',)

    def customer_name(self, obj):
        return obj.customer.customer_name


@admin.register(CreditCard)
class CreditCardAdmin(admin.ModelAdmin):
    list_display = ('credit_card', 'customer_name', 'expires', 'created_date',)

    def customer_name(self, obj):
        return obj.customer.customer_name


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ('url', 'file_name', 'customer_name', 'created_date',)

    def customer_name(self, obj):
        return obj.customer.customer_name


@admin.register(AppData)
class AppDataAdmin(admin.ModelAdmin):
    list_display = ('name', 'value',)
