from django.db import models
from django.contrib.auth.models import User

class Warehouse (models.Model):
    name = models.CharField(max_length = 100)
    address = models.CharField(max_length = 150)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='warehouses' )

    def __str__(self):
        return self.name


class Item (models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    quantity = models.PositiveIntegerField(default=0)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='items')

    def __str__(self):
        return self.name
    
