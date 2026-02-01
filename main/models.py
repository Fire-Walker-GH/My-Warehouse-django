from django.db import models
from django.contrib.auth.models import User

class Warehouse (models.Model):
    name = models.CharField(max_length = 100)
    address = models.CharField(max_length = 150)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='warehouses' )
    shared_users = models.ManyToManyField(User, through='WarehouseAccess', related_name='shared_warehouses')

    def __str__(self):
        return self.name


class WarehouseAccess(models.Model):
    ROLE_CHOICES = [
        ('viewer', 'Наблюдатель'),
        ('editor', 'Редактор'),
    ]
    
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='viewer')

    class Meta:
        unique_together = ('warehouse', 'user')

class Item (models.Model):
    name = models.CharField(max_length=70)
    description = models.TextField(max_length = 90)
    quantity = models.PositiveIntegerField(default=0)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='items')

    def __str__(self):
        return self.name
    
