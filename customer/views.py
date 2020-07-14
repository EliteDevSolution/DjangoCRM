from django.conf import settings
import os
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
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
import xlwt

from customer.models import (AppData, CreditCard, Customer, ElectricPower,
                             File, Lead, Payment, Requirement, RoofType,
                             ServiceNote, Storey, Supplier)


@login_required
def update_app_data(request):
    print(request.POST)
    if AppData.objects.filter(name=request.POST.get('app_data_name')).exists():
        app_data = AppData.objects.get(name=request.POST.get('app_data_name'))
        app_data.value = request.POST.get('app_data_value')
    else:
        app_data = AppData(name=request.POST.get(
            'app_data_name'), value=request.POST.get('app_data_value'))

    app_data.save()
    return JsonResponse(json.dumps({'message': '{} updated'.format(request.POST.get('app_data_name'))}), safe=False)


@login_required
def save_service_note(request):
    """Save or update a service note linked to a Requirement. All args are contained in resquest form. Returns a JSON data.

    Args:
        requirement_pk: Requirement ID.
        service_note_pk: Optional. Service note ID. If provided, it updated fields of service note, if not, the method creates a new service note.
        content: Service note content.

    Returns:
        message: String to display to the user.
        html: HTML of the table of service notes to reload table.
    """

    if request.method == 'POST':

        if request.POST.get('service_note_pk'):
            # if service note id is provided, load existing service note
            message = 'updated'
            service_note = ServiceNote.objects.get(
                pk=request.POST.get('service_note_pk'))
        else:
            # if service notes id is not provided, create a new service note
            message = 'saved'
            service_note = ServiceNote()

        # set service notes fields
        service_note.requirement_id = request.POST.get('requirement_pk')
        service_note.content = request.POST.get(
            'service_notes') if request.POST.get('service_notes') else None

        # save service note
        service_note.save()

        # load all service notes of the requirement
        service_notes = ServiceNote.objects.filter(
            requirement_id=request.POST.get('requirement_pk'))

        # pre render table to be updated in HTML
        html = render_to_string(
            'customer/service-notes-list.html', context={'service_notes': service_notes})

        return JsonResponse(json.dumps({'message': 'Note {}'.format(message), 'service_notes_list_html': html}),
                            safe=False)


@login_required
def delete_service_note(request):
    """Delete a service note. All args are contained in resquest form. Returns a JSON data.

    Args:
        requirement_pk: Requirement ID.
        service_note_pk: Optional. Service note ID. If provided, it updated fields of service note, if not, the method creates a new service note.

    Returns:
        message: String to display to the user.
        html: HTML of the table of service notes to reload table.
    """

    if request.method == 'POST':
        # load existing service note
        service_note = ServiceNote.objects.get(
            pk=request.POST.get('service_note_pk'))
        service_note.delete()

        # load all service notes of the requirement
        service_notes = ServiceNote.objects.filter(
            requirement_id=request.POST.get('requirement_pk'))

        # pre render table to be updated in HTML
        html = render_to_string(
            'customer/service-notes-list.html', context={'service_notes': service_notes})

        return JsonResponse(json.dumps({'message': 'Note deleted', 'service_notes_list_html': html}), safe=False)


@login_required
def save_supplier(request):
    """Save or update a supplier linked to a Requirement. All args are contained in resquest form. Returns a JSON data.

    Args:
        requirement_pk: Requirement ID.
        supplier_pk: Optional. Supplier ID. If provided, it updated fields of supplier, if not, the method creates a new supplier.
        supplier_name: Supplier name.
        supplier_invoice: Supplier invoice.
        supplier_amount: Supplier paid amount.
        supplier_date_paid: Supplier payment date.

    Returns:
        message: String to display to the user.
        html: HTML of the table of suppliers to reload table.
    """

    if request.method == 'POST':

        if request.POST.get('supplier_pk'):
            # if supplier id is provided, load existing supplier
            message = 'updated'
            supplier = Supplier.objects.get(pk=request.POST.get('supplier_pk'))
        else:
            # if supplier id is not provided, create a new supplier
            message = 'saved'
            supplier = Supplier()

        # set supplier fields
        supplier.requirement_id = request.POST.get('requirement_pk')
        supplier.supplier_name = request.POST.get(
            'supplier_name') if request.POST.get('supplier_name') else None
        supplier.supplier_invoice = request.POST.get(
            'supplier_invoice') if request.POST.get('supplier_invoice') else None
        supplier.supplier_amount = request.POST.get(
            'supplier_amount') if request.POST.get('supplier_amount') else None
        supplier.supplier_date_paid = datetime.strptime(request.POST.get(
            'supplier_date_paid'), '%d/%m/%Y').strftime('%Y-%m-%d') if request.POST.get('supplier_date_paid') else None
        supplier.supplier_notes = request.POST.get(
            'supplier_notes') if request.POST.get('supplier_notes') else None

        # save supplier
        supplier.save()

        # load all suppliers of the requirement
        suppliers = Supplier.objects.filter(
            requirement_id=request.POST.get('requirement_pk'))

        # pre render table to be updated in HTML
        html = render_to_string(
            'customer/supplier-list.html', context={'suppliers': suppliers})

        return JsonResponse(json.dumps(
            {'message': '{} {}'.format(request.POST.get('supplier_name'), message), 'supplier_list_html': html}),
            safe=False)


@login_required
def delete_supplier(request):
    """Delete a supplier. All args are contained in resquest form. Returns a JSON data.

    Args:
        requirement_pk: Requirement ID.
        supplier_pk: Optional. Supplier ID. If provided, it updated fields of supplier, if not, the method creates a new supplier.

    Returns:
        message: String to display to the user.
        html: HTML of the table of suppliers to reload table.
    """

    if request.method == 'POST':
        # load existing supplier
        supplier = Supplier.objects.get(pk=request.POST.get('supplier_pk'))
        supplier.delete()
        message = 'deleted'

        # load all suppliers of the requirement
        suppliers = Supplier.objects.filter(
            requirement_id=request.POST.get('requirement_pk'))

        # pre render table to be updated in HTML
        html = render_to_string(
            'customer/supplier-list.html', context={'suppliers': suppliers})

        return JsonResponse(json.dumps(
            {'message': '{} {}'.format(request.POST.get('supplier_name'), message), 'supplier_list_html': html}),
            safe=False)


@login_required
def upload_file(request):
    """Upload a file and create File model linked to Customer. All args are contained in resquest form. Returns a JSON data.

    Args:
        file: File to upload.

    Returns:
        message: String to display to the user.
        html: HTML of the table of files uploaded.
    """

    if request.method == 'POST':
        # get file from request and store it in disk
        file = request.FILES['file']
        fs = FileSystemStorage()
        filename = fs.save(file.name, file)
        uploaded_file_url = fs.url(filename)

        # create File model for the uploaded file
        file_model = File(customer_id=request.POST.get(
            'customer_id'), file_name=request.POST.get('file_name'), url=uploaded_file_url)

        file_model.save()

        # pre render table to be updated in HTML
        html = render_to_string('customer/file-list.html', context={'files': File.objects.filter(
            customer_id=request.POST.get('customer_id'))}, request=request)

        return JsonResponse(
            json.dumps({'message': 'File {} uploaded'.format(
                request.POST.get('file_name')), 'file_list_html': html}),
            safe=False)



@login_required
def delete_file(request):
    """delete a file. All args are contained in resquest form. Returns a JSON data.

    Args:
        file: File to delete.

    Returns:
        message: String to display to the user.
        html: HTML of the table of files uploaded.
    """

    if request.method == 'POST':
        # get file from request and store it in disk
        file_id = request.POST.get('file')
        file_model = File.objects.get(id=int(file_id))
        name = file_model.file_name
        os.remove(os.path.join(settings.MEDIA_ROOT, name))


        file_model.delete()

        # pre render table to be updated in HTML
        html = render_to_string('customer/file-list.html', context={'files': File.objects.filter(
            customer_id=request.POST.get('customer_id'))}, request=request)

        return JsonResponse(
            json.dumps({'message': 'File {} Deleted'.format(
                name), 'file_list_html': html}),
            safe=False)



@login_required
def settings_customers(request):
    pass



@login_required
def requirement(request):
    """update all information submitted in customer form. Supplier and File upload are not contained in this endpoint"""
    if request.method == 'POST':
        # Fetch customer data
        customer = Customer.objects.get(id=request.POST.get('pk'))

        if 'btn_delete' in request.POST:
            # Delete the current customer and all his data
            customer.delete()
            messages.warning(request, 'Customer {} was deleted.'.format(
                customer.customer_name))

        else:
            # Fetch requirement and credit card data
            requirement = Requirement.objects.filter(
                customer_id=customer.id).first()
            credit_card = CreditCard.objects.filter(
                customer_id=customer.id).first()

            # Update any customer field from form
            customer.leads_from_id = request.POST.get('leads_from') if request.POST.get(
                'leads_from') else None if 'leads_from' in request.POST else customer.leads_from_id
            customer.sales_person_id = request.POST.get('sales_person') if request.POST.get(
                'sales_person') else None if 'sales_person' in request.POST else customer.sales_person_id
            customer.agm = request.POST.get('agm') if request.POST.get(
                'agm') else None if 'agm' in request.POST else customer.agm
            customer.date_signed = datetime.strptime(request.POST.get('date_signed'), '%d/%m/%Y').strftime(
                '%Y-%m-%d') if request.POST.get(
                'date_signed') else None if 'date_signed' in request.POST else customer.date_signed
            customer.customer_name = request.POST.get('customer_name') if request.POST.get(
                'customer_name') else None if 'customer_name' in request.POST else customer.customer_name
            customer.customer_address = request.POST.get('customer_address') if request.POST.get(
                'customer_address') else None if 'customer_address' in request.POST else customer.customer_address
            customer.customer_email = request.POST.get('customer_email') if request.POST.get(
                'customer_email') else None if 'customer_email' in request.POST else customer.customer_email
            customer.phone_number = request.POST.get('phone_number') if request.POST.get(
                'phone_number') else None if 'phone_number' in request.POST else customer.phone_number
            customer.follow_up = request.POST.get('follow_up') if request.POST.get(
                'follow_up') else None if 'follow_up' in request.POST else customer.follow_up
            customer.customer_notes = request.POST.get('customer_notes') if request.POST.get(
                'customer_notes') else None if 'customer_notes' in request.POST else customer.customer_notes
            customer.customer_check = True if request.POST.get(
                'customer_check') else False

            customer.save()

            # Update requirement field from form
            requirement.kw = request.POST.get('kw') if request.POST.get(
                'kw') else None if 'kw' in request.POST else requirement.kw
            requirement.panel = request.POST.get('panel') if request.POST.get(
                'panel') else None if 'panel' in request.POST else requirement.panel
            requirement.panel_pcs = request.POST.get('panel_pcs') if request.POST.get(
                'panel_pcs') else None if 'panel_pcs' in request.POST else requirement.panel_pcs
            requirement.inverter = request.POST.get('inverter') if request.POST.get(
                'inverter') else None if 'inverter' in request.POST else requirement.inverter
            requirement.inverter_pcs = request.POST.get('inverter_pcs') if request.POST.get(
                'inverter_pcs') else None if 'inverter_pcs' in request.POST else requirement.inverter_pcs
            requirement.roof_type_id = request.POST.get('roof_type') if request.POST.get(
                'roof_type') else None if 'roof_type' in request.POST else requirement.roof_type_id
            requirement.storey_id = request.POST.get('storey') if request.POST.get(
                'storey') else None if 'storey' in request.POST else requirement.storey_id
            requirement.electric_power_id = request.POST.get('electric_power') if request.POST.get(
                'electric_power') else None if 'electric_power' in request.POST else requirement.electric_power_id
            requirement.installation_notes = request.POST.get('installation_notes') if request.POST.get(
                'installation_notes') else None if 'installation_notes' in request.POST else requirement.installation_notes
            requirement.extra_amount = request.POST.get('extra_amount') if request.POST.get(
                'extra_amount') else None if 'extra_amount' in request.POST else requirement.extra_amount
            requirement.total_price = request.POST.get('total_price') if request.POST.get(
                'total_price') else None if 'total_price' in request.POST else requirement.total_price
            requirement.deposit_amount = request.POST.get('deposit_amount') if request.POST.get(
                'deposit_amount') else None if 'deposit_amount' in request.POST else requirement.deposit_amount
            requirement.last_amount = request.POST.get('last_amount') if request.POST.get(
                'last_amount') else None if 'last_amount' in request.POST else requirement.last_amount

            requirement.system_price = request.POST.get('system_price') if request.POST.get(
                'system_price') else None if 'system_price' in request.POST else requirement.system_price

            requirement.MNI = request.POST.get('MNI') if request.POST.get(
                'MNI') else None if 'MNI' in request.POST else requirement.MNI

            requirement.finance = request.POST.get('finance') if request.POST.get(
                'finance') else None if 'finance' in request.POST else requirement.finance

            requirement.application = True if request.POST.get(
                'Application') else False

            requirement.installation_date = datetime.strptime(request.POST.get('installation_date'),
                                                              '%d/%m/%Y').strftime(
                '%Y-%m-%d') if request.POST.get(
                'installation_date') else None if 'installation_date' in request.POST else requirement.installation_date
            requirement.installer_id = request.POST.get('installer') if request.POST.get(
                'installer') else None if 'installer' in request.POST else requirement.installer_id

            requirement.installer_date_paid = datetime.strptime(request.POST.get('installer_date_paid'),
                                                                '%d/%m/%Y').strftime('%Y-%m-%d') if request.POST.get(
                'installer_date_paid') else None if 'installer_date_paid' in request.POST else requirement.installer_date_paid

            requirement.installer_amount = request.POST.get('installer_amount') if request.POST.get(
                'installer_amount') else None if 'installer_amount' in request.POST else requirement.installer_amount

            requirement.Installer_notes = request.POST.get('installer_notes') if request.POST.get(
                'installer_notes') else None if 'installer_notes' in request.POST else requirement.Installer_notes

            requirement.deposit_date_paid = datetime.strptime(request.POST.get('deposit_date_paid'),
                                                              '%d/%m/%Y').strftime('%Y-%m-%d') if request.POST.get(
                'deposit_date_paid') else None if 'deposit_date_paid' in request.POST else requirement.deposit_date_paid

            requirement.deposit_payment_id = request.POST.get('deposit_payment') if request.POST.get(
                'deposit_payment') else None if 'deposit_payment' in request.POST else requirement.deposit_payment_id

            requirement.unit = float(request.POST.get('Unit')) if request.POST.get(
                'Unit') else None if 'Unit' in request.POST else requirement.unit

            requirement.unit_price = request.POST.get('unit_price') if request.POST.get(
                'unit_price') else None if 'unit_price' in request.POST else requirement.unit_price

            requirement.stc_application = True if request.POST.get(
                'Stc_Application') else False

            requirement.balance_due = datetime.strptime(request.POST.get('Balance_due'), '%d/%m/%Y').strftime(
                '%Y-%m-%d') if request.POST.get(
                'Balance_due') else None if 'Balance_due' in request.POST else requirement.balance_due


            requirement.stc_notes = request.POST.get('stc_notes') if request.POST.get(
                'stc_notes') else None if 'stc_notes' in request.POST else requirement.stc_notes

            requirement.stc_amount = request.POST.get('Stc') if request.POST.get(
                'Stc') else None if 'Stc' in request.POST else requirement.stc_amount
            requirement.stc_date_paid = datetime.strptime(request.POST.get('stc_date_paid'), '%d/%m/%Y').strftime(
                '%Y-%m-%d') if request.POST.get(
                'stc_date_paid') else None if 'stc_date_paid' in request.POST else requirement.stc_date_paid
            requirement.STC_PAYMENT = request.POST.get('STC_PAYMENT') if request.POST.get(
                'STC_PAYMENT') else None if 'STC_PAYMENT' in request.POST else requirement.STC_PAYMENT
            requirement.last_amount_paid_date = datetime.strptime(request.POST.get('last_amount_paid_date'),
                                                                  '%d/%m/%Y').strftime(
                '%Y-%m-%d') if request.POST.get(
                'last_amount_paid_date') else None if 'last_amount_paid_date' in request.POST else requirement.last_amount_paid_date

            requirement.last_amount_payment = request.POST.get('last_amount_payment') if request.POST.get(
                'last_amount_payment') else None if 'last_amount_payment' in request.POST else requirement.last_amount_payment

            requirement.last_amount_balance_due = request.POST.get('last_amount_balance_due') if request.POST.get(
                'last_amount_balance_due') else None if 'last_amount_balance_due' in request.POST else requirement.last_amount_balance_due

            requirement.last_amount_payment_method_id = request.POST.get(
                'last_amount_payment_method') if request.POST.get(
                'deposit_payment') else None if 'last_amount_payment_method' in request.POST else requirement.last_amount_payment_method_id

            requirement.last_amount_notes = request.POST.get(
                'last_amount_notes') if request.POST.get(
                'last_amount_notes') else None if 'last_amount_notes' in request.POST else requirement.last_amount_notes

            requirement.power_connection = request.POST.get('power_connection') if request.POST.get(
                'power_connection') else None if 'power_connection' in request.POST else requirement.power_connection
            requirement.meter_connection = request.POST.get('meter_connection') if request.POST.get(
                'meter_connection') else None if 'meter_connection' in request.POST else requirement.meter_connection

            try:
                __stc = float(requirement.stc_amount)
            except TypeError:
                __stc = 0
            try:
                __stc_payment = float(requirement.STC_PAYMENT)
            except TypeError:
                __stc_payment = 0
            requirement.stc_amount_payment =  __stc - __stc_payment

            read_only_status = '' #for signed page
            # Check which button was pressed
            if 'btn_already_signed' in request.POST:
                status = 'DEPOSIT'
                read_only_status = 'SIGNED' # for read-only page signed
            elif 'btn_deposit_paid' in request.POST:
                if requirement.finance != "Yes" and all([requirement.deposit_payment, requirement.deposit_date_paid]):
                    status = 'ON_FILE'
                else:
                    status = None
                    messages.error(
                        request, 'You need complete the "Deposite Data" section')
            elif 'btn_payment_order' in request.POST:
                if all([customer.customer_check]):
                    status = 'ORDER'
                    if requirement.finance != "Yes" and all([requirement.deposit_payment, requirement.deposit_date_paid]):
                        status = 'ORDER'
                    else:
                        status = None
                        messages.error(
                            request, 'You need complete the "Deposite Data" section')
                else:
                    status = None
                    messages.error(
                        request, 'Customer has to be checked before promoting to order')

            elif 'btn_confirm_all' in request.POST:
                # if customer_check and deposite_date_paid or finance == Yes
                # the status has INSTALLATION and order_paid = True
                if all([customer.customer_check, requirement.deposit_date_paid]) or \
                                                        requirement.finance == "Yes":
                    status = 'INSTALLATION'
                    requirement.order_paid = True
                    if requirement.finance != "Yes" and all([requirement.deposit_payment, requirement.deposit_date_paid]):
                        pass
                    else:
                        status = None
                        messages.error(
                            request, 'You need complete the "Deposite Data" section')

                else:
                    status = None
                    messages.error(
                        request, 'Customer has to be checked and deposit has to be paid before confirming')
            elif 'btn_order_paid' in request.POST:
                if all([requirement.deposit_date_paid]) or requirement.finance == "Yes":
                    status = 'INSTALLATION'
                    requirement.order_paid = True
                else:
                    status = None
                    messages.error(
                        request, 'Deposit has to be paid before finishing')
            elif 'btn_finish_installation' in request.POST:
                if requirement.finance != "Yes" and all([requirement.deposit_payment, requirement.deposit_date_paid]):
                    status = 'ACCOUNT'
                else:
                    status = None
                    messages.error(
                        request, 'You need complete the "Deposite Data" section')
            elif 'btn_all_paid' in request.POST:
                if all([requirement.deposit_date_paid, requirement.stc_date_paid, requirement.last_amount_paid_date,
                        requirement.suppliers_paid, requirement.installer_date_paid]):
                    status = 'FINISHED'
                else:
                    if not customer.created_from_account:
                        status = None
                        messages.error(
                            request, 'All amounts have to be paid before finishing')
                    elif customer.created_from_account:
                        status = 'FINISHED'
            elif 'btn_service' in request.POST:
                status = 'SERVICE'
            elif 'btn_delivered' in request.POST:
                status = 'DELIVERED'
            elif 'btn_delivered_home' in request.POST:
                status = 'DELIVERED_HOME'
            elif 'btn_service_home' in request.POST:
                status = 'SERVICE_HOME'
            else:
                status = None

            requirement.status = status if status else requirement.status if requirement.status else None
            requirement.save()

            # Update any credit card field from form
            credit_card.credit_card = request.POST.get('credit_card') if request.POST.get(
                'credit_card') else None if 'credit_card' in request.POST else credit_card.credit_card
            credit_card.expires = datetime.strptime(request.POST.get('expires'), '%m/%Y').strftime(
                '%Y-%m-01') if request.POST.get(
                'expires') else None if 'expires' in request.POST else credit_card.expires

            credit_card.save()

            # Build message to show what was updated
            status_message = ' moved to {}'.format(
                status) if status else ' saved'
            messages.success(request, 'Customer {}{}.'.format(
                request.POST.get('customer_name'), status_message))
            if read_only_status:
                 messages.success(request,f"Customer {request.POST.get('customer_name')} moved to {read_only_status}")

        if 'btn_save' in request.POST or customer.created_from_account:
            return redirect(request.META['HTTP_REFERER'])
        elif 'btn_finish_installation' in request.POST:
            return HttpResponseRedirect('/account')
        else:
            return redirect('home')


@login_required
@permission_required(['customer.deposit_list'])
def deposit_list(request):
    """Returns List of customers in DEPOSIT"""
    if request.method == 'GET':
        # Get all requirements in DEPOSIT status
        if request.user.has_perm('customer.customer_view_others'):
            requirements = Requirement.objects.filter(
                status="DEPOSIT").distinct().order_by('customer__date_signed')
        else:
            requirements = Requirement.objects.filter(Q(customer__sales_person=request.user) | Q(
                installer=request.user), status="DEPOSIT").distinct().order_by('customer__date_signed')

        # Set columns to display.
        # IMPORTANT: to set columns in dict "columns",
        # 'key' is the title of the column and 'value' is the field in requirement object,
        # e.g. to get the customer name, 'requirement' object has an attribute 'customer' and this has an attribute 'customer_name'
        # so to retrieve it you will use 'customer.customer_name'
        columns = {
            'Data signed': 'customer.date_signed',
            'Sales': 'customer.sales_person',
            'AGM': 'customer.agm',
            'Customer Name': 'customer.customer_name',
            'Phone': 'customer.phone_number',
            'Address': 'customer.customer_address',
            'Deposit': 'deposit_paid',
            'Finance': 'finance',
            'Customer Check': 'customer.customer_check',
            'Install notes': 'installation_notes',
        }

        # Set template context
        #   requirements: Requirements data
        #   url_view: name of url to enter each customer form
        #   columns: colums definition
        #   colspan: number of columns of the table. used to display a 'No results' message when empty
        #   current_tab: name of the current tab to set active class
        
        context = {
            'requirements': requirements,
            'url_view': 'deposit-view',
            'columns': columns,
            'colspan': len(columns) + 2,
            'deposit_search_field_visible': True,
            'current_tab': 'deposit-tab'
        }
        # Return requirement list in DEPOSIT status
        return render(request, 'customer/requirement-list.html', context=context)


@login_required
def deposit_search(request):
    """Returns List of customers in DEPOSIT"""
    if request.method == 'POST':
        # get Search Key data from search form
        search_value = request.POST.get('search_value')
        print("========================")

        # Get all requirements in DEPOSIT status
        if request.user.has_perm('customer.customer_view_others'):
            requirements = Requirement.objects.filter(
                Q(customer__customer_name__contains=search_value) |
                Q(customer__customer_address__contains=search_value) |
                Q(customer__customer_email__contains=search_value) |
                Q(customer__phone_number__contains=search_value) |
                Q(customer__agm__contains=search_value),
                status="DEPOSIT").distinct()
        else:
            requirements = Requirement.objects.filter(
                Q(customer__sales_person=request.user) |
                Q(customer__customer_name__contains=search_value) |
                Q(customer__customer_address__contains=search_value) |
                Q(customer__customer_email__contains=search_value) |
                Q(customer__phone_number__contains=search_value) |
                Q(customer__agm__contains=search_value) |
                Q(installer=request.user), status="DEPOSIT").distinct()

        # Set columns to display.
        # IMPORTANT: to set columns in dict "columns",
        # 'key' is the title of the column and 'value' is the field in requirement object,
        # e.g. to get the customer name, 'requirement' object has an attribute 'customer' and this has an attribute 'customer_name'
        # so to retrieve it you will use 'customer.customer_name'
        columns = {
            'Data signed': 'customer.date_signed',
            'Sales': 'customer.sales_person',
            'AGM': 'customer.agm',
            'Customer Name': 'customer.customer_name',
            'Phone': 'customer.phone_number',
            'Address': 'customer.customer_address',
            'Deposit': 'deposit_paid',
            'Finance': 'finance',
            'Customer Check': 'customer.customer_check',
            'Install notes': 'installation_notes',
        }

        # Set template context
        #   requirements: Requirements data
        #   url_view: name of url to enter each customer form
        #   columns: colums definition
        #   colspan: number of columns of the table. used to display a 'No results' message when empty
        #   current_tab: name of the current tab to set active class
        context = {
            'requirements': requirements,
            'url_view': 'deposit-view',
            'columns': columns,
            'colspan': len(columns) + 2,
            'deposit_search_field_visible': True,
            'search_value': search_value,
            'current_tab': 'deposit-tab',
        }

        # Return requirement list in DEPOSIT status
        return render(request, 'customer/requirement-list.html', context=context)


@login_required
@permission_required(['customer.deposit_view'])
def deposit_view(request, pk):
    """Returns a customer form in DEPOSIT status"""
    customer = Customer.objects.get(id=pk)

    # Set context.
    # leads, sales_people, roof_types, storeys, electric_powers, payments are default options loaded in Django admin
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
        'installation_notes': True,
        'electric_power': True,
        'extra_amount': True,
        'total_price': True,
        'deposit_amount': True,
        'last_amount': True
    }
    required_fields = {
        'customer_fields': customer_fields,
        'system_fields': system_fields
    }
    context = {
        'current_tab': 'deposit-tab',
        'leads': Lead.objects.all(),
        'sales_people': get_user_model().objects.filter(profile__title='salesman'),
        'roof_types': RoofType.objects.all(),
        'storeys': Storey.objects.all(),
        'electric_powers': ElectricPower.objects.all(),
        'customer': customer,
        'requirement': Requirement.objects.filter(customer_id=customer.id).first(),
        'credit_card': CreditCard.objects.filter(customer_id=customer.id).first(),
        'files': File.objects.filter(customer_id=customer.id),
        'payments': Payment.objects.all(),
        'power_meter_connection_disable': True,
        'required_fields': required_fields,
        'options': {
            'user_created_enabled': True,
            'customer_data_enabled': True,
            'requirement_data_enabled': True,
            'service_data_enabled': False,
            'follow_up': False,
            'file_upload_enabled': True,
            'file_list_enabled': True,
            'installation_data_enabled': False,
            'customer_check_enabled': True,
            'deposit_info_enabled': True,
            'installer_payment_data_enabled': True,
            'supplier_list_enabled': False,
            'Finance': True,
            'buttons': [
                {
                    'btn_promote_name': 'btn_deposit_paid',
                    'btn_promote_text': 'Deposit Paid'
                }
            ]
        }
    }

    # Return customer form for DEPOSIT status
    return render(request, 'customer/customer-full-form.html', context=context)

@login_required
@permission_required(['customer.sales_signed'])
def salesSigned_list(request):
    """Returns List of customers in SIGNED"""
    if request.method == 'GET':
        # Get all requirements in DEPOSIT status
        if request.user.has_perm('customer.customer_view_others'):
            requirements = Requirement.objects.filter(Q(status="DEPOSIT") |
                Q(status="ON_FILE") | Q(status="ORDER") |
                Q(status="ACCOUNT") | Q(status="INSTALLATION") |
                Q(status="SERVICE") | Q(status="FINISHED")).distinct().order_by('-customer__date_signed')
        else:
            requirements = Requirement.objects.filter(Q(customer__sales_person=request.user) | Q(
                installer=request.user), Q(status="DEPOSIT") |
                Q(status="ON_FILE") | Q(status="ORDER") |
                Q(status="ACCOUNT") | Q(status="INSTALLATION") |
                Q(status="SERVICE") | Q(status="FINISHED")).distinct().order_by('-customer__date_signed')

        # Set columns to display.
        # IMPORTANT: to set columns in dict "columns",
        # 'key' is the title of the column and 'value' is the field in requirement object,
        # e.g. to get the customer name, 'requirement' object has an attribute 'customer' and this has an attribute 'customer_name'
        # so to retrieve it you will use 'customer.customer_name'
        columns = {
            'Date signed': 'customer.date_signed',
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
            'columns': columns,
            'colspan': len(columns) + 2,
            'signed_search_field_visible': True,
            'current_tab': 'signed-tab'

        }
        # Return requirement list in SIGNED status
        return render(request, 'customer/requirement-list.html', context=context)

@login_required
@permission_required(['customer.sales_signed'])
def salesSigned_search(request):
    if request.method == 'POST':
        # get Search Key data from search form
        search_value = request.POST.get('search_value')

        # Get all requirements in SIGNED status
        if request.user.has_perm('customer.customer_view_others'):
            requirements = Requirement.objects.filter(
                Q(customer__customer_name__contains=search_value) |
                Q(customer__customer_address__contains=search_value) |
                Q(customer__customer_email__contains=search_value) |
                Q(customer__phone_number__contains=search_value) |
                Q(customer__agm__contains=search_value)).distinct()
        else:
            requirements = Requirement.objects.filter(
                Q(customer__sales_person=request.user) |
                Q(customer__customer_name__contains=search_value) |
                Q(customer__customer_address__contains=search_value) |
                Q(customer__customer_email__contains=search_value) |
                Q(customer__phone_number__contains=search_value) |
                Q(customer__agm__contains=search_value) |
                Q(installer=request.user)).distinct()

        # Set columns to display.
        # IMPORTANT: to set columns in dict "columns",
        # 'key' is the title of the column and 'value' is the field in requirement object,
        # e.g. to get the customer name, 'requirement' object has an attribute 'customer' and this has an attribute 'customer_name'
        # so to retrieve it you will use 'customer.customer_name'
        columns = {
            'Date signed': 'customer.date_signed',
            'Sales': 'customer.sales_person',
            'AGM': 'customer.agm',
            'Customer Name': 'customer.customer_name',
            'Phone': 'customer.phone_number',
            'Address': 'customer.customer_address',
            'Deposit': 'deposit_paid',
            'Finance': 'finance',
            'Customer Check': 'customer.customer_check',
            'Install notes': 'installation_notes',
        }

        # Set template context
        #   requirements: Requirements data
        #   url_view: name of url to enter each customer form
        #   columns: colums definition
        #   colspan: number of columns of the table. used to display a 'No results' message when empty
        #   current_tab: name of the current tab to set active class
        context = {
            'requirements': requirements,
            'columns': columns,
            'colspan': len(columns) + 2,
            'signed_search_field_visible': True,
            'search_value': search_value,
            'current_tab': 'signed-tab',
        }

        # Return requirement list in DEPOSIT status
        return render(request, 'customer/requirement-list.html', context=context)

@login_required
@permission_required(['customer.sales_signed'])
def salesSigned_view(request,pk):
    """Returns a customer form in already SIGNED status"""
    customer = Customer.objects.get(id=pk)

    # Set context.
    # leads, sales_people, roof_types, storeys, electric_powers, payments are default options loaded in Django admin
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
        'installation_notes': True,
        'electric_power': True,
        'extra_amount': True,
        'total_price': True,
        'deposit_amount': True,
        'last_amount': True
    }
    required_fields = {
        'customer_fields': customer_fields,
        'system_fields': system_fields
    }
    context = {
        'current_tab': 'signed-tab',
        'leads': Lead.objects.all(),
        'sales_people': get_user_model().objects.filter(profile__title='salesman'),
        'roof_types': RoofType.objects.all(),
        'storeys': Storey.objects.all(),
        'electric_powers': ElectricPower.objects.all(),
        'customer': customer,
        'requirement': Requirement.objects.filter(customer_id=customer.id).first(),
        'credit_card': CreditCard.objects.filter(customer_id=customer.id).first(),
        'files': File.objects.filter(customer_id=customer.id),
        'payments': Payment.objects.all(),
        'power_meter_connection_disable': True,
        'required_fields': required_fields,
        'options': {
            'user_created_enabled': True,
            'customer_data_enabled': True,
            'requirement_data_enabled': True,
            'service_data_enabled': False,
            'follow_up': False,
            'file_upload_enabled': True,
            'file_list_enabled': True,
            'installation_data_enabled': False,
            'customer_check_enabled': True,
            'deposit_info_enabled': True,
            'installer_payment_data_enabled': True,
            'supplier_list_enabled': False,
            'Finance': True,

        }
    }

    # Return customer form for Already signed status
    return render(request, 'customer/customer-full-form.html', context=context)



@login_required
@permission_required(['customer.on_file_list'])
def on_file_list(request):
    """Returns List of customers in ON_FILE"""
    if request.method == 'GET':
        # Get all requirements in ON_FILE status
        if request.user.has_perm('customer.customer_view_others'):
            requirements = Requirement.objects.filter(
                status="ON_FILE").distinct().order_by('customer__date_signed')
        else:
            requirements = Requirement.objects.filter(Q(customer__sales_person=request.user) | Q(
                installer=request.user), status="ON_FILE").distinct().order_by('customer__date_signed')

        # Set columns to display.
        # IMPORTANT: to set columns in dict "columns",
        # 'key' is the title of the column and 'value' is the field in requirement object,
        # e.g. to get the customer name, 'requirement' object has an attribute 'customer' and this has an attribute 'customer_name'
        # so to retrieve it you will use 'customer.customer_name'
        columns = {
            'Data signed': 'customer.date_signed',
            'Sales': 'customer.sales_person',
            'AGM': 'customer.agm',
            'Customer Name': 'customer.customer_name',
            'Phone': 'customer.phone_number',
            'Address': 'customer.customer_address',
            'Deposit': 'deposit_paid',
            'Finance': 'finance',
            'Customer Check': 'customer.customer_check',
            'Con/ap': 'application',
            'Install notes': 'installation_notes',
        }

        # Set template context
        #   requirements: Requirements data
        #   url_view: name of url to enter each customer form
        #   columns: colums definition
        #   colspan: number of columns of the table. used to display a 'No results' message when empty
        #   current_tab: name of the current tab to set active class
        context = {
            'requirements': requirements,
            'url_view': 'on-file-view',
            'columns': columns,
            'colspan': len(columns) + 2,
            'on_file_search_visible': True,
            'current_tab': 'on-file-tab'
        }

        # Return requirement list in ON_FILE status
        return render(request, 'customer/requirement-list.html', context=context)


@login_required
def on_file_search(request):
    """Returns List of customers in ON_FILE"""
    if request.method == 'POST':

        # get Search Key data from search form
        search_value = request.POST.get('search_value')
        print("========================")

        # Get all requirements in ON_FILE status
        if request.user.has_perm('customer.customer_view_others'):
            requirements = Requirement.objects.filter(
                Q(customer__customer_name__contains=search_value) |
                Q(customer__customer_address__contains=search_value) |
                Q(customer__customer_email__contains=search_value) |
                Q(customer__phone_number__contains=search_value) |
                Q(customer__agm__contains=search_value),
                status="ON_FILE").distinct()
        else:
            requirements = Requirement.objects.filter(
                Q(customer__sales_person=request.user) |
                Q(customer__customer_name__contains=search_value) |
                Q(customer__customer_address__contains=search_value) |
                Q(customer__customer_email__contains=search_value) |
                Q(customer__phone_number__contains=search_value) |
                Q(customer__agm__contains=search_value) |
                Q(installer=request.user), status="ON_FILE").distinct()

        # Set columns to display.
        # IMPORTANT: to set columns in dict "columns",
        # 'key' is the title of the column and 'value' is the field in requirement object,
        # e.g. to get the customer name, 'requirement' object has an attribute 'customer' and this has an attribute 'customer_name'
        # so to retrieve it you will use 'customer.customer_name'
        columns = {
            'Data signed': 'customer.date_signed',
            'Sales': 'customer.sales_person',
            'AGM': 'customer.agm',
            'Customer Name': 'customer.customer_name',
            'Phone': 'customer.phone_number',
            'Address': 'customer.customer_address',
            'Deposit': 'deposit_paid',
            'Customer Check': 'customer.customer_check',
            'Con/ap': 'application',
            'Install notes': 'installation_notes',
        }

        # Set template context
        #   requirements: Requirements data
        #   url_view: name of url to enter each customer form
        #   columns: colums definition
        #   colspan: number of columns of the table. used to display a 'No results' message when empty
        #   current_tab: name of the current tab to set active class
        context = {
            'requirements': requirements,
            'url_view': 'on-file-view',
            'columns': columns,
            'colspan': len(columns) + 2,
            'on_file_search_visible': True,
            'search_value': search_value,
            'current_tab': 'on-file-tab'
        }

        # Return requirement list in ON_FILE status
        return render(request, 'customer/requirement-list.html', context=context)


@login_required
@permission_required(['customer.on_file_view'])
def on_file_view(request, pk):
    """Returns a customer form in ON_FILE status"""
    customer = Customer.objects.get(id=pk)
    requirement = Requirement.objects.filter(customer_id=customer.id).first()

    # Set context.
    # leads, sales_people, roof_types, storeys, electric_powers, payments, installers are default options loaded in Django admin
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
        'installation_notes': True,
        'electric_power': True,
        'extra_amount': True,
        'total_price': True,
        'deposit_amount': True,
        'last_amount': True,
        'power_connection': True
    }
    installation_fields = {
        'installation_date': True,
        'installer': True
    }
    supplier_fields = {
        'supplier_name': True,
        'supplier_invoice': False,
        'supplier_amount': False,
        'supplier_date_paid': False,
        'supplier_notes': False
    }
    required_fields = {
        'customer_fields': customer_fields,
        'system_fields': system_fields,
        'installation_fields': installation_fields,
        'supplier_fields': supplier_fields
    }
    context = {
        'current_tab': 'on-file-tab',
        'leads': Lead.objects.all(),
        'sales_people': get_user_model().objects.filter(profile__title='salesman'),
        'roof_types': RoofType.objects.all(),
        'storeys': Storey.objects.all(),
        'electric_powers': ElectricPower.objects.all(),
        'installers': get_user_model().objects.filter(profile__title='installer'),
        'customer': customer,
        'requirement': requirement,
        'credit_card': CreditCard.objects.filter(customer_id=customer.id).first(),
        'files': File.objects.filter(customer_id=customer.id),
        'payments': Payment.objects.all(),
        'suppliers': Supplier.objects.filter(requirement_id=requirement.id),
        'required_fields': required_fields,
        'options': {
            'user_created_enabled': True,
            'customer_data_enabled': True,
            'requirement_data_enabled': True,
            'service_data_enabled': False,
            'follow_up': False,
            'file_upload_enabled': True,
            'file_list_enabled': True,
            'installation_data_enabled': True,
            'customer_check_enabled': True,
            'deposit_info_enabled': True,
            'installer_payment_data_enabled': True,
            'supplier_list_enabled': True,
            'Finance': True,
            'buttons': [
                {
                    'btn_promote_name': 'btn_confirm_all',
                    'btn_promote_text': 'Confirm All'
                },
                {
                    'btn_promote_name': 'btn_payment_order',
                    'btn_promote_text': 'Payment Order'
                }
            ]
        }
    }

    # Return customer form for ON_FILE status
    return render(request, 'customer/customer-full-form.html', context=context)


@login_required
@permission_required(['customer.order_list'])
def order_list(request):
    """Returns List of customers in ORDER"""
    if request.method == 'GET':
        # Get all requirements in ORDER status
        if request.user.has_perm('customer.customer_view_others'):
            requirements = Requirement.objects.filter(
                status="ORDER").distinct().order_by('installation_date')
        else:
            requirements = Requirement.objects.filter(Q(customer__sales_person=request.user) | Q(
                installer=request.user), status="ORDER").distinct().order_by('installation_date')

        order = {}
        for requirement in requirements:
            suppliers = Supplier.objects.filter(requirement_id=requirement.id)
            amount = 0
            supplier_exisits = False
            Amount_exists = False
            for supplier in suppliers:
                supplier_exisits = True
                if supplier.supplier_date_paid is None:
                    try:
                        amount += supplier.supplier_amount
                        Amount_exists = True

                    except TypeError:
                        pass
                else:
                    Amount_exists = True

            if supplier_exisits == False:
                order[requirement.id] = '_'
            elif Amount_exists == False:
                order[requirement.id] = '_'
            elif amount == 0 and supplier_exisits:
                order[requirement.id] = 'Paid'
            else:
                order[requirement.id] = '$ ' + str(amount)

        # Set columns to display.
        # IMPORTANT: to set columns in dict "columns",
        # 'key' is the title of the column and 'value' is the field in requirement object,
        # e.g. to get the customer name, 'requirement' object has an attribute 'customer' and this has an attribute 'customer_name'
        # so to retrieve it you will use 'customer.customer_name'
        columns = {
            'Installation Date': 'installation_date',
            'Sales': 'customer.sales_person',
            'AGM': 'customer.agm',
            'Customer Name': 'customer.customer_name',
            'Phone': 'customer.phone_number',
            'Address': 'customer.customer_address',
            'Order': 'True',
            'Customer Check': 'customer.customer_check',
            'Con/ap': 'application',
            'Install notes': 'installation_notes',

        }

        # Set template context
        #   requirements: Requirements data
        #   url_view: name of url to enter each customer form
        #   columns: colums definition
        #   colspan: number of columns of the table. used to display a 'No results' message when empty
        #   current_tab: name of the current tab to set active class
        context = {
            'requirements': requirements,
            'url_view': 'order-view',
            'columns': columns,
            'colspan': len(columns) + 2,
            'order_search_field_visibie': True,
            'current_tab': 'order-tab',
            'OrderFlag': True,
            'order': order
        }

        # Return requirement list in ORDER status
        return render(request, 'customer/requirement-list.html', context=context)


@login_required
def order_search(request):
    """Returns List of customers in ORDER"""
    if request.method == 'POST':
        # get Search Key data from search form
        search_value = request.POST.get('search_value')
        print("========================")

        # Get all requirements in ORDER status
        if request.user.has_perm('customer.customer_view_others'):
            requirements = Requirement.objects.filter(
                Q(customer__customer_name__contains=search_value) |
                Q(customer__customer_address__contains=search_value) |
                Q(customer__customer_email__contains=search_value) |
                Q(customer__phone_number__contains=search_value) |
                Q(customer__agm__contains=search_value),
                status="ORDER").distinct()
        else:
            requirements = Requirement.objects.filter(
                Q(customer__sales_person=request.user) |
                Q(customer__customer_name__contains=search_value) |
                Q(customer__customer_address__contains=search_value) |
                Q(customer__customer_email__contains=search_value) |
                Q(customer__phone_number__contains=search_value) |
                Q(customer__agm__contains=search_value) |
                Q(installer=request.user), status="ORDER").distinct()

        # Set columns to display.
        # IMPORTANT: to set columns in dict "columns",
        # 'key' is the title of the column and 'value' is the field in requirement object,
        # e.g. to get the customer name, 'requirement' object has an attribute 'customer' and this has an attribute 'customer_name'
        # so to retrieve it you will use 'customer.customer_name'
        columns = {
            'Installation Date': 'installation_date',
            'Sales': 'customer.sales_person',
            'AGM': 'customer.agm',
            'Customer Name': 'customer.customer_name',
            'Phone': 'customer.phone_number',
            'Address': 'customer.customer_address',
            'Customer Check': 'customer.customer_check',
            'Con/ap': 'application',
            'Install notes': 'installation_notes',

        }

        # Set template context
        #   requirements: Requirements data
        #   url_view: name of url to enter each customer form
        #   columns: colums definition
        #   colspan: number of columns of the table. used to display a 'No results' message when empty
        #   current_tab: name of the current tab to set active class
        context = {
            'requirements': requirements,
            'url_view': 'order-view',
            'columns': columns,
            'colspan': len(columns) + 2,
            'order_search_field_visibie': True,
            'search_value': search_value,
            'current_tab': 'order-tab'
        }

        # Return requirement list in ORDER status
        return render(request, 'customer/requirement-list.html', context=context)


@login_required
@permission_required(['customer.order_view'])
def order_view(request, pk):
    """Returns a customer form in ORDER status"""
    customer = Customer.objects.get(id=pk)
    requirement = Requirement.objects.filter(customer_id=customer.id).first()

    # Set context.
    # leads, sales_people, roof_types, storeys, electric_powers, payments, installers are default options loaded in Django admin
    # requirement, credit_card, files are loaded from current customer
    # suppliers is loaded from current requirement
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
        'installation_notes': True,
        'electric_power': True,
        'extra_amount': True,
        'total_price': True,
        'deposit_amount': True,
        'last_amount': True,
        'power_connection': True
    }
    installation_fields = {
        'installation_date': True,
        'installer': True
    }
    supplier_fields = {
        'supplier_name': True,
        'supplier_invoice': True,
        'supplier_amount': True,
        'supplier_date_paid': False,
        'supplier_notes': False
    }
    required_fields = {
        'customer_fields': customer_fields,
        'system_fields': system_fields,
        'installation_fields': installation_fields,
        'supplier_fields': supplier_fields
    }
    context = {
        'current_tab': 'order-tab',
        'leads': Lead.objects.all(),
        'sales_people': get_user_model().objects.filter(profile__title='salesman'),
        'roof_types': RoofType.objects.all(),
        'storeys': Storey.objects.all(),
        'electric_powers': ElectricPower.objects.all(),
        'installers': get_user_model().objects.filter(profile__title='installer'),
        'customer': customer,
        'requirement': requirement,
        'credit_card': CreditCard.objects.filter(customer_id=customer.id).first(),
        'files': File.objects.filter(customer_id=customer.id),
        'suppliers': Supplier.objects.filter(requirement_id=requirement.id),
        'payments': Payment.objects.all(),
        'options': {
            'user_created_enabled': True,
            'customer_data_enabled': True,
            'requirement_data_enabled': True,
            'service_data_enabled': False,
            'follow_up': False,
            'file_upload_enabled': True,
            'file_list_enabled': True,
            'installation_data_enabled': True,
            'customer_check_enabled': True,
            'deposit_info_enabled': True,
            'installer_payment_data_enabled': True,
            'supplier_list_enabled': True,
            'Finance': True,
            'required_fields': required_fields,
            'buttons': [
                {
                    'btn_promote_name': 'btn_order_paid',
                    'btn_promote_text': 'Order Paid'
                }
            ]
        }
    }

    # Return customer form for ORDER status
    return render(request, 'customer/customer-full-form.html', context=context)


@login_required
@permission_required(['customer.installation_list'])
def installation_list(request):
    """Returns List of customers in ORDER and INSTALLATION"""
    if request.method == 'GET':
        # Get all requirements in ORDER and INSTALLATION status
        if request.user.has_perm('customer.customer_view_others'):
            requirements = Requirement.objects.filter(
                Q(status="ORDER") | Q(status="INSTALLATION")).distinct().order_by('installation_date') # order by oldest
        else:
            requirements = Requirement.objects.filter((Q(customer__sales_person=request.user) | Q(
                installer=request.user)) & (Q(status="ORDER") | Q(status="INSTALLATION"))).distinct().order_by('installation_date') # order by latest

        order = {}
        for requirement in requirements:
            suppliers = Supplier.objects.filter(requirement_id=requirement.id)
            amount = 0
            supplier_exisits = False
            Amount_exists = False
            for supplier in suppliers:
                supplier_exisits = True
                if supplier.supplier_date_paid is None:
                    try:
                        amount += supplier.supplier_amount
                        Amount_exists = True

                    except TypeError:
                        pass
                else:
                    Amount_exists = True

            if supplier_exisits == False:
                order[requirement.id] = '_'
            elif  Amount_exists == False:
                order[requirement.id] = '_'
            elif amount == 0 and supplier_exisits:
                order[requirement.id] = 'Paid'
            else:
                order[requirement.id] = '$ ' + str(amount)

        # Set columns to display.
        # IMPORTANT: to set columns in dict "columns",
        # 'key' is the title of the column and 'value' is the field in requirement object,
        # e.g. to get the customer name, 'requirement' object has an attribute 'customer' and this has an attribute 'customer_name'
        # so to retrieve it you will use 'customer.customer_name'
        columns = {
            'Installation Date': 'installation_date',
            'Installer': 'installer',
            'AGM': 'customer.agm',
            'Customer Name': 'customer.customer_name',
            'Phone': 'customer.phone_number',
            'Address': 'customer.customer_address',
            'Order': 'True',
            'Customer Check': 'customer.customer_check',
            'Con/ap': 'application',
            'Install notes': 'installation_notes',

        }

        # Set template context
        #   requirements: Requirements data
        #   url_view: name of url to enter each customer form
        #   columns: colums definition
        #   colspan: number of columns of the table. used to display a 'No results' message when empty
        #   current_tab: name of the current tab to set active class
        context = {
            'requirements': requirements,
            'url_view': 'installation-view',
            'columns': columns,
            'colspan': len(columns) + 2,
            'installation_search_field_visible': True,
            'current_tab': 'installation-tab',
            'OrderFlag': True,
            'order': order
        }

        # Return requirement list in ORDER and INSTALLATION status
        return render(request, 'customer/requirement-list.html', context=context)


@login_required
def installation_search(request):
    """Returns List of customers in ORDER and INSTALLATION"""
    if request.method == 'POST':

        # get Search Key data from search form
        search_value = request.POST.get('search_value')
        print("========================")

        # Get all requirements in ORDER and INSTALLATION status
        if request.user.has_perm('customer.customer_view_others'):
            requirements = Requirement.objects.filter(
                Q(customer__customer_name__contains=search_value) |
                Q(customer__customer_address__contains=search_value) |
                Q(customer__customer_email__contains=search_value) |
                Q(customer__phone_number__contains=search_value) |
                Q(customer__agm__contains=search_value),
                Q(status="ORDER") | Q(status="INSTALLATION")).distinct()
        else:
            requirements = Requirement.objects.filter(
                (Q(customer__sales_person=request.user) |
                 Q(customer__sales_person=request.user) |
                 Q(customer__customer_name__contains=search_value) |
                 Q(customer__customer_address__contains=search_value) |
                 Q(customer__customer_email__contains=search_value) |
                 Q(customer__phone_number__contains=search_value) |
                 Q(customer__agm__contains=search_value) |
                 Q(installer=request.user)) & (Q(status="ORDER") | Q(status="INSTALLATION"))).distinct()

        # Set columns to display.
        # IMPORTANT: to set columns in dict "columns",
        # 'key' is the title of the column and 'value' is the field in requirement object,
        # e.g. to get the customer name, 'requirement' object has an attribute 'customer' and this has an attribute 'customer_name'
        # so to retrieve it you will use 'customer.customer_name'
        columns = {
            'Installation Date': 'installation_date',
            'AGM': 'customer.agm',
            'Customer Name': 'customer.customer_name',
            'Phone': 'customer.phone_number',
            'Address': 'customer.customer_address',

            'Customer Check': 'customer.customer_check',
            'Con/ap': 'application',
            'Install notes': 'installation_notes',
        }

        # Set template context
        #   requirements: Requirements data
        #   url_view: name of url to enter each customer form
        #   columns: colums definition
        #   colspan: number of columns of the table. used to display a 'No results' message when empty
        #   current_tab: name of the current tab to set active class
        context = {
            'requirements': requirements,
            'url_view': 'installation-view',
            'columns': columns,
            'colspan': len(columns) + 2,
            'installation_search_field_visible': True,
            'search_value': search_value,
            'current_tab': 'installation-tab'
        }

        # Return requirement list in ORDER and INSTALLATION status
        return render(request, 'customer/requirement-list.html', context=context)


@login_required
@permission_required(['customer.installation_view'])
def installation_view(request, pk):
    """Returns a customer form in ORDER and INSTALLATION status"""
    customer = Customer.objects.get(id=pk)
    requirement = Requirement.objects.filter(customer_id=customer.id).first()

    # Set context.
    # leads, sales_people, roof_types, storeys, electric_powers, payments, installers are default options loaded in Django admin
    # requirement, credit_card, files are loaded from current customer
    # suppliers is loaded from current requirement
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
        'installation_notes': True,
        'electric_power': True,
        'extra_amount': True,
        'total_price': True,
        'deposit_amount': True,
        'last_amount': True,
        'power_connection': True
    }
    installation_fields = {
        'installation_date': True,
        'installer': True,
        'installer_notes': True
    }
    supplier_fields = {
        'supplier_name': True,
        'supplier_invoice': False,
        'supplier_amount': False,
        'supplier_date_paid': False,
        'supplier_notes': False
    }
    required_fields = {
        'customer_fields': customer_fields,
        'system_fields': system_fields,
        'installation_fields': installation_fields,
        'supplier_fields': supplier_fields
    }
    context = {
        'current_tab': 'installation-tab',
        'leads': Lead.objects.all(),
        'sales_people': get_user_model().objects.filter(profile__title='salesman'),
        'roof_types': RoofType.objects.all(),
        'storeys': Storey.objects.all(),
        'electric_powers': ElectricPower.objects.all(),
        'installers': get_user_model().objects.filter(profile__title='installer'),
        'customer': customer,
        'requirement': Requirement.objects.filter(customer_id=customer.id).first(),
        'credit_card': CreditCard.objects.filter(customer_id=customer.id).first(),
        'files': File.objects.filter(customer_id=customer.id),
        'suppliers': Supplier.objects.filter(requirement_id=requirement.id),
        'payments': Payment.objects.all(),
        'required_fields': required_fields,
        'options': {
            'user_created_enabled': True,
            'customer_data_enabled': True,
            'requirement_data_enabled': True,
            'service_data_enabled': False,
            'follow_up': False,
            'file_upload_enabled': True,
            'file_list_enabled': True,
            'installation_data_enabled': True,
            'customer_check_enabled': True,
            'deposit_info_enabled': True,
            'installer_payment_data_enabled': True,
            'supplier_list_enabled': True,
            'Finance': True,
            'buttons': [
                {
                    'btn_promote_name': 'btn_finish_installation',
                    'btn_promote_text': 'Finish Installation'
                }
            ]
        }
    }

    # Return customer form for ORDER and INSTALLATION status
    return render(request, 'customer/customer-full-form.html', context=context)


@login_required
@permission_required(['customer.reports_view'])
def all_download(request):
    # Return download in reports and INSTALLATION status
    return render(request, 'customer/download.html')

@login_required
@permission_required(['customer.reports_view'])
def export_xls(request):

    # Initialize for excel export.
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="reports.xls"'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Reports', cell_overwrite_ok=True)
    
    if request.method == 'POST':
        # Get all requirements in ONFILE and INSTALLATION status
        if request.user.has_perm('customer.customer_view_others'):
            onfilelist = Requirement.objects.filter(
                status="ON_FILE").distinct().order_by('customer__date_signed')
        else:
            onfilelist = Requirement.objects.filter(Q(customer__sales_person=request.user) | Q(
                installer=request.user), status="ON_FILE").distinct().order_by('customer__date_signed')
        # Get all requirements in ORDER and INSTALLATION status
        if request.user.has_perm('customer.customer_view_others'):
            orderlist = Requirement.objects.filter(
                status="ORDER").distinct().order_by('installation_date')
        else:
            orderlist = Requirement.objects.filter(Q(customer__sales_person=request.user) | Q(
                installer=request.user), status="ORDER").distinct().order_by('installation_date')
        
        # Get all list in order status
        order = {}
        for requirement in orderlist:
            suppliers = Supplier.objects.filter(requirement_id=requirement.id)
            amount = 0
            supplier_exisits = False
            Amount_exists = False
            for supplier in suppliers:
                supplier_exisits = True
                if supplier.supplier_date_paid is None:
                    try:
                        amount += supplier.supplier_amount
                        Amount_exists = True

                    except TypeError:
                        pass
                else:
                    Amount_exists = True

            if supplier_exisits == False:
                order[requirement.id] = '_'
            elif Amount_exists == False:
                order[requirement.id] = '_'
            elif amount == 0 and supplier_exisits:
                order[requirement.id] = 'Paid'
            else:
                order[requirement.id] = '$ ' + str(amount)
        
        # Get all requirements in ORDER and INSTALLATION status
        if request.user.has_perm('customer.customer_view_others'):
            installerlist = Requirement.objects.filter(
                Q(status="ORDER") | Q(status="INSTALLATION")).distinct().order_by('installation_date') # order by oldest
        else:
            requirements = Requirement.objects.filter((Q(customer__sales_person=request.user) | Q(
                installerlist=request.user)) & (Q(status="ORDER") | Q(status="INSTALLATION"))).distinct().order_by('installation_date') # order by latest
        
        # Get all list in order status
        order_install = {}
        for requirement in installerlist:
            suppliers = Supplier.objects.filter(requirement_id=requirement.id)
            amount = 0
            supplier_exisits = False
            Amount_exists = False
            for supplier in suppliers:
                supplier_exisits = True
                if supplier.supplier_date_paid is None:
                    try:
                        amount += supplier.supplier_amount
                        Amount_exists = True

                    except TypeError:
                        pass
                else:
                    Amount_exists = True

            if supplier_exisits == False:
                order_install[requirement.id] = '_'
            elif  Amount_exists == False:
                order_install[requirement.id] = '_'
            elif amount == 0 and supplier_exisits:
                order_install[requirement.id] = 'Paid'
            else:
                order_install[requirement.id] = '$ ' + str(amount)

        # Get all requirements in ACCOUNT and INSTALLATION status
        if request.user.has_perm('customer.customer_view_others'):
            acountlist = Requirement.objects.filter(Q(status="ACCOUNT")).distinct().order_by('installation_date')
        else:
            acountlist = Requirement.objects.filter((Q(customer__sales_person=request.user) |  Q(
                status="ACCOUNT"))).distinct().order_by('installation_date')
        
        # Get all in Supplier and SupplierMax status
        supplier = {}
        for requirement in acountlist:
            if requirement.last_amount_payment is not None:
                requirement.last_amount_balance_due = requirement.last_amount - requirement.last_amount_payment
                requirement.save()

            supplier[requirement.id] = Supplier.objects.filter(requirement_id=requirement.id)
        
        supplierMax = Supplier.objects.values('requirement').order_by().annotate(Count('requirement'))
        supplierMax = [x['requirement__count'] for x in supplierMax]
        supplierMax.append(0)
        supplierMax = max(supplierMax)

        
        # Set columns to display.
        # IMPORTANT: to set columns in dict "columns",
        # 'key' is the title of the column and 'value' is the field in requirement object,
        # e.g. to get the customer name, 'requirement' object has an attribute 'customer' and this has an attribute 'customer_name'
        # so to retrieve it you will use 'customer.customer_name'
        columns1 = {
            'Data signed': 'customer.date_signed',
            'Sales': 'customer.sales_person',
            'AGM': 'customer.agm',
            'Customer Name': 'customer.customer_name',
            'Phone': 'customer.phone_number',
            'Address': 'customer.customer_address',
            'Deposit': 'deposit_paid',
            'Finance': 'finance',
            'Customer Check': 'customer.customer_check',
            'Con/ap': 'application',
            'Install notes': 'installation_notes',
        }

        # Set columns to display.
        # IMPORTANT: to set columns in dict "columns",
        # 'key' is the title of the column and 'value' is the field in requirement object,
        # e.g. to get the customer name, 'requirement' object has an attribute 'customer' and this has an attribute 'customer_name'
        # so to retrieve it you will use 'customer.customer_name'
        columns2 = {
            'Installation Date': 'installation_date',
            'Sales': 'customer.sales_person',
            'AGM': 'customer.agm',
            'Customer Name': 'customer.customer_name',
            'Phone': 'customer.phone_number',
            'Address': 'customer.customer_address',
            'Order': 'Order',
            'Customer Check':'customer.customer_check',
            'Con/ap': 'application',
            'Install notes': 'installation_notes'
        }

        # Set columns to display.
        # IMPORTANT: to set columns in dict "columns",
        # 'key' is the title of the column and 'value' is the field in requirement object,
        # e.g. to get the customer name, 'requirement' object has an attribute 'customer' and this has an attribute 'customer_name'
        # so to retrieve it you will use 'customer.customer_name'
        columns3 = {
            'Installation Date': 'installation_date',
            'Installer': 'installer',
            'AGM': 'customer.agm',
            'Customer Name': 'customer.customer_name',
            'Phone': 'customer.phone_number',
            'Address': 'customer.customer_address',
            'Order': 'Order',
            'Customer Check': 'customer.customer_check',
            'Con/ap': 'application',
            'Install notes': 'installation_notes',

        }

        # Set columns to display.
        # IMPORTANT: to set columns in dict "columns",
        # 'key' is the title of the column and 'value' is the field in requirement object,
        # e.g. to get the customer name, 'requirement' object has an attribute 'customer' and this has an attribute 'customer_name'
        # so to retrieve it you will use 'customer.customer_name'
        columns4 = {
            'Installation Date': 'installation_date',
            'AGM': 'customer.agm',
            'Customer Name': 'customer.customer_name',
            'Phone': 'customer.phone_number',
            'STC/ap': 'stc_application',
            'Last amount': 'last_amount_balance_due',
            'STC': 'stc_amount_payment',
            'Installer': 'installer_amount',
            'Supplier': 'Supplier',
            'Payment notes': 'last_amount_notes'
        }

        col_num1 = 0
        col_num2 = 0
        col_num3 = 0
        col_num4 = 0

        # ONFILE LIST write to excel file.
        font_style = xlwt.XFStyle()
        font_style.font.bold = True
        ws.write(0, 0, "On File", font_style)
        for key,value in columns1.items():
            ws.write(2, col_num1, key, font_style)
            col_num1 += 1
        
        col_num1 = 0
        row_num = 3
        font_style = xlwt.XFStyle()            
        for row in onfilelist:
            for key,value in columns1.items():
                if value == 'customer.date_signed':
                    if row.customer.date_signed is None:
                        ws.write(row_num, col_num1, '-', font_style)
                    else:
                        ws.write(row_num, col_num1, str(row.customer.date_signed.strftime("%m/%d/%Y")), font_style)
                if value == 'customer.sales_person':
                    ws.write(row_num, col_num1, str(row.customer.sales_person), font_style)
                if value == 'customer.agm':
                    ws.write(row_num, col_num1, row.customer.agm, font_style)
                if value == 'customer.customer_name':
                    ws.write(row_num, col_num1, row.customer.customer_name, font_style)
                if value == 'customer.phone_number':
                    ws.write(row_num, col_num1, row.customer.phone_number, font_style)
                if value == 'customer.customer_address':
                    ws.write(row_num, col_num1, row.customer.customer_address, font_style)
                if value == 'deposit_paid':
                    ws.write(row_num, col_num1, row.deposit_paid, font_style)                                        
                if value == 'finance':
                    ws.write(row_num, col_num1, row.finance, font_style)
                if value == 'customer.customer_check':
                    cus_check = 'No'
                    if row.customer.customer_check == True:
                        cus_check = 'Yes'
                    ws.write(row_num, col_num1, cus_check, font_style)
                if value == 'application':
                    conap = 'No'
                    if row.application == True:
                        conap = 'Yes'
                    ws.write(row_num, col_num1, conap, font_style)
                if value == 'installation_notes':
                    ws.write(row_num, col_num1, row.installation_notes, font_style)
                col_num1 += 1
            row_num += 1
            col_num1 = 0
            
        
        # ORDER LIST write to excel file.
        font_style = xlwt.XFStyle()
        font_style.font.bold = True
        ws.write(row_num + 2, col_num2, "Order", font_style)
        for key,value in columns2.items():
            ws.write(row_num + 4, col_num2, key, font_style)
            col_num2 += 1

        col_num2 = 0
        row_num = row_num + 5
        font_style = xlwt.XFStyle()
        
        for row in orderlist:
            for key,value in columns2.items():
                if value == 'installation_date':
                    if value == 'installation_date':
                        if row.installation_date is None:
                            ws.write(row_num, col_num2, '-', font_style)
                        else:
                            ws.write(row_num, col_num2, str(row.installation_date.strftime("%m/%d/%Y")), font_style)
                if value == 'customer.sales_person':
                    ws.write(row_num, col_num2, str(row.customer.sales_person), font_style)
                if value == 'customer.agm':
                    ws.write(row_num, col_num2, row.customer.agm, font_style)
                if value == 'customer.customer_name':
                    ws.write(row_num, col_num2, row.customer.customer_name, font_style)
                if value == 'customer.phone_number':
                    ws.write(row_num, col_num2, row.customer.phone_number, font_style)
                if value == 'customer.customer_address':
                    ws.write(row_num, col_num2, row.customer.customer_address, font_style)
                if value == 'Order':
                    ws.write(row_num, col_num2, order[row.id], font_style)
                if value == 'customer.customer_check':
                    cus_check = 'No'
                    if row.customer.customer_check == True:
                        cus_check = 'Yes'
                    ws.write(row_num, col_num2, str(cus_check), font_style)
                if value == 'application':
                    conap = 'No'
                    if row.application == True:
                        conap = 'Yes'
                    ws.write(row_num, col_num2, str(conap), font_style)
                if value == 'installation_notes':
                    ws.write(row_num, col_num2, str(row.installation_notes), font_style)
                col_num2 += 1
            row_num += 1
            col_num2 = 0

        # Installation LIST write to excel file.
        font_style = xlwt.XFStyle()
        font_style.font.bold = True
        ws.write(row_num + 2, col_num3, "Installation", font_style)
        for key,value in columns3.items():
            ws.write(row_num + 4, col_num3, key, font_style)
            col_num3 += 1
        
        row_num = row_num + 5
        col_num3 = 0
        font_style = xlwt.XFStyle()
        for row in installerlist:
            for key,value in columns3.items():
                if value == 'installation_date':
                    if value == 'installation_date':
                        if row.installation_date is None:
                            ws.write(row_num, col_num3, '-', font_style)
                        else:
                            ws.write(row_num, col_num3, str(row.installation_date.strftime("%m/%d/%Y")), font_style)
                if value == 'installer':
                    ws.write(row_num, col_num3, str(row.installer), font_style)
                if value == 'customer.agm':
                    ws.write(row_num, col_num3, row.customer.agm, font_style)
                if value == 'customer.customer_name':
                    ws.write(row_num, col_num3, row.customer.customer_name, font_style)
                if value == 'customer.phone_number':
                    ws.write(row_num, col_num3, row.customer.phone_number, font_style)
                if value == 'customer.customer_address':
                    ws.write(row_num, col_num3, row.customer.customer_address, font_style)
                if value == 'Order':
                    ws.write(row_num, col_num3, order_install[row.id], font_style)
                if value == 'customer.customer_check':
                    cus_check = 'No'
                    if row.customer.customer_check == True:
                        cus_check = 'Yes'
                    ws.write(row_num, col_num3, str(cus_check), font_style)
                if value == 'application':
                    conap = 'No'
                    if row.application == True:
                        conap = 'Yes'
                    ws.write(row_num, col_num3, str(conap), font_style)
                if value == 'installation_notes':
                    ws.write(row_num, col_num3, str(row.installation_notes), font_style)
                col_num3 += 1
            row_num += 1
            col_num3 = 0

        # Account LIST write to excel file.            
        font_style = xlwt.XFStyle()
        font_style.font.bold = True
        ws.write(row_num + 2, col_num4, "Account", font_style)
        supplierCnt = 0
        for key,value in columns4.items():
            if key == 'Supplier':
                for x in range(0, supplierMax):
                    ws.write(row_num + 4, col_num4, key + str(x+1), font_style)
                    supplierCnt += 1
                    col_num4 += 1
            else:
                ws.write(row_num + 4, col_num4, key, font_style)
                col_num4 += 1
        
        col_num4 = -1
        row_num = row_num + 5
        font_style = xlwt.XFStyle()
        for row in acountlist:
            col_num4 = -1
            for key,value in columns4.items():
                col_num4 += 1
                if value == 'installation_date':
                    if row.installation_date is None:
                        ws.write(row_num, col_num4, '-', font_style)
                    else:
                        ws.write(row_num, col_num4, str(row.installation_date.strftime("%m/%d/%Y")), font_style)
                if value == 'customer.agm':
                    ws.write(row_num, col_num4, row.customer.agm, font_style)
                if value == 'customer.customer_name':
                    ws.write(row_num, col_num4, row.customer.customer_name, font_style)
                if value == 'customer.phone_number':
                    ws.write(row_num, col_num4, row.customer.phone_number, font_style)
                if value == 'stc_application':
                    stc_app = 'No'
                    if row.stc_application:
                        stc_app = 'YES'
                    ws.write(row_num, col_num4, stc_app, font_style)
                if value == 'last_amount_balance_due':
                    if row.last_amount_balance_due == None:
                        row.last_amount_balance_due = '0.00'
                    ws.write(row_num, col_num4, '$ ' + str(row.last_amount_balance_due), font_style)
                if value == 'stc_amount_payment':
                    if row.stc_amount_payment == '':
                        row.stc_amount_payment = '0.00'
                    ws.write(row_num, col_num4, '$ ' + str(row.stc_amount_payment), font_style)
                if value == 'installer_amount':
                    if row.installer_amount == None:
                        ws.write(row_num, col_num4, '$ 0.0', font_style)
                    elif row.installer_date_paid is not None:
                        row.installer_amount = 'Paid'
                        ws.write(row_num, col_num4, row.installer_amount, font_style)
                    else:
                        ws.write(row_num, col_num4, '$ ' + str(row.installer_amount), font_style)
                if value == 'Supplier':
                    supplierFor = supplier[row.id]
                    for val in supplierFor:
                        if val.supplier_date_paid is None and  val.supplier_amount is not None:
                            ws.write(row_num, col_num4, '$ ' + str(round(val.supplier_amount, 2)), font_style)
                        elif val.supplier_amount is None:  
                            ws.write(row_num, col_num4, '-', font_style)
                        else:
                            ws.write(row_num, col_num4, 'Paid', font_style)
                        col_num4 += 1
                if value == 'last_amount_notes':
                    if row.last_amount_notes is None:
                        row.last_amount_notes = '-'
                    ws.write(row_num, 8 + supplierCnt, str(row.last_amount_notes), font_style)
            row_num += 1
        wb.save(response)
        return response


@login_required
def global_search(request):
    if request.method == 'POST':

        # get Search Key data from search form
        search_value = request.POST.get('search_value')
        current_tab = request.POST.get('current_tab')
        tab = current_tab.split('-')[0]
        print("========================")

        if request.user.has_perm('customer.customer_view_others'):
            requirements = Requirement.objects.filter(
                Q(customer__customer_name__contains=search_value) |
                Q(customer__customer_address__contains=search_value) |
                Q(customer__customer_email__contains=search_value) |
                Q(customer__phone_number__contains=search_value) |
                Q(customer__agm__contains=search_value),
                ).distinct()
        else:
            requirements = Requirement.objects.filter(
                Q(customer__customer_name=search_value) |
                Q(customer__customer_address=search_value) |
                Q(customer__customer_email=search_value) |
                Q(customer__phone_number=search_value) |
                Q(customer__agm=search_value),
                Q(customer__sales_person=request.user)).distinct()

        # Set columns to display.
        # IMPORTANT: to set columns in dict "columns",
        # 'key' is the title of the column and 'value' is the field in requirement object,
        # e.g. to get the customer name, 'requirement' object has an attribute 'customer' and this has an attribute 'customer_name'
        # so to retrieve it you will use 'customer.customer_name'
        columns = {
            'Created Date': 'customer.created_date',
            'Sales': 'customer.sales_person',
            'AGM': 'customer.agm',

            'Customer Name': 'customer.customer_name',
            'Phone': 'customer.phone_number',
            'Address': 'customer.customer_address',
            'Email': 'customer.customer_email',
            'Status' : 'status'
        }

        # Set template context
        #   requirements: Requirements data
        #   url_view: name of url to enter each customer form
        #   columns: colums definition
        #   colspan: number of columns of the table. used to display a 'No results' message when empty
        #   current_tab: name of the current tab to set active class
        #   summary_enabled: show summary charts at the top of the view
        #   summary: Contains all aggregated results from models
        context = {
            'requirements': requirements,
            'url_view': 'finished-view',
            'columns': columns,
            'colspan': len(columns) + 2,
            f'{tab}_search_field_visible': True,
            'search_value': search_value,
            'current_tab': f'{current_tab}',
            'summary_enabled': False
        }
        return render(request, 'customer/requirement-list.html', context=context)


@login_required
@permission_required(['customer.account_list'])
def account_list(request):
    """Returns List of customers in ORDER, INSTALLATION and ACCOUNT"""
    if request.method == 'GET':
        # Get all requirements in ORDER, INSTALLATION and ACCOUNT status
        if request.user.has_perm('customer.customer_view_others'):
            requirements = Requirement.objects.filter(Q(status="ACCOUNT")).distinct().order_by('installation_date')
        else:
            requirements = Requirement.objects.filter((Q(customer__sales_person=request.user) |  Q(
                status="ACCOUNT"))).distinct().order_by('installation_date')

        supplier = {}
        for requirement in requirements:
            if requirement.last_amount_payment is not None:
                requirement.last_amount_balance_due = requirement.last_amount - requirement.last_amount_payment
                requirement.save()

            supplier[requirement.id] = Supplier.objects.filter(requirement_id=requirement.id)

        supplierMax = Supplier.objects.values('requirement').order_by().annotate(Count('requirement'))
        supplierMax = [x['requirement__count'] for x in supplierMax]
        supplierMax.append(0)
        supplierMax = max(supplierMax)

        # Set coagmlumns to display.
        # IMPORTANT: to set columns in dict "columns",
        # 'key' is the title of the column and 'value' is the field in requirement object,
        # e.g. to get the customer name, 'requirement' object has an attribute 'customer' and this has an attribute 'customer_name'
        # so to retrieve it you will use 'customer.customer_name'
        columns = {

            'Installation Date': 'installation_date',
            'AGM': 'customer.agm',
            'Customer Name': 'customer.customer_name',
            'Phone': 'customer.phone_number',
            'STC/ap': 'stc_application',
            'Last amount': 'last_amount_balance_due',
            'STC': 'stc_amount_payment',
            'Installer': 'installer_amount',
            'Supplier': 'Supplier',
            'Payment notes': 'last_amount_notes'

        }
        
        # Set template context
        #   requirements: Requirements data
        #   url_view: name of url to enter each customer form
        #   columns: colums definition
        #   colspan: number of columns of the table. used to display a 'No results' message when empty
        #   current_tab: name of the current tab to set active class
        #   summary_enabled: show summary charts at the top of the view
        #   summary: Contains all aggregated results from models
        total_stc = 0
        total_last_amount = 0
        for x in requirements:
            try:
                total_stc += float(x.stc_amount_payment)
            except TypeError:
                pass
            try:
                total_last_amount += float(x.last_amount_balance_due)
            except TypeError:
                pass
        context = {
            'requirements': requirements,
            'url_view': 'account-view',
            'columns': columns,
            'colspan': len(columns) + 2,
            'current_tab': 'account-tab',
            'summary_enabled': True,
            'suppliers': supplier,
            'MaxSuppliers': supplier,
            'supplierFlag': True,
            'supplierMax': supplierMax,
            'account_search_field_visible':True,
            'installer_flag':True,
            'summary': {
                'total_bank': AppData.objects.get(name='total_bank').value if AppData.objects.filter(
                    name='total_bank').exists() else 0,

                # i thinks this code are wrong
                **requirements.aggregate(total_stc=Sum('stc_amount'), total_last_amount=Sum('last_amount'),
                                         total_installers=Sum('installer_amount',filter=Q(installer_date_paid=None))),
                'total_suppliers': sum(filter(None, [
                    req.supplier_set.aggregate(total_suppliers=Sum('supplier_amount',filter=Q(supplier_date_paid=None))).get('total_suppliers') for req in
                    requirements])),
                'total_stc': total_stc,
                'total_last_amount': total_last_amount
            }
        }

        # Return requirement list in ORDER, INSTALLATION and ACCOUNT status
        return render(request, 'customer/requirement-list.html', context=context)


@login_required
def account_search(request):
    """Returns List of customers in ORDER, INSTALLATION and ACCOUNT"""
    if request.method == 'POST':
        # get Search Key data from search form
        search_value = request.POST.get('search_value')
        print("========================")

        # Get all requirements in ORDER, INSTALLATION and ACCOUNT status
        if request.user.has_perm('customer.customer_view_others'):
            requirements = Requirement.objects.filter(
                Q(customer__customer_name__contains=search_value) |
                Q(customer__customer_address__contains=search_value) |
                Q(customer__customer_email__contains=search_value) |
                Q(customer__phone_number__contains=search_value) |
                Q(customer__agm__contains=search_value),
                Q(status="ORDER") | Q(
                    status="INSTALLATION") | Q(status="ACCOUNT")).distinct()
        else:
            requirements = Requirement.objects.filter(
                Q(customer__sales_person=request.user) |
                Q(customer__customer_name__contains=search_value) |
                Q(customer__customer_address__contains=search_value) |
                Q(customer__customer_email__contains=search_value) |
                Q(customer__phone_number__contains=search_value) |
                Q(customer__agm__contains=search_value),
                (Q(customer__sales_person__contains=request.user) | Q(
                    installer=request.user)) & (Q(status="ORDER") | Q(status="INSTALLATION") | Q(
                    status="ACCOUNT"))).distinct()

        # Set columns to display.
        # IMPORTANT: to set columns in dict "columns",
        # 'key' is the title of the column and 'value' is the field in requirement object,
        # e.g. to get the customer name, 'requirement' object has an attribute 'customer' and this has an attribute 'customer_name'
        # so to retrieve it you will use 'customer.customer_name'
        columns = {

            'Installation Date': 'installation_date',
            'AGM': 'customer.agm',
            'Customer Name': 'customer.customer_name',
            'Phone': 'customer.phone_number',
            'STC/ap': 'stc_application',
            'Last amount': 'last_amount_balance_due',
            'STC': 'balance_due',
            'Installer': 'installer_amount',
            'Payment notes': 'last_amount_notes'

        }

        # Set template context
        #   requirements: Requirements data
        #   url_view: name of url to enter each customer form
        #   columns: colums definition
        #   colspan: number of columns of the table. used to display a 'No results' message when empty
        #   current_tab: name of the current tab to set active class
        #   summary_enabled: show summary charts at the top of the view
        #   summary: Contains all aggregated results from models
        context = {
            'requirements': requirements,
            'url_view': 'account-view',
            'columns': columns,
            'colspan': len(columns) + 2,
            'current_tab': 'account-tab',
            'summary_enabled': True,
            'account_search_field_visible': True,
            'search_value': search_value,
            'summary': {
                'total_bank': AppData.objects.get(name='total_bank').value if AppData.objects.filter(
                    name='total_bank').exists() else 0,
                **requirements.aggregate(total_stc=Sum('stc_amount'), total_last_amount=Sum('last_amount'),
                                         total_installers=Sum('installer_amount')),
                'total_suppliers': sum(filter(None, [
                    req.supplier_set.aggregate(total_suppliers=Sum('supplier_amount')).get('total_suppliers') for req in
                    requirements]))
            }
        }

        # Return requirement list in ORDER, INSTALLATION and ACCOUNT status
        return render(request, 'customer/requirement-list.html', context=context)


@login_required
@permission_required(['customer.account_view'])
def account_view(request, pk):
    """Returns a customer form in ORDER, INSTALLATION and ACCOUNT status"""
    customer = Customer.objects.get(id=pk)
    requirement = Requirement.objects.filter(customer_id=customer.id).first()

    # Set context.
    # leads, sales_people, roof_types, storeys, electric_powers, payments, installers are default options loaded in Django admin
    # requirement, credit_card, files are loaded from current customer
    # suppliers is loaded from current requirement
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
        'installation_notes': True,
        'electric_power': True,
        'extra_amount': True,
        'total_price': True,
        'deposit_amount': True,
        'last_amount': True,
        'power_connection': True
    }
    installation_fields = {
        'installation_date': True,
        'installer': True,
        'installer_notes': True,
        'installation_date': True,
        'installer_amount': True,
        'installer_date_paid': True
    }
    supplier_fields = {
        'supplier_name': True,
        'supplier_invoice': True,
        'supplier_amount': True,
        'supplier_date_paid': True,
        'supplier_notes': True
    }
    credit_fields = {
        'credit_card': True,
        'expires': True
    }
    deposit_fields = {
        'deposit_date_paid': True,
        'deposit_payment': True
    }
    required_fields = {
        'customer_fields': customer_fields,
        'system_fields': system_fields,
        'installation_fields': installation_fields,
        'supplier_fields': supplier_fields,
        'credit_fields': credit_fields,
        'deposit_fields': deposit_fields
    }
    context = {
        'current_tab': 'account-tab',
        'leads': Lead.objects.all(),
        'sales_people': get_user_model().objects.filter(profile__title='salesman'),
        'roof_types': RoofType.objects.all(),
        'storeys': Storey.objects.all(),
        'electric_powers': ElectricPower.objects.all(),
        'installers': get_user_model().objects.filter(profile__title='installer'),
        'customer': customer,
        'requirement': Requirement.objects.filter(customer_id=customer.id).first(),
        'credit_card': CreditCard.objects.filter(customer_id=customer.id).first(),
        'files': File.objects.filter(customer_id=customer.id),
        'suppliers': Supplier.objects.filter(requirement_id=requirement.id),
        'payments': Payment.objects.all(),
        'required_fields': required_fields,
        'options': {
            'user_created_enabled': True,
            'customer_data_enabled': True,
            'requirement_data_enabled': True,
            'service_data_enabled': False,
            'follow_up': False,
            'file_upload_enabled': True,
            'file_list_enabled': True,
            'installation_data_enabled': True,
            'customer_check_enabled': True,
            'deposit_info_enabled': True,
            'installer_payment_data_enabled': True,
            'supplier_list_enabled': True,
            'last_amount_data_enabled': True,
            'Finance': True,
            'buttons': [
                {
                    'btn_promote_name': 'btn_all_paid',
                    'btn_promote_text': 'All Paid'
                }
            ]
        }
    }

    # Return customer form for ORDER, INSTALLATION and ACCOUNT status
    return render(request, 'customer/customer-full-form.html', context=context)

@login_required
@permission_required(['customer.add_new_customer_via_account'])
def add_customer_via_account(request):
    '''Add new customer by getting all forms and redirect to Account '''
    if request.method == 'GET':
        upload_fields = {
                'upload': True
                }
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
            'installation_notes': True,
            'electric_power': True,
            'extra_amount': True,
            'total_price': True,
            'deposit_amount': True,
            'last_amount': True,
            'power_connection': True
        }
        installation_fields = {
            'installation_date': True,
            'installer': True,
            'installer_notes': True,
            'installation_date': True,
            'installer_amount': True,
            'installer_date_paid': True
        }
        supplier_fields = {
            'supplier_name': True,
            'supplier_invoice': True,
            'supplier_amount': True,
            'supplier_date_paid': True,
            'supplier_notes': True
        }
        credit_fields = {
            'credit_card': True,
            'expires': True
        }
        deposit_fields = {
            'deposit_date_paid': True,
            'deposit_payment': True
        }
        required_fields = {
            'customer_fields': customer_fields,
            'system_fields': system_fields,
            'installation_fields': installation_fields,
            'supplier_fields': supplier_fields,
            'credit_fields': credit_fields,
            'deposit_fields': deposit_fields,
            'upload_fields' : upload_fields

        }
        context = {
                'created_from_account' : True,
                'current_tab': 'account-tab',
                'leads': Lead.objects.all(),
                'sales_people': get_user_model().objects.filter(profile__title='salesman'),
                'roof_types': RoofType.objects.all(),
                'storeys': Storey.objects.all(),
                'electric_powers': ElectricPower.objects.all(),
                'installers': get_user_model().objects.filter(profile__title='installer'),
                'payments': Payment.objects.all(),
                'required_fields' : required_fields,
                'options': {
                    'customer_data_enabled': True,
                    'requirement_data_enabled': True,
                    'service_data_enabled': False,
                    'follow_up': True,
                    'file_upload_enabled': False,
                    'file_list_enabled': False,
                    'installation_data_enabled': True,
                    'customer_check_enabled': True,
                    'deposit_info_enabled': True,
                    'installer_payment_data_enabled': True,
                    'supplier_list_enabled': False,
                    'last_amount_data_enabled': True,
                    'Finance': True,

                    }
                }

        return render(request, 'customer/add_customer_via_account.html',context=context)

    elif request.method == 'POST':
        #checks if the customer name already exists
        customer_name = request.POST.get('customer_name')
        agm = request.POST.get('agm') if request.POST.get('agm') else None
        phone_number = request.POST.get('phone_number')
        try:
            customer = Customer.objects.get(customer_name=customer_name,agm=agm,phone_number=phone_number)

            messages.error(request,f'Customer {customer_name} already exists. Please enter new customer')
            return redirect('account-add-customer')
        except ObjectDoesNotExist:
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
                'customer_notes': request.POST.get('customer_notes') if request.POST.get('customer_notes') else None,
                'created_from_account' : True
            }


            kw = request.POST.get('kw') if request.POST.get(
                    'kw') else None
            panel = request.POST.get('panel') if request.POST.get(
                'panel') else None
            panel_pcs = request.POST.get('panel_pcs') if request.POST.get(
                'panel_pcs') else None
            inverter = request.POST.get('inverter') if request.POST.get(
                'inverter') else None
            inverter_pcs = request.POST.get('inverter_pcs') if request.POST.get(
                'inverter_pcs') else None
            roof_type_id = request.POST.get('roof_type') if request.POST.get(
                'roof_type') else None
            storey_id = request.POST.get('storey') if request.POST.get(
                'storey') else None
            electric_power_id = request.POST.get('electric_power') if request.POST.get(
                'electric_power') else None
            installation_notes = request.POST.get('installation_notes') if request.POST.get(
                'installation_notes') else None
            extra_amount = request.POST.get('extra_amount') if request.POST.get(
                'extra_amount') else None
            total_price = request.POST.get('total_price') if request.POST.get(
                'total_price') else None
            deposit_amount = request.POST.get('deposit_amount') if request.POST.get(
                'deposit_amount') else None
            last_amount = request.POST.get('last_amount') if request.POST.get(
                'last_amount') else None

            system_price = request.POST.get('system_price') if request.POST.get(
                'system_price') else None

            MNI = request.POST.get('MNI') if request.POST.get(
                'MNI') else None

            finance = request.POST.get('finance') if request.POST.get(
                'finance') else None

            Application = True if request.POST.get(
                'Application') else False

            installation_date = datetime.strptime(request.POST.get('installation_date'),
                                                              '%d/%m/%Y').strftime(
                '%Y-%m-%d') if request.POST.get(
                'installation_date') else None
            installer_id = request.POST.get('installer') if request.POST.get(
                'installer') else None

            installer_date_paid = datetime.strptime(request.POST.get('installer_date_paid'),
                                                                '%d/%m/%Y').strftime('%Y-%m-%d') if request.POST.get(
                'installer_date_paid') else None

            installer_amount = request.POST.get('installer_amount') if request.POST.get(
                'installer_amount') else None
            installer_notes = request.POST.get('installer_notes') if request.POST.get(
                'installer_notes') else None

            deposit_date_paid = datetime.strptime(request.POST.get('deposit_date_paid'),
                                                              '%d/%m/%Y').strftime('%Y-%m-%d') if request.POST.get(
                'deposit_date_paid') else None

            deposit_payment_id = request.POST.get('deposit_payment') if request.POST.get(
                'deposit_payment') else None

            unit = float(request.POST.get('Unit')) if request.POST.get(
                'Unit') else None

            unit_price = request.POST.get('unit_price') if request.POST.get(
                'unit_price') else None
            stc_application = True if request.POST.get(
                'Stc_Application') else False

            balance_due = datetime.strptime(request.POST.get('Balance_due'), '%d/%m/%Y').strftime(
                '%Y-%m-%d') if request.POST.get(
                'Balance_due') else None


            stc_notes = request.POST.get('stc_notes') if request.POST.get(
                'stc_notes') else None

            stc_amount = request.POST.get('Stc') if request.POST.get(
                'Stc') else None
            stc_date_paid = datetime.strptime(request.POST.get('stc_date_paid'), '%d/%m/%Y').strftime(
                '%Y-%m-%d') if request.POST.get(
                'stc_date_paid') else None
            STC_PAYMENT = request.POST.get('STC_PAYMENT') if request.POST.get(
                'STC_PAYMENT') else None
            last_amount_paid_date = datetime.strptime(request.POST.get('last_amount_paid_date'),
                                                                  '%d/%m/%Y').strftime(
                '%Y-%m-%d') if request.POST.get(
                'last_amount_paid_date') else None

            last_amount_payment = request.POST.get('last_amount_payment') if request.POST.get(
                'last_amount_payment') else None

            last_amount_balance_due = request.POST.get('last_amount_balance_due') if request.POST.get(
                'last_amount_balance_due') else None

            last_amount_payment_method_id = request.POST.get(
                'last_amount_payment_method') if request.POST.get(
                'deposit_payment') else None
            last_amount_notes = request.POST.get(
                'last_amount_notes') if request.POST.get(
                'last_amount_notes') else None

            power_connection = request.POST.get('power_connection') if request.POST.get(
                'power_connection') else None
            meter_connection = request.POST.get('meter_connection') if request.POST.get(
                'meter_connection') else None


            try:
                __stc = float(stc_amount)
            except TypeError:
                __stc = 0
            try:
                __stc_payment = float(STC_PAYMENT)
            except TypeError:
                __stc_payment = 0
            stc_amount_payment =  __stc - __stc_payment


            requirement_data = {
                'kw': kw,'panel' :panel,'panel_pcs' : panel_pcs,'inverter' : inverter,
                'inverter_pcs' : inverter_pcs,'roof_type_id' : roof_type_id,'storey_id':storey_id,
                'electric_power_id' : electric_power_id,'installation_notes':installation_notes,
                'extra_amount' : extra_amount,'total_price':total_price,'deposit_amount':deposit_amount,
                'last_amount':last_amount,'system_price':system_price,'MNI':MNI,'finance':finance,
                'application':Application,'installation_date': installation_date,'installer_id': installer_id,
                'installer_date_paid':installer_date_paid,'installer_amount':installer_amount,
                'Installer_notes':installer_notes,'deposit_date_paid':deposit_date_paid,'deposit_payment_id':deposit_payment_id,
                'unit':unit,'unit_price':unit_price,'stc_application':stc_application,'balance_due':balance_due,
                'stc_notes':stc_notes,'stc_date_paid':stc_date_paid,'stc_amount_payment':stc_amount_payment,
                'last_amount_paid_date':last_amount_paid_date,'last_amount_payment':last_amount_payment,
                'last_amount_balance_due':last_amount_balance_due,'last_amount_payment_method_id':last_amount_payment_method_id,
                'last_amount_notes':last_amount_notes,'power_connection':power_connection,'meter_connection':meter_connection
            }

            # Create new customer and store it in database
            customer = Customer(**customer_data)
            customer.save()

            status = 'ACCOUNT'

            # Create new requirement and credit card for the new customer
            requirement = Requirement(
                customer=customer, status=status, **requirement_data)
            requirement.save()

            credit_card = request.POST.get('credit_card') if request.POST.get(
                        'credit_card') else None
            expires = datetime.strptime(request.POST.get('expires'), '%m/%Y').strftime(
                        '%Y-%m-01') if request.POST.get('expires') else None

            credit_card_data = {
                    'credit_card':credit_card,
                    'expires' :expires
                    }
            credit_card = CreditCard(customer=customer,**credit_card_data)
            credit_card.save()

            if request.POST.get('service_note'):
                service_note = ServiceNote(
                    requirement=requirement, content=request.POST.get('service_note').strip())
                service_note.save()

            if 'btn_save' in request.POST:
                return HttpResponseRedirect('/account')




@login_required
@permission_required(['customer.service_list'])
def service_list(request):
    """Returns List of customers in SERVICE"""
    if request.method == 'GET':
        # Get all requirements in SERVICE status
        if request.user.has_perm('customer.customer_view_others'):
            requirements = Requirement.objects.filter(
                Q(status="SERVICE") | Q(status="SERVICE_HOME")).distinct().order_by('installation_date')
        else:
            requirements = Requirement.objects.filter(
                (Q(customer__sales_person=request.user) | Q(installer=request.user)) & (
                        Q(status="SERVICE") | Q(status="SERVICE_HOME"))).distinct().order_by('installation_date')

        # Set columns to display.
        # IMPORTANT: to set columns in dict "columns",
        # 'key' is the title of the column and 'value' is the field in requirement object,
        # e.g. to get the customer name, 'requirement' object has an attribute 'customer' and this has an attribute 'customer_name'
        # so to retrieve it you will use 'customer.customer_name'
        columns = {
            'Installation Date': 'installation_date',
            'Sales': 'customer.sales_person',
            'AGM': 'customer.agm',

            'Customer Name': 'customer.customer_name',
            'Phone': 'customer.phone_number',
            'Address': 'customer.customer_address',
            'Address': 'customer.customer_address',
            'SERIVCE notes': 'service_notes'
        }

        # Set template context
        #   requirements: Requirements data
        #   url_view: name of url to enter each customer form
        #   columns: colums definition
        #   colspan: number of columns of the table. used to display a 'No results' message when empty
        #   current_tab: name of the current tab to set active class
        #   summary_enabled: show summary charts at the top of the view
        #   summary: Contains all aggregated results from models
        context = {
            'requirements': requirements,
            'url_view': 'service-view',
            'columns': columns,
            'colspan': len(columns) + 2,
            'service_search_field_visible': True,
            'current_tab': 'service-tab',
            'summary_enabled': False
        }

        # Return requirement list in SERVICE status
        return render(request, 'customer/requirement-list.html', context=context)


@login_required
def service_search(request):
    """Returns List of customers in SERVICE"""
    if request.method == 'POST':
        # get Search Key data from search form
        search_value = request.POST.get('search_value')
        print("========================")

        # Get all requirements in SERVICE status
        if request.user.has_perm('customer.customer_view_others'):
            requirements = Requirement.objects.filter(
                Q(customer__customer_name__contains=search_value) |
                Q(customer__customer_address__contains=search_value) |
                Q(customer__customer_email__contains=search_value) |
                Q(customer__phone_number__contains=search_value) |
                Q(customer__agm__contains=search_value),
                Q(status="SERVICE") | Q(status="SERVICE_HOME")).distinct()
        else:
            requirements = Requirement.objects.filter(
                Q(customer__customer_name=search_value) |
                Q(customer__customer_address=search_value) |
                Q(customer__customer_email=search_value) |
                Q(customer__phone_number=search_value) |
                Q(customer__agm=search_value),
                (Q(customer__sales_person=request.user) | Q(installer=request.user)) & (
                        Q(status="SERVICE") | Q(status="SERVICE_HOME"))).distinct()

        # Set columns to display.
        # IMPORTANT: to set columns in dict "columns",
        # 'key' is the title of the column and 'value' is the field in requirement object,
        # e.g. to get the customer name, 'requirement' object has an attribute 'customer' and this has an attribute 'customer_name'
        # so to retrieve it you will use 'customer.customer_name'
        columns = {
            'Installation Date': 'installation_date',
            'Sales': 'customer.sales_person',
            'AGM': 'customer.agm',

            'Customer Name': 'customer.customer_name',
            'Phone': 'customer.phone_number',
            'Address': 'customer.customer_address',
            'Address': 'customer.customer_address',
            'SERIVCE notes': 'service_notes'
        }

        # Set template context
        #   requirements: Requirements data
        #   url_view: name of url to enter each customer form
        #   columns: colums definition
        #   colspan: number of columns of the table. used to display a 'No results' message when empty
        #   current_tab: name of the current tab to set active class
        #   summary_enabled: show summary charts at the top of the view
        #   summary: Contains all aggregated results from models
        context = {
            'requirements': requirements,
            'url_view': 'service-view',
            'columns': columns,
            'colspan': len(columns) + 2,
            'service_search_field_visible': True,
            'search_value': search_value,
            'current_tab': 'service-tab',
            'summary_enabled': False
        }

        # Return requirement list in SERVICE status
        return render(request, 'customer/requirement-list.html', context=context)


@login_required
@permission_required(['customer.service_view'])
def service_view(request, pk):
    """Returns a customer form in SERVICE status"""
    customer = Customer.objects.get(id=pk)
    requirement = Requirement.objects.filter(customer_id=customer.id).first()

    # Set context.
    # leads, sales_people, roof_types, storeys, electric_powers, payments, installers are default options loaded in Django admin
    # requirement, credit_card, files are loaded from current customer
    # suppliers is loaded from current requirement
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
    if requirement.status in ['SERVICE_HOME']:
        context = {
            'current_tab': 'service-tab',
            'installers': get_user_model().objects.filter(profile__title='installer'),
            'customer': customer,
            'requirement': Requirement.objects.filter(customer_id=customer.id).first(),
            'service_notes': ServiceNote.objects.filter(requirement_id=requirement.id),
            'options': {
                'customer_data_enabled': False,
                'requirement_data_enabled': False,
                'service_data_enabled': True,
                'follow_up': False,
                'file_upload_enabled': False,
                'file_list_enabled': False,
                'installation_data_enabled': False,
                'customer_check_enabled': False,
                'deposit_info_enabled': False,
                'installer_payment_data_enabled': False,
                'supplier_list_enabled': False,
                'last_amount_data_enabled': False,
                'service_notes_enabled': False,
                'service_note_disabled': True,
                'Finance': True,
                'buttons': [
                    {
                        'btn_promote_name': 'btn_delivered_home',
                        'btn_promote_text': 'Mark as delivered'
                    }
                ]
            }
        }
    elif requirement.status in ['SERVICE']:
        context = {
            'current_tab': 'service-tab',
            'leads': Lead.objects.all(),
            'sales_people': get_user_model().objects.filter(profile__title='salesman'),
            'roof_types': RoofType.objects.all(),
            'storeys': Storey.objects.all(),
            'electric_powers': ElectricPower.objects.all(),
            'installers': get_user_model().objects.filter(profile__title='installer'),
            'customer': customer,
            'requirement': Requirement.objects.filter(customer_id=customer.id).first(),
            'credit_card': CreditCard.objects.filter(customer_id=customer.id).first(),
            'files': File.objects.filter(customer_id=customer.id),
            'suppliers': Supplier.objects.filter(requirement_id=requirement.id),
            'payments': Payment.objects.all(),
            'service_notes': ServiceNote.objects.filter(requirement_id=requirement.id),
            'options': {
                'user_created_enabled': True,
                'customer_data_enabled': True,
                'requirement_data_enabled': True,
                'service_data_enabled': False,
                'follow_up': False,
                'file_upload_enabled': True,
                'file_list_enabled': True,
                'installation_data_enabled': True,
                'customer_check_enabled': True,
                'deposit_info_enabled': True,
                'installer_payment_data_enabled': True,
                'supplier_list_enabled': True,
                'last_amount_data_enabled': True,
                'service_notes_enabled': True,
                'buttons': [
                    {
                        'btn_promote_name': 'btn_delivered',
                        'btn_promote_text': 'Mark as delivered'
                    }
                ]
            }
        }

    # Return customer form for SERVICE status
    return render(request, 'customer/customer-full-form.html', context=context)


@login_required
@permission_required(['customer.finished_list'])
def finished_list(request):
    """Returns List of customers in FINISHED and SERVICE"""
    if request.method == 'GET':
        # Get all requirements in FINISHED and SERVICE status
        if request.user.has_perm('customer.customer_view_others'):
            requirements = Requirement.objects.filter(Q(status="FINISHED") | Q(
                status="DELIVERED") | Q(status="DELIVERED_HOME")).distinct()
        else:
            requirements = Requirement.objects.filter(Q(customer__sales_person=request.user) | Q(
                installer=request.user), Q(status="FINISHED") | Q(status="DELIVERED") | Q(
                status="DELIVERED_HOME")).distinct()

        # Set columns to display.
        # IMPORTANT: to set columns in dict "columns",
        # 'key' is the title of the column and 'value' is the field in requirement object,
        # e.g. to get the customer name, 'requirement' object has an attribute 'customer' and this has an attribute 'customer_name'
        # so to retrieve it you will use 'customer.customer_name'
        columns = {
            'Installation Date': 'installation_date',
            'Sales': 'customer.sales_person',
            'AGM': 'customer.agm',

            'Customer Name': 'customer.customer_name',
            'Phone': 'customer.phone_number',
            'Address': 'customer.customer_address',
            'Email': 'customer.customer_email',
            'Total amount': 'total_price',
            'KW': 'kw'

        }

        # Set template context
        #   requirements: Requirements data
        #   url_view: name of url to enter each customer form
        #   columns: colums definition
        #   colspan: number of columns of the table. used to display a 'No results' message when empty
        #   current_tab: name of the current tab to set active class
        #   summary_enabled: show summary charts at the top of the view
        #   summary: Contains all aggregated results from models
        context = {
            'requirements': requirements,
            'url_view': 'finished-view',
            'columns': columns,
            'colspan': len(columns) + 2,
            'finished_search_field_visible': True,
            'current_tab': 'finished-tab',
            'summary_enabled': False
        }

        # Return requirement list in FINISHED and SERVICE status
        return render(request, 'customer/requirement-list.html', context=context)


@login_required
def finished_search(request):
    """Returns List of customers in FINISHED and SERVICE"""
    if request.method == 'POST':

        # get Search Key data from search form
        search_value = request.POST.get('search_value')
        print("========================")

        # Get all requirements in FINISHED and SERVICE status
        if request.user.has_perm('customer.customer_view_others'):
            requirements = Requirement.objects.filter(
                Q(customer__customer_name__contains=search_value) |
                Q(customer__customer_address__contains=search_value) |
                Q(customer__customer_email__contains=search_value) |
                Q(customer__phone_number__contains=search_value) |
                Q(customer__agm__contains=search_value),
                Q(status="FINISHED") | Q(
                    status="DELIVERED") | Q(status="DELIVERED_HOME")).distinct()
        else:
            requirements = Requirement.objects.filter(
                Q(customer__customer_name=search_value) |
                Q(customer__customer_address=search_value) |
                Q(customer__customer_email=search_value) |
                Q(customer__phone_number=search_value) |
                Q(customer__agm=search_value),
                Q(customer__sales_person=request.user) | Q(
                    installer=request.user), Q(status="FINISHED") | Q(status="DELIVERED") | Q(
                    status="DELIVERED_HOME")).distinct()

        # Set columns to display.
        # IMPORTANT: to set columns in dict "columns",
        # 'key' is the title of the column and 'value' is the field in requirement object,
        # e.g. to get the customer name, 'requirement' object has an attribute 'customer' and this has an attribute 'customer_name'
        # so to retrieve it you will use 'customer.customer_name'
        columns = {
            'Installation Date': 'installation_date',
            'Sales': 'customer.sales_person',
            'AGM': 'customer.agm',

            'Customer Name': 'customer.customer_name',
            'Phone': 'customer.phone_number',
            'Address': 'customer.customer_address',
            'Email': 'customer.customer_email',
            'Total amount': 'total_price',
            'KW': 'kw'

        }

        # Set template context
        #   requirements: Requirements data
        #   url_view: name of url to enter each customer form
        #   columns: colums definition
        #   colspan: number of columns of the table. used to display a 'No results' message when empty
        #   current_tab: name of the current tab to set active class
        #   summary_enabled: show summary charts at the top of the view
        #   summary: Contains all aggregated results from models
        context = {
            'requirements': requirements,
            'url_view': 'finished-view',
            'columns': columns,
            'colspan': len(columns) + 2,
            'finished_search_field_visible': True,
            'search_value': search_value,
            'current_tab': 'finished-tab',
            'summary_enabled': False
        }

        # Return requirement list in FINISHED and SERVICE status
        return render(request, 'customer/requirement-list.html', context=context)


@login_required
@permission_required(['customer.finished_view'])
def finished_view(request, pk):
    """Returns a customer form in FINISHED and SERVICE status"""
    customer = Customer.objects.get(id=pk)
    requirement = Requirement.objects.filter(customer_id=customer.id).first()

    # Set context.
    # leads, sales_people, roof_types, storeys, electric_powers, payments, installers are default options loaded in Django admin
    # requirement, credit_card, files are loaded from current customer
    # suppliers is loaded from current requirement
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
    if requirement.status in ['DELIVERED_HOME']:
        context = {
            'current_tab': 'finished-tab',
            'installers': get_user_model().objects.filter(profile__title='installer'),
            'customer': customer,
            'requirement': Requirement.objects.filter(customer_id=customer.id).first(),
            'service_notes': ServiceNote.objects.filter(requirement_id=requirement.id),
            'options': {
                'customer_data_enabled': False,
                'requirement_data_enabled': False,
                'service_data_enabled': True,
                'follow_up': False,
                'file_upload_enabled': False,
                'file_list_enabled': False,
                'installation_data_enabled': False,
                'customer_check_enabled': False,
                'deposit_info_enabled': False,
                'installer_payment_data_enabled': False,
                'supplier_list_enabled': False,
                'last_amount_data_enabled': False,
                'service_notes_enabled': True,
                'Finance': True,
                'buttons': [
                    {
                        'btn_promote_name': 'btn_service_home',
                        'btn_promote_text': 'Service'
                    }
                ]
            }
        }
    elif requirement.status in ['FINISHED', 'DELIVERED']:
        context = {
            'current_tab': 'finished-tab',
            'leads': Lead.objects.all(),
            'sales_people': get_user_model().objects.filter(profile__title='salesman'),
            'roof_types': RoofType.objects.all(),
            'storeys': Storey.objects.all(),
            'electric_powers': ElectricPower.objects.all(),
            'installers': get_user_model().objects.filter(profile__title='installer'),
            'customer': customer,
            'requirement': Requirement.objects.filter(customer_id=customer.id).first(),
            'credit_card': CreditCard.objects.filter(customer_id=customer.id).first(),
            'files': File.objects.filter(customer_id=customer.id),
            'suppliers': Supplier.objects.filter(requirement_id=requirement.id),
            'payments': Payment.objects.all(),
            'service_notes': ServiceNote.objects.filter(requirement_id=requirement.id),
            'options': {
                'user_created_enabled': True,
                'customer_data_enabled': True,
                'requirement_data_enabled': True,
                'service_data_enabled': False,
                'follow_up': False,
                'file_upload_enabled': True,
                'file_list_enabled': True,
                'installation_data_enabled': True,
                'customer_check_enabled': True,
                'deposit_info_enabled': True,
                'installer_payment_data_enabled': True,
                'supplier_list_enabled': True,
                'last_amount_data_enabled': True,
                'service_notes_enabled': True,
                'buttons': [
                    {
                        'btn_promote_name': 'btn_service',
                        'btn_promote_text': 'Service'
                    }
                ]
            }
        }

    # Return customer form for FINISHED and SERVICE status
    return render(request, 'customer/customer-full-form.html', context=context)
