from django.db import models
from django.utils.translation import gettext_lazy as _
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User

class Technician(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(_("Código"), max_length=2)
    document_id = models.IntegerField(_("Nro. De Cédula"))
    phone_1 = models.CharField(_("Teléfono 1"), max_length=20)
    phone_2 = models.CharField(_("Teléfono 2"), max_length=20, blank=True, null=True)
    address = models.CharField(_("Dirección"), max_length=200)
    rol = models.CharField(_("Rol"), max_length=50, blank=True, null=True)
    has_vehicle = models.BooleanField(_("¿Posee vehículo?"), default=False)
    vehicle_data = models.CharField(_("Datos del vehículo"), max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = _("technician")
        verbose_name_plural = _("technicians")
        permissions = ()

    def __str__(self):
        return "{} {}".format(self.user.first_name, self.user.last_name)


class Customer(models.Model):
    CUSTOMER_TYPE_CHOICES = [
        ('FR','Fibra Residencial'),
        ('FP','Fibra PYME'),
        ('OT','Otro'),
    ]

    CATEGORY_CHOICES = [
        ('INS','Instalación'),
        ('MIG','Migración'),
        ('MUD','Mudanza'),
        ('M&M','Migración y mudanza'),
        ('SER','Servicio'),
        ('OTR','Otro'),
    ]

    PLAN_CHOICES = [
        ('BA','Básico'),
        ('BP','Básico Plus'),
        ('BR','Bronce'),
        ('PL','Plata'),
        ('OR','Oro'),
        ('EM','Emprendedor'),
        ('PR','Productivo'),
        ('PP','Productivo Pro'),
        ('VP','Visionario Pro'),
        ('OT','Otro'),
    ]

    contract_number = models.IntegerField(_("Nro. De Contrato"), primary_key=True)
    customer_name = models.CharField(_("Nombre Cliente"), max_length=50)
    email = models.EmailField(_("Email"), max_length=254, blank=True, null=True)
    phone_1 = models.CharField(_("Teléfono 1"), max_length=20)
    phone_2 = models.CharField(_("Teléfono 2"), max_length=20, blank=True, null=True)
    address = models.CharField(_("Dirección"), max_length=300)
    customer_type = models.CharField(_("Tipo De Cliente"), max_length=2, choices=CUSTOMER_TYPE_CHOICES, default='FR')
    category = models.CharField(_("Categoría"), max_length=3, choices=CATEGORY_CHOICES, default='INS')
    plan = models.CharField(_("Plan"), max_length=2, choices=PLAN_CHOICES, default='BR')
    assigned_to = models.CharField(_("Asignado a"), max_length=100, blank=True, null=True)
    seller = models.CharField(_("Vendedor"), max_length=100, blank=True, null=True)
    comment = models.CharField(_("Observaciones"), max_length=300, blank=True, null=True)
    date_assigned = models.DateField(_("Fecha Recibida"), blank=True, null=True)
    date_created = models.DateTimeField(_("Fecha De Creación"), auto_now=False, auto_now_add=True)
    date_updated = models.DateTimeField(_("Última Modificación"), auto_now=True, auto_now_add=False)


    class Meta:
        verbose_name = _("customer")
        verbose_name_plural = _("customers")

    def __str__(self):
        return 'C{} - {}'.format(self.contract_number, self.customer_name)


class Order(models.Model):
    CUSTOMER_CONFIRMATION_CHOICES = [
        (0, 'Sin confirmar'),
        (1, 'En espera'),
        (2, 'Confirmada'),
    ]
    customer = models.ForeignKey(Customer, verbose_name=_("Cliente"), on_delete=models.CASCADE, related_name="orders", related_query_name='order')
    technician = models.ForeignKey(Technician, verbose_name=_("Técnico"), on_delete=models.CASCADE, blank=True, null=True, related_name="orders", related_query_name='order')
    completed = models.BooleanField(_("Completada"), default=False)
    extra_order_comment = models.CharField(_("Información extra"), max_length=200, blank=True, null=True)
    closed = models.BooleanField(_("Orden Cerrada"), default=False)
    customer_confirmation = models.IntegerField(_("Confirmación Cliente"), choices=CUSTOMER_CONFIRMATION_CHOICES, default=0)
    date_assigned = models.DateTimeField(_("Fecha a realizar"), blank=True, null=True)
    date_created = models.DateTimeField(_("Fecha De Creación"), auto_now=False, auto_now_add=True)
    date_updated = models.DateTimeField(_("Última Modificación"), auto_now=True, auto_now_add=False)

    class Meta:
        verbose_name = _("order")
        verbose_name_plural = _("orders")

    def __str__(self):
        return 'OR-{} | {}'.format(self.pk, self.customer)
    

class Installation(models.Model):
    order = models.OneToOneField(Order, verbose_name=_("Orden de instalación"), on_delete=models.CASCADE, blank=True, null=True)
    zone = models.IntegerField(_("Zona"), blank=True, null=True)
    olt = models.IntegerField(_("OLT"), blank=True, null=True)
    pon = models.IntegerField(_("PON"), blank=True, null=True)
    card = models.IntegerField(_("Tarjeta"), blank=True, null=True)
    box = models.IntegerField(_("Caja"), blank=True, null=True)
    port = models.IntegerField(_("Puerto"), blank=True, null=True)
    box_power = models.FloatField(_("Potencia Caja"), blank=True, null=True)
    house_power = models.FloatField(_("Potencia Roseta"), blank=True, null=True)
    onu_serial = models.CharField(_("Serial ONU"), max_length=32, blank=True, null=True)
    router_serial = models.CharField(_("Serial Router"), max_length=32, blank=True, null=True)
    drop_serial = models.IntegerField(_("Serial DROP"), blank=True, null=True)
    drop_used = models.IntegerField(_("DROP"), blank=True, null=True)
    hook_used = models.IntegerField(_("Tensores"), default=0, blank=True, null=True)
    fast_conn_used = models.IntegerField(_("Conectores"), default=2, blank=True, null=True)
    extra_comment = models.CharField(_("Información"), max_length=200, blank=True, null=True)

    class Meta:
        verbose_name = _("installation")
        verbose_name_plural = _("installations")

    def __str__(self):
        return 'INS-{}'.format(self.pk)


@receiver(post_save, sender=Customer)
def customer_post_save_receiver(sender, instance, **kwargs):
    if kwargs['created']: Order.objects.create(customer=instance)

@receiver(post_save, sender=Order)
def order_post_save_receiver(sender, instance, **kwargs):
    if kwargs['created']: Installation.objects.create(order=instance)
