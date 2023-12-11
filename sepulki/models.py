import uuid

from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _


class SepulkaProperty(models.Model):
    name = models.CharField(
        _('name'),
        max_length=50,
        unique=True,
    )
    description = models.TextField(
        _('description'),
        max_length=250,
        blank=True,
        default='',
    )

    is_active = models.BooleanField(
        _('is active'),
        default=True,
        help_text=_(
            'If the property is inactive, then user can not to create '
            'sepulka with it.',
        ),
    )

    class Meta:
        abstract = True


class Color(SepulkaProperty):
    hex = models.CharField(
        _('hex code'),
        max_length=7,
        unique=True,
        validators=[
            RegexValidator(r'^#(?:[0-9a-fA-F]{3}){1,2}$'),
        ],
        help_text=_('Color hex code in #000 or #000000 formats.'),
    )

    class Meta:
        verbose_name = _('color')
        verbose_name_plural = _('color')

    def __str__(self) -> str:
        return f'{self.name} [{self.hex}]'


class Size(SepulkaProperty):
    volume = models.PositiveIntegerField(_('volume in m3 units'))

    class Meta:
        verbose_name = _('size')
        verbose_name_plural = _('sizes')

    def __str__(self) -> str:
        return f'{self.name} [{self.volume} m3]'


class Material(SepulkaProperty):
    density = models.PositiveIntegerField(_('density in kg/m3 units'))
    cost = models.PositiveIntegerField(_('cost in money/kg units'))

    class Meta:
        verbose_name = _('material')
        verbose_name_plural = _('materials')

    def __str__(self) -> str:
        return f'{self.name} [{self.density} kg/m3]'


class PreparedPropertiesSet(SepulkaProperty):
    color = models.ForeignKey(
        Color,
        on_delete=models.CASCADE,
        verbose_name=_('color'),
    )
    size = models.ForeignKey(
        Size,
        on_delete=models.CASCADE,
        verbose_name=_('size'),
    )
    material = models.ForeignKey(
        Material,
        on_delete=models.CASCADE,
        verbose_name=_('material'),
    )

    class Meta:
        verbose_name = _('prepared properties set')
        verbose_name_plural = _('prepared properties sets')

    def __str__(self) -> str:
        return self.name


class Order(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    client = models.ForeignKey(
        get_user_model(),
        on_delete=models.PROTECT,
        verbose_name=_('client'),
    )
    color = models.ForeignKey(
        Color,
        on_delete=models.PROTECT,
        verbose_name=_('color'),
    )
    size = models.ForeignKey(
        Size,
        on_delete=models.PROTECT,
        verbose_name=_('size'),
    )
    material = models.ForeignKey(
        Material,
        on_delete=models.PROTECT,
        verbose_name=_('material'),
    )

    class StatusChoice(models.TextChoices):
        PENDING = 'pending', _('pending manager decision')
        IN_PROCESS = 'in_process', _('in process by picker')
        IN_STOCK = 'in_stock', _('pending deliveryman')
        IN_DELIVERY = 'in_delivery', _('in delivery by deliveryman')
        DELIVERED = 'delivered', _('delivered to client')

    status = models.CharField(
        _('status'),
        max_length=15,
        choices=StatusChoice.choices,
        default=StatusChoice.PENDING,
    )

    is_rejected = models.BooleanField(
        _('is rejected'),
        default=False,
        help_text=_('The order can be rejected by the manager.'),
    )
    reject_message = models.TextField(
        _('reject message'),
        max_length=250,
        blank=True,
        default='',
        help_text=_(
            'Must be specified if the order is rejected by the manager.',
        ),
    )

    created = models.DateTimeField(_('created date'), auto_now_add=True)
    modified = models.DateTimeField(_('modified date'), auto_now=True)

    class Meta:
        verbose_name = _('order')
        verbose_name_plural = _('orders')

    @property
    def weight(self):
        return self.size.volume * self.material.density

    @property
    def total_cost(self):
        return self.weight * self.material.cost

    @property
    def is_returned(self):
        return bool(getattr(self, 'orderreturn', None))

    @property
    def can_be_returned(self):
        return (
            self.status == self.StatusChoice.DELIVERED
            and not self.is_rejected
        )


class OrderReturn(models.Model):
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        verbose_name=_('returned order'),
    )

    class SolutionChoice(models.TextChoices):
        MONEY = 'money', _('return money')
        ORDER = 'order', _('crete new order')

    solution = models.CharField(
        _('solution'),
        max_length=15,
        choices=SolutionChoice.choices,
        blank=True,
        default='',
        help_text=_(
            'Order returning solution, must be specified by the manager.',
        ),
    )

    new_order = models.OneToOneField(
        Order,
        on_delete=models.SET_NULL,
        verbose_name=_('new order for user'),
        related_name=_('returned_to_client'),
        null=True,
        default=None,
        help_text=_(
            'If the manager solution is `order`, then create new order, '
            'which will be send to the client.',
        ),
    )

    created = models.DateTimeField(_('created date'), auto_now_add=True)
    modified = models.DateTimeField(_('modified date'), auto_now=True)

    def clean(self) -> None:
        if self.order.status != Order.StatusChoice.DELIVERED:
            raise ValidationError(
                _('Only the delivered order can be returned.'),
            )

        if self.new_order and self.order == self.new_order:
            raise ValidationError(
                _('The returned order and new order can not be equal.'),
            )

        return super().clean()
