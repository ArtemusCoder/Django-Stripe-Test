from django.db import models


class Item(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price_id = models.CharField(max_length=255)
    price = models.FloatField()

    def __str__(self):
        return "ID: " + str(self.pk) + " - " + self.name


class Discount(models.Model):
    id_stripe = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    amount_of = models.FloatField(null=True, blank=True)
    percent_of = models.FloatField(null=True, blank=True)


class Tax(models.Model):
    id_stripe = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    inclusive = models.BooleanField()
    percentage = models.FloatField()


class Order(models.Model):
    name = models.CharField(max_length=255)
    items = models.ManyToManyField(Item)
    discount = models.ForeignKey(Discount, on_delete=models.SET_NULL, null=True, blank=True)
    tax = models.ForeignKey(Tax, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return "ID: " + str(self.pk) + " - " + self.name
