from django.db import models


class Item(models.Model):
    title = models.CharField(max_length=50, verbose_name='Наименование')
    price = models.DecimalField(max_digits=6, decimal_places=2, verbose_name='Стоимость')

    def __str__(self):
        return f"Item '{self.title}' for {self.price}"
