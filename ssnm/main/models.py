'''Models for Ecouser and Ecomap.
Ecouser is an extension of the User Profile'''
from django.db import models
from django.contrib.auth.models import User


class EcomapManager(models.Manager):
    def create_ecomap(self, owner):
        ecomap = self.create(owner=owner)
        return ecomap


class Ecomap(models.Model):
    '''Store Ecomap and associated information'''
    name = models.CharField(max_length=50)
    ecomap_xml = models.TextField()
    owner = models.ForeignKey(User)
    description = models.TextField()
    objects = EcomapManager()
