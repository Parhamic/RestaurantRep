from django.db import models
from django.contrib.auth.models import AbstractUser

class Employee(AbstractUser):
	class Meta:
		permissions = (
		    ("can_add_order", "Can add order"),
		    ("can_see_orders", "Can see orders"),
		    ("can_change_salary", "Can change salary"),
		    ("can_see_activities", "Can see activities"),
		    ("can_change_materials", "Can change materials"),
		    ("can_add_payments", "Can add payments"),
		)

	jobTitle = models.CharField(max_length=64, default='مدیر')
	salary = models.IntegerField(default=0)
	workStart = models.TimeField(blank=True, null=True)
	workEnd = models.TimeField(blank=True, null=True)


class Activity(models.Model): # reports, logs
	title = models.CharField(max_length=128)
	description = models.CharField(max_length=2048)
	commitTime = models.DateTimeField(auto_now_add=True)

class Customer(models.Model):
	name = models.CharField(max_length=64)
	isVIP = models.BooleanField(default=False)

class Item(models.Model): # Food menu items
	name = models.CharField(max_length=64)
	price = models.IntegerField(default=0)

class Order(models.Model):
	orderer = models.ForeignKey(Customer, blank=True, null=True, on_delete=models.CASCADE)
	items = models.ManyToManyField(Item)
	orderTime = models.DateTimeField(auto_now_add=True)
	
	ORDER_STATES = (
        ('WT', 'Waiting'), # waiting for the chef to confirm
        ('CM', 'Confirmed'), # confirmed by the chef
        ('RD', 'Ready'), # ready
    )
	state = models.CharField(
		max_length=2,
		choices=ORDER_STATES,
		default='WT',
	)


class Supply(models.Model):
	name = models.CharField(max_length=64)
	available = models.BooleanField(default=False) # do we have this supply enough?
