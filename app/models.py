from django.db import models
from django.contrib.auth.models import AbstractUser

class Employee(AbstractUser):
	class Meta:
		permissions = (
		    ("can_drive", "Can drive"),
		    ("can_vote", "Can vote in elections"),
		    ("can_drink", "Can drink alcohol"),
		)
