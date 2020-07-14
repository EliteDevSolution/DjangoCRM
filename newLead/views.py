import json
from datetime import datetime

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, permission_required
from django.core.files.storage import FileSystemStorage
from django.db.models import Count
from django.db.models import Q, Sum
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.template.loader import render_to_string

from customer.models import (AppData, CreditCard, Customer, ElectricPower,
                             File, Lead, Payment, Requirement, RoofType,
                             ServiceNote, Storey, Supplier)

from django.core.exceptions import ObjectDoesNotExist

from django.shortcuts import render

# Create your views here.




@login_required
def home(request):
    """Renders home page with default select options"""
    if request.user.groups.filter(name='installer').exists():
        return redirect('./installation')


    customer_fields = {
        'from': True,
        'assign': False,
        'agm': False,
        'date_signed': False,
        'customer_name': True,
        'customer_address': False,
        'customer_email': False,
        'phone_number': True,
        'notes': False
    }
    service_fields = {
        'agm': True,
        'customer_name': True,
        'customer_address': True,
        'customer_email': True,
        'phone_number': True,
        'installation_date': True,
        'installer': False,
        'service_note': True
    }
    required_fields = {
        'customer_fields': customer_fields,
        'service_fields': service_fields
    }
    context = {
        'leads': Lead.objects.all(),
        'sales_people': get_user_model().objects.filter(profile__title='salesman'),
        'installers': get_user_model().objects.filter(profile__title='installer'),
        'current_tab': 'home-tab',
        'required_fields': required_fields
    }
    return render(request, 'customer/home.html', context=context)



@login_required
@permission_required(['customer.customer_list'])
def newLead_list(request):
    """POST: Creates a customer and redirects to customer requirement form. GET: Returns List of new leads."""
    if request.method == 'POST':
        # get input data to check
        customer_name = request.POST.get('customer_name')
        agm = request.POST.get('agm') if request.POST.get('agm') else None
        address = request.POST.get('customer_address') if request.POST.get('customer_address') else None
        
        # checks if the customer name already exists
        customer = Customer.objects.filter(customer_name=customer_name)
        agm_customer = Customer.objects.filter(agm=agm)
        adress_customer = Customer.objects.filter(customer_address=address)
        # if customer:
        #     messages.error(request,f'Customer {customer_name} already exists.')
        #     return redirect('home')
        if agm:
            if agm_customer:
                messages.error(request,f'AGM {agm} already exists.')
                return redirect('home')
        elif address:
            if adress_customer:
                messages.error(request,f'Address {address} already exists.')
                return redirect('home')
        else:
            # Get data from form
            customer_data = {
                'creator': request.user,
                'leads_from_id': request.POST.get('leads_from'),
                'sales_person_id': request.POST.get('sales_person'),
                'agm': request.POST.get('agm') if request.POST.get('agm') else None,
                'date_signed': datetime.strptime(request.POST.get('date_signed'), '%d/%m/%Y').strftime(
                    '%Y-%m-%d') if request.POST.get('date_signed') else None,
                'customer_name': request.POST.get('customer_name'),
                'customer_address': request.POST.get('customer_address'),
                'customer_email': request.POST.get('customer_email'),
                'phone_number': request.POST.get('phone_number'),
                'customer_notes': request.POST.get('customer_notes') if request.POST.get('customer_notes') else None
            }

            requirement_data = {
                'installation_date': datetime.strptime(request.POST.get('installation_date'), '%d/%m/%Y').strftime(
                    '%Y-%m-%d') if request.POST.get('installation_date') else None,
                'installer_id': request.POST.get('installer')
            }

            # Create new customer and store it in database
            customer = Customer(**customer_data)
            customer.save()

            if 'btn_create_customer' in request.POST:
                status = 'CREATED'
                path = 'newLead-view'
            elif 'btn_create_service' in request.POST:
                status = 'SERVICE_HOME'
                path = 'service-view'

            # Create new requirement and credit card for the new customer
            requirement = Requirement(
                customer=customer, status=status, **requirement_data)
            requirement.save()
            credit_card = CreditCard(customer=customer)
            credit_card.save()

            if request.POST.get('service_note'):
                service_note = ServiceNote(
                    requirement=requirement, content=request.POST.get('service_note').strip())
                service_note.save()

            # redirect to new customer view
            return redirect(path, pk=customer.id)

    elif request.method == 'GET':
        # Get all requirements in CREATED status
        if request.user.has_perm('customer.customer_view_others'):
            requirements = Requirement.objects.filter(
                status="CREATED").distinct()
        else:
            requirements = Requirement.objects.filter(Q(customer__sales_person=request.user) | Q(
                installer=request.user), status="CREATED").distinct()

        # Set columns to display.
        # IMPORTANT: to set columns in dict "columns",
        # 'key' is the title of the column and 'value' is the field in requirement object,
        # e.g. to get the customer name, 'requirement' object has an attribute 'customer' and this has an attribute 'customer_name'
        # so to retrieve it you will use 'customer.customer_name'
        columns = {
            'Creation Date': 'customer.created_date',
            'Sales': 'customer.sales_person',
            'Lead Name': 'customer.customer_name',
            'Phone': 'customer.phone_number',
            'Address': 'customer.customer_address',
            'Follow Up': 'customer.follow_up',
            'Notes': 'customer.customer_notes',
        }

        # Set template context
        #   requirements: Requirements data
        #   url_view: name of url to enter each customer form
        #   columns: colums definition
        #   colspan: number of columns of the table. used to display a 'No results' message when empty
        #   current_tab: name of the current tab to set active class
        context = {
            'requirements': requirements,
            'url_view': 'newLead-view',
            'columns': columns,
            'search_field_visible': True,
            'colspan': len(columns) + 2,
            'current_tab': 'customer-tab'
        }
        # Return requirement list in CREATED status
        return render(request, 'customer/requirement-list.html', context=context)


@login_required
def newLead_search(request):
    if request.method == 'POST':

        # get Search Key data from search form
        search_value = request.POST.get('search_value')
        print("========================")

        # Get all requirements in CREATED status
        if request.user.has_perm('customer.customer_view_others'):
            requirements = Requirement.objects.filter(
                Q(customer__customer_name__contains=search_value) |
                Q(customer__customer_address__contains=search_value) |
                Q(customer__customer_email__contains=search_value) |
                Q(customer__phone_number__contains=search_value) |
                Q(customer__agm__contains=search_value),
                status="CREATED").distinct()
        else:
            requirements = Requirement.objects.filter(
                Q(customer__sales_person=request.user) |
                Q(customer__customer_name__contains=search_value) |
                Q(customer__customer_address__contains=search_value) |
                Q(customer__customer_email__contains=search_value) |
                Q(customer__phone_number__contains=search_value) |
                Q(customer__agm__contains=search_value) |
                Q(installer=request.user), status="CREATED").distinct()

        # Set columns to display.
        # IMPORTANT: to set columns in dict "columns",
        # 'key' is the title of the column and 'value' is the field in requirement object,
        # e.g. to get the customer name, 'requirement' object has an attribute 'customer' and this has an attribute 'customer_name'
        # so to retrieve it you will use 'customer.customer_name'
        columns = {
            'Creation Date': 'customer.created_date',
            'Sales': 'customer.sales_person',
            'Customer Name': 'customer.customer_name',
            'Phone': 'customer.phone_number',
            'Address': 'customer.customer_address',
            'Follow Up': 'customer.follow_up',
            'Notes': 'customer.customer_notes',
        }

        # Set template context
        #   requirements: Requirements data
        #   url_view: name of url to enter each customer form
        #   columns: colums definition
        #   colspan: number of columns of the table. used to display a 'No results' message when empty
        #   current_tab: name of the current tab to set active class
        context = {
            'requirements': requirements,
            'url_view': 'newLead-view',
            'columns': columns,
            'colspan': len(columns) + 2,
            'current_tab': 'customer-tab',
            'search_field_visible': True,
            'search_value': search_value,
        }

        # Return requirement list in CREATED status
        return render(request, 'customer/requirement-list.html', context=context)


@login_required
@permission_required(['customer.customer_view'])
def newLead_view(request, pk):
    """Returns a customer form in CREATED status"""
    customer = Customer.objects.get(id=pk)

    # Set context.
    # leads, sales_people, roof_types, storeys, electric_powers are default options loaded in Django admin
    # requirement, credit_card, files are loaded from current customer
    # options allow to configure if a section is displayed or not:
    #   follow_up: show follow up input
    #   file_upload_enabled: show file upload form
    #   file_list_enabled: show uploaded files list
    #   installation_data_enabled: show installation data form
    #   customer_check_enabled: show customer check input
    #   deposit_info_enabled: show deposit data form
    #   installer_payment_data_enabled: show installer payment form
    #   supplier_list_enabled: show list of suppliers
    # buttons allow to configure the promotion buttons to display:
    #   btn_promote_name: this is the 'name' attribute of HTML tag
    #   btn_promote_text: this is the content that will be displayed to user
    customer_fields = {
        'from': True,
        'assign': True,
        'agm': True,
        'date_signed': True,
        'customer_name': True,
        'customer_address': True,
        'customer_email': True,
        'phone_number': True,
        'notes': True
    }
    system_fields = {
        'kw': True,
        'panel': True,
        'panel_pcs': True,
        'inverter': True,
        'inverter_pcs': True,
        'roof_type': True,
        'storey': True,
        'installation_notes': False,
        'electric_power': True,
        'extra_amount': False,
        'total_price': True,
        'deposit_amount': True,
        'last_amount': True
    }
    upload_fields = {
        'upload': True
    }
    required_fields = {
        'customer_fields': customer_fields,
        'system_fields': system_fields,
        'upload_fields': upload_fields
    }
    context = {
        'current_tab': 'customer-tab',
        'leads': Lead.objects.all(),
        'sales_people': get_user_model().objects.filter(profile__title='salesman'),
        'roof_types': RoofType.objects.all(),
        'storeys': Storey.objects.all(),
        'electric_powers': ElectricPower.objects.all(),
        'customer': customer,
        'requirement': Requirement.objects.filter(customer_id=customer.id).first(),
        'credit_card': CreditCard.objects.filter(customer_id=customer.id).first(),
        'files': File.objects.filter(customer_id=customer.id),
        'power_meter_connection_disable': True,
        'required_fields': required_fields,
        'options': {
            'user_created_enabled': True,
            'customer_data_enabled': True,
            'requirement_data_enabled': True,
            'service_data_enabled': False,
            'follow_up': True,
            'file_upload_enabled': True,
            'file_list_enabled': True,
            'installation_data_enabled': False,
            'customer_check_enabled': False,
            'deposit_info_enabled': False,
            'installer_payment_data_enabled': False,
            'supplier_list_enabled': False,
            'Finance': False,
            'new_lead':True,
            'buttons': [
                {
                    'btn_promote_name': 'btn_already_signed',
                    'btn_promote_text': 'Already Signed'
                }
            ]
        }
    }

    # Return customer form for CREATED status
    return render(request, 'customer/customer-full-form.html', context=context)

