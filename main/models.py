# -*- coding: utf-8 -*-
from django.db import models
'''
class City(BaseModel):
    country = models.ForeignKey(Country, default = 0)
    name = models.CharField(max_length=64, verbose_name = u'adı')
    province_id = models.IntegerField(max_length = 4, default = 0, verbose_name = u'kodu')
    order_number = models.IntegerField(default=10)
    slug = models.SlugField()

    class Meta:
        verbose_name_plural = "Şehirler"
        verbose_name = "Şehir"
        ordering = ['order_number','name']

    def __unicode__(self):
        return "%s" % (self.name)

class Town(BaseModel):
    city = models.ForeignKey(City)
    name = models.CharField(max_length=50)
    slug = models.SlugField(blank=True,null=True)

    class Meta:
        unique_together = (('city','slug'),)
        verbose_name_plural = "İlçeler"
        verbose_name = "İlçe"
        ordering = ['name',]
    def __unicode__(self):
        return "%s" % self.name

class District(BaseModel):
    town = models.ForeignKey(Town)
    name = models.CharField(max_length=50)

    class Meta:
        ordering = ['name',]
        verbose_name_plural = "Mahalleler"
        verbose_name = "Mahalle"
    def __unicode__(self):
        return "%s" % self.name

'''
