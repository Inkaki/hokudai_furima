from django.db import models
from django.utils import timezone
from django.conf import settings
from django.db.models import F, Max, Q
from versatileimagefield.fields import PPOIField, VersatileImageField
import os
from versatileimagefield.placeholder import OnDiscPlaceholderImage
from django.core.exceptions import ValidationError
from enum import Enum

class AccessLevelChoice(Enum):   # A subclass of Enum
    public = "公開"
    private = "非公開"

def has_no_singlequote(value):
    if "\'" in value:
        raise ValidationError(
            '商品名にはシングルクオート（\'）を含めないでください。',
            params={'value': value},
        )

class Product(models.Model):
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='seller')
    title  = models.CharField('商品名', max_length=200, validators=[has_no_singlequote])
    description = models.TextField('説明文', max_length=2000)
    price = models.PositiveIntegerField('値段(円)', default=0)
    is_sold = models.BooleanField(default=False)
    created_date = models.DateTimeField(default=timezone.now)
    updated_date = models.DateTimeField(blank=True, null=True)
    sold_date = models.DateTimeField(blank=True, null=True)
    wanting_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='wanting_users')
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, related_name='buyer')
    access_level = models.CharField('公開/非公開',
        max_length=10,
        choices=[(level.name, level.value) for level in AccessLevelChoice],
        default='public'
    )
    watched_count = models.PositiveIntegerField(default=0)

    def update(self):
        self.updated_date = timezone.now()
        self.save()

    def __str__(self):
        return self.title

    def increment_watched_count(self):
        self.watched_count += 1
        self.update()


class ProductImage(models.Model):
    image = VersatileImageField(
        '',
        upload_to='product', 
        blank=True,
        null=True
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def update(self):
        self.save()

    @property
    def thumbnail_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.thumbnail['600x600'].url

    @property
    def thumbnail_100_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.thumbnail['100x100'].url
