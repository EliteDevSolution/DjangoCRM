from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.db import models

numeric = RegexValidator(r'^[0-9]*$', 'Only numeric characters are allowed.')


class Lead(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name if self.name else ''


USER_PROFILES = [
    ('user', 'User'),
    ('Installation', 'Installation'),
    ('installer', 'Installer'),
    ('salesman', 'Salesman'),
    ('account', 'Account'),
]


class Profile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    title = models.CharField(
        max_length=20, choices=USER_PROFILES, default=USER_PROFILES[0][0])

    def __str__(self):
        return self.title if self.title else ''


class Payment(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name if self.name else ''


class Customer(models.Model):
    creator = models.ForeignKey(get_user_model(
    ), on_delete=models.CASCADE, null=True, blank=True, related_name='customer_creator')
    created_date = models.DateTimeField(auto_now_add=True)
    leads_from = models.ForeignKey(
        Lead, on_delete=models.CASCADE, null=True, blank=True)
    sales_person = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, null=True, blank=True, related_name='customer_salesman')
    agm = models.CharField(max_length=50, blank=True, null=True)  # optional
    date_signed = models.DateField(blank=True, null=True)  # optional
    customer_name = models.CharField(max_length=50)
    customer_address = models.CharField(
        max_length=200, blank=True, null=True)  # optional
    customer_email = models.EmailField(
        max_length=200, blank=True, null=True)  # optional
    phone_number = models.CharField(max_length=20, blank=True,
                                    null=True, validators=[numeric])  # optional
    follow_up = models.CharField(
        max_length=100, blank=True, null=True)  # optional
    customer_notes = models.CharField(
        max_length=500, blank=True, null=True)  # optional

    customer_check = models.BooleanField(default=False)
    
    created_from_account = models.BooleanField(default=False) # for adding customer via account
    

    def __str__(self):
        return self.customer_name if self.customer_name else ''

    class Meta:
        ordering = ['-created_date']
        permissions = [
            ("customer_list", "Can view New Customer List page"),
            ("customer_view", "Can view New Customer details"),
            ("deposit_list", "Can view Deposit List page"),
            ("deposit_view", "Can view Deposit details"),
            ("on_file_list", "Can view On File List page"),
            ("on_file_view", "Can view On File details"),
            ("order_list", "Can view Order List page"),
            ("order_view", "Can view Order details"),
            ("installation_list", "Can view Installation List page"),
            ("installation_view", "Can view Installation details"),
            ("account_list", "Can view Account List page"),
            ("account_view", "Can view Account details"),
            ("service_list", "Can view Service List page"),
            ("service_view", "Can view Service details"),
            ("finished_list", "Can view Finished List page"),
            ("finished_view", "Can view Finished details"),
            ("customer_view_others", "Can view Customers of other users"),
            ("delete_customer_data", "Can delete Customer data"),
            ("add_new_customer_via_account","Add new customer via account"),
            ("sales_signed","See already signed customer"),
            ("view_reports", "Can view reports")
        ]


class Service(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    agm = models.IntegerField()
    customer_name = models.CharField(max_length=50)
    customer_address = models.CharField(max_length=200)
    customer_email = models.EmailField(max_length=200)
    customer_phone = models.CharField(max_length=20, validators=[numeric])
    installation_date = models.DateField()
    installer = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    notes = models.CharField(max_length=500)

    def __str__(self):
        return self.customer_name if self.customer_name else ''

# Models for new requirements


class RoofType(models.Model):
    # Model added for future customization
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name if self.name else ''


class Storey(models.Model):
    # Model added for future customization
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name if self.name else ''


class ElectricPower(models.Model):
    # Model added for future customization
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name if self.name else ''


class Requirement(models.Model):
    """
    Users create a customer and the information is stored in a database.
    """
    created_date = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    kw = models.CharField(max_length=50, null=True, blank=True)
    panel = models.CharField(max_length=50, null=True, blank=True)
    panel_pcs = models.IntegerField(null=True, blank=True)
    inverter = models.CharField(max_length=50, null=True, blank=True)
    inverter_pcs = models.IntegerField(null=True, blank=True)
    # linked as a foreign key for flexibility
    roof_type = models.ForeignKey(
        RoofType, on_delete=models.CASCADE, null=True, blank=True)
    # linked as a foreign key for flexibility
    storey = models.ForeignKey(
        Storey, on_delete=models.CASCADE, null=True, blank=True)
    # linked as a foreign key for flexibility
    electric_power = models.ForeignKey(
        ElectricPower, on_delete=models.CASCADE, null=True, blank=True)
    installation_notes = models.CharField(
        max_length=500, null=True, blank=True)

    finance = models.CharField(max_length=50,default='No',null=True, blank=True) # changed from Boolean to Charfield


    system_price = models.FloatField(null=True, blank=True,default=0.00)
    extra_amount = models.FloatField(null=True, blank=True,default=0.00)
    total_price = models.FloatField(null=True, blank=True,default=0.00)
    deposit_amount = models.FloatField(null=True, blank=True,default=0.00)
    last_amount = models.FloatField(null=True, blank=True,default=0.00)
    status = models.CharField(max_length=50, default='CREATED')

    deposit_date_paid = models.DateField(null=True, blank=True)
    deposit_payment = models.ForeignKey(
        Payment, on_delete=models.CASCADE, related_name='requirement_deposit_payment', null=True, blank=True)

    #this is the installation data
    installation_date = models.DateField(null=True, blank=True)
    installer = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, null=True, blank=True)
    installer_amount = models.FloatField(null=True, blank=True,default=0.00)
    installer_date_paid = models.DateField(null=True, blank=True)
    Installer_notes = models.CharField(max_length=500, null=True, blank=True,default="")

    order_paid = models.BooleanField(default=False)

    # This is the stc fields
    unit =  models.IntegerField(null=True, blank=True)
    unit_price = models.FloatField(null=True, blank=True,default=0.00)
    stc_application = models.BooleanField(default=False)
    balance_due =  models.DateField(null=True, blank=True)
    stc_amount_payment = models.FloatField(null=True, blank=True,default=0.00)
    stc_notes = models.CharField(max_length=500, null=True, blank=True)
    STC_PAYMENT = models.FloatField(null=True, blank=True,default=0.00)
    stc_amount = models.FloatField(null=True, blank=True,default=0.00)
    stc_date_paid = models.DateField(null=True, blank=True)

    pcs = models.IntegerField(null=True, blank=True)

    # This is the last amount fields
    last_amount_paid_date = models.DateField(null=True, blank=True)
    last_amount_payment = models.FloatField(null=True, blank=True,default=0.00)
    last_amount_payment_method = models.ForeignKey(
        Payment, on_delete=models.CASCADE, related_name='requirement_last_amount_payment', null=True, blank=True)
    last_amount_balance_due =  models.FloatField(null=True, blank=True,default=0.00)
    last_amount_notes = models.CharField(max_length=500, null=True, blank=True)

    power_connection = models.CharField(max_length=50, null=True, blank=True)
    meter_connection = models.CharField(max_length=50, null=True, blank=True)
    MNI = models.CharField(max_length=50, null=True, blank=True)
    application =  models.BooleanField(default=False)

    def __str__(self):
        return self.customer.customer_name if self.customer.customer_name else ''

    @property
    def supplier_status(self):
        """Summarizes suppliers information to display in account list view"""
        supplier_data = []
        for supplier in self.supplier_set.all():
            supplier_data.append('{}: {}'.format(supplier.supplier_name, 'Paid' if supplier.supplier_date_paid else '$ {}'.format(
                supplier.supplier_amount) if supplier.supplier_amount else '-'))
        return '\n'.join(supplier_data)

    @property
    def suppliers_paid(self):
        return all([True if supplier.supplier_date_paid else False for supplier in self.supplier_set.all()])

    @property
    def installation_paid(self):
        """Returns whether the installation has a pay date or not"""
        return 'Paid' if self.installer_date_paid else '$ {}'.format(self.installer_amount) if self.installer_amount else None

    @property
    def deposit_paid(self):
        return 'Paid' if self.deposit_date_paid else '$ {}'.format(self.deposit_amount) if self.deposit_amount else None

    @property
    def stc_paid(self):
        return 'Paid' if self.stc_date_paid else '$ {}'.format(self.stc_amount) if self.stc_amount else None

    @property
    def last_amount_paid(self):
        return 'Paid' if self.last_amount_paid_date else '$ {}'.format(self.last_amount) if self.last_amount else None

    class Meta:
        ordering = ['-customer__created_date']
    # content_type =   models.ForeignKey(ContentType, on_delete=models.CASCADE)
    # object_id = models.PositiveIntegerField()
    # content_object=GenericForeignKey('object_id')

    # customer = models.ForeignKey(newCustomer, on_delete=models.CASCADE, null=True)


class ServiceNote(models.Model):
    requirement = models.ForeignKey(Requirement, on_delete=models.CASCADE)
    content = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.content if self.content else ''


class CreditCard(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    credit_card = models.CharField(max_length=20, validators=[
                                   numeric], null=True, blank=True)
    expires = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.credit_card if self.credit_card else ''
    # customer = models.ForeignKey(newCustomer, on_delete=models.CASCADE, null=True)


class File(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    file_name = models.CharField(max_length=50, default='Unknown File')
    url = models.CharField(max_length=100)

    def __str__(self):
        return self.file_name if self.file_name else ''
    # customer = models.ForeignKey(newCustomer, on_delete=models.CASCADE, null=True)


class Supplier(models.Model):
    requirement = models.ForeignKey(Requirement, on_delete=models.CASCADE)
    supplier_name = models.CharField(max_length=50, null=True, blank=True)
    supplier_invoice = models.CharField(max_length=50, null=True, blank=True)
    supplier_amount = models.FloatField(null=True, blank=True,default=0.00)
    supplier_date_paid = models.DateField(null=True, blank=True)
    supplier_notes = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.supplier_name if self.supplier_name else ''


class AppData(models.Model):
    name = models.CharField(max_length=50)
    value = models.CharField(max_length=50)

    def __str__(self):
        return self.name if self.name else ''
