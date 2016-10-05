# -*- coding: utf-8 -*-

from datetime import datetime
from django.contrib.gis.geos import Point
from django.core.urlresolvers import reverse
from django.core.validators import MaxLengthValidator
from django.db import models
from django.db.models import Max, Min
from django.utils.translation import ugettext_lazy as _
import os,hashlib
from skp.core.models.constants import *
from skp.settings import SERVER_ROOT, MEDIA_URL, STATIC_URL
import random
from django.contrib.auth.models import User
from taggit.managers import TaggableManager

file_size = str(MAX_UPLOAD_SIZE/1024/1024)
help_text_fix = u"MAX DOSYA BOYUTU %s MB - RESMİN BOYUTLARI  %sx%s olmalıdır."
help_text_flexible = u"MAX DOSYA BOYUTU %s MB - GENİŞLİĞİ %s ile %s ,  YÜKSEKLİĞİ %s ile %s px arasında olmalıdır"

def get_upload_path(instance, filename):
    class_name = instance.__class__.__name__
    filename_splitted = filename.split('.')
    ext = filename_splitted[-1]
    date_fmt = '%Y/%m'

    if instance.id: #if already created
        date_path = instance.create_date.strftime(date_fmt)

    else: # not yet created
        date_path = datetime.today().strftime(date_fmt)

    if(News.__instancecheck__(instance) or NewsPhoto.__instancecheck__(instance)):
        if NewsPhoto.__instancecheck__(instance):
            if instance.id:
                date_fmt += '/%d'
                date_path = instance.create_date.strftime(date_fmt)
            else:
                date_path = datetime.today().strftime(date_fmt)
            path = 'photos/News/NewsPhoto/%s' %(date_path)
        else:
            if instance.id:
                date_fmt += '/%d'
                date_path = instance.create_date.strftime(date_fmt)
            else:
                date_path = datetime.today().strftime(date_fmt)
            path = 'photos/News/%s' %(date_path)

    elif not (Company.__instancecheck__(instance) or JointCompany.__instancecheck__(instance) or Gallery.__instancecheck__(instance)):
        extra_path = ''
        if HousePlanPhoto.__instancecheck__(instance):
            project = instance.house.project
            extra_path = '%s/HousePlanPhoto/' % instance.house.id
            class_name = 'HouseType'
        elif(Project.__instancecheck__(instance)):
            project = instance
            class_name= 'Self'
        else:
            project = instance.project
        date_path = project.create_date.strftime(date_fmt)
        project_id_hash = hashlib.sha1('%s' %project.id).hexdigest()[:16]
        path = 'photos/Project/%s/%s/%s/%s' %( date_path,project_id_hash,class_name,extra_path)
    else:
        path = 'photos/%s/%s' %( class_name,date_path)

    random_number = str(random.random())[2:]
    filename_hash = hashlib.sha1('%s' %random_number).hexdigest()[:16]
    filename = "%s.%s" % (filename_hash,ext.lower())
    return os.path.join(path,filename)

# Create your models here.
class BaseModel(models.Model):
    create_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(editable=False, default=False, verbose_name='Silindi')
    class Meta:
        abstract = True

class BaseWithStatus(BaseModel):
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=0, verbose_name= 'Durum')
    class Meta:
        abstract = True

class Country(BaseModel):
    name = models.CharField(max_length=64, verbose_name = u'adı')
    abbrevation = models.CharField(max_length=4, verbose_name = u'kodu')
    phone_code = models.CharField(max_length=8, verbose_name = u'telefon kodu')
    slug = models.SlugField()

    class Meta:
        verbose_name_plural = "Ülkeler"
        verbose_name = "Ülke"
        ordering = ['name']

    def __unicode__(self):
        return "%s" % (self.name)

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

class Company(BaseModel):
    name = models.CharField(max_length=150, verbose_name=u'firma adı')
    website = models.URLField(max_length=200, verify_exists=False, verbose_name=u'web sitesi')
    commercial_title = models.CharField(max_length=100, blank=True, null=True, verbose_name=u'ticari ünvanı')
    corparate_customer = models.ForeignKey(User, null=True, blank=True, verbose_name=u'emlak sorumlusu')
    email = models.EmailField(blank=True, null=True, verbose_name=u'email')
    phone = models.CharField(max_length=11, help_text='11 Haneli Telefon Numarası', blank=True, null=True, verbose_name=u'telefon')
    address = models.TextField(verbose_name=u'açık adres')
    city = models.ForeignKey(City, verbose_name=u'firmanın bulunduğu il')
    fax = models.CharField( max_length=11, help_text='11 Haneli Fax Numarası', blank=True, null=True, verbose_name=u'fax')
    logo = models.ImageField(upload_to=get_upload_path, blank=True, null=True,
        help_text=help_text_fix %(file_size, OPTIMUM_COMPANY_LOGO_WIDTH,  OPTIMUM_COMPANY_LOGO_HEIGHT))
    cover_photo = models.ImageField(upload_to=get_upload_path, blank=True, null=True, verbose_name=u'kapak fotoğrafı',
                                    help_text=help_text_fix%(file_size, OPTIMUM_COVER_WIDTH, OPTIMUM_COVER_HEIGHT ))
    banner = models.ImageField(upload_to=get_upload_path, blank=True, null=True)
    contact = models.CharField(max_length=500, blank=True, null=True, verbose_name=u'iletişim kurulacak kişi')
    description = models.TextField(blank=True, null=True, verbose_name=u'not')
    slug = models.SlugField(unique=True)
    def __unicode__(self):
        return "%s" % self.name

    class Meta:
        verbose_name_plural = "Firmalar"
        verbose_name = "Firma"
        ordering = ['name',]

    def project_count(self):
        return Project.objects.filter(company=self).count()
    project_count.short_description = 'Proje Sayısı'

    def check_commercial_site(self):
        active_site = self.commercialsite_set.all().filter(end_date__gte = datetime.now().date())
        if active_site.count() > 0:
            return True
        return False

    def has_commercial_site(self):
        if self.check_commercial_site() == True:
            return '<img src="/projeler/static/admin/img/admin/icon-yes.gif" alt="True" />'
        return '<img src="/projeler/static/admin/img/admin/icon-no.gif" alt="True" />'
    has_commercial_site.short_description = 'Kurumsal Site'
    has_commercial_site.allow_tags = True

    @models.permalink
    def get_absolute_url(self):
        return ('core.views.company', (), {'slug': self.slug})

class JointCompany(BaseModel):
    name = models.CharField('Firma Adı', max_length=150)
    companies = models.ManyToManyField(Company, verbose_name='Ortak Şirketler')
    logo = models.ImageField(upload_to=get_upload_path, blank=True, null=True,
        help_text=help_text_fix %(file_size, OPTIMUM_COMPANY_LOGO_WIDTH, OPTIMUM_COMPANY_LOGO_HEIGHT ), verbose_name='Ortaklı Firmanın Logosu')
    slug = models.SlugField(unique=True)
    def __unicode__(self):
        return "%s" % self.name
    class Meta:
        verbose_name_plural = "Ortaklı Firmalar"
        verbose_name = "Ortaklı Firma"
        ordering = ['name',]

    def project_count(self):
        return Project.objects.filter(joint_company=self).count()
    project_count.short_description = 'Proje Sayısı'

    def check_commercial_site(self):
        return False

class CommercialSite(models.Model):
    company = models.ForeignKey(Company)
    start_date = models.DateField('Başlangıç Tarihi', default=datetime.now().date())
    validity_as_months = models.PositiveSmallIntegerField('Geçerlilik Süresi', choices=VALIDITY_TYPE, default=6)
    end_date = models.DateField('Bitiş Tarihi')
    about = models.TextField('Hakkımızda', validators=[MaxLengthValidator(1000)])
    mission = models.TextField('Misyon', blank=True, null=True, validators=[MaxLengthValidator(1000)])
    vision = models.TextField('Vizyon', blank=True, null=True, validators=[MaxLengthValidator(1000)])
    class Meta:
        verbose_name_plural = "Kurumsal Siteler"
        verbose_name = "Kurumsal Site"
    def __unicode__(self):
        return "%s" % self.company.name

class FAQ(BaseModel):
    question = models.CharField('Soru', max_length=500)
    answer = models.TextField('Cevap')
    slug = models.SlugField(unique=True)
    def __unicode__(self):
        return "%s" % self.question
    class Meta:
        verbose_name_plural = "Püf Noktalar"
        verbose_name = "Püf Nokta"
    def answer_text(self):
        return self.answer
    answer_text.short_description = 'Cevap'
    answer_text.allow_tags = True

class SEO(BaseModel):
    keyword = models.CharField('Keyword', max_length=100)
    keyword_map_url = models.CharField('Keyword için Url', max_length=500)

    def __unicode__(self):
        return "%s" % self.keyword
    class Meta:
        verbose_name_plural = "SEO Keywordleri"
        verbose_name = "SEO Keyword"

class Author(BaseModel):
    name = models.CharField('Yazar Adı', max_length=50)
    email = models.EmailField('Yazar Mail')
    slug = models.SlugField(unique=True)
    def __unicode__(self):
        return "%s" % self.name
    class Meta:
        verbose_name_plural = "Yazarlar"
        verbose_name = "Yazar"
    def news_count(self):
        return News.objects.filter(author=self).count()
    news_count.short_description = 'Yazı Sayısı'



class Category(BaseModel):
    name = models.CharField(max_length=30,verbose_name='kategori adı', null=True)
    slug = models.SlugField(null=True,unique=True) #TODO null=False
    class Meta:
        verbose_name_plural = "haber kategorileri"
        verbose_name = "haber kategorisi"
    def __unicode__(self):
        return "%s" % (self.name)

    @models.permalink
    def get_absolute_url(self):
        return ('core.views.news.news_category', (), {'slug': self.slug})

class News(BaseWithStatus):
    title = models.CharField( max_length=100, verbose_name=u'haber başlık')
    spot = models.TextField(validators=[MaxLengthValidator(1300)],verbose_name=u'spot')
    author = models.ForeignKey(Author, verbose_name=u"yazar")
    building_type = models.PositiveSmallIntegerField(choices=BUILDING_TYPE, verbose_name=u'ilgili yapı tipi')
    news_bulletin = models.CharField(max_length=50, default="sahibinden.com", verbose_name=u'haberin Kaynağı')
    content = models.TextField(verbose_name= u'Haber İçeriği')
    photo = models.ImageField( upload_to=get_upload_path,
        help_text=help_text_fix % (file_size, OPTIMUM_NEWS_WIDTH, OPTIMUM_NEWS_HEIGHT), verbose_name='haberin fotoğrafı')
    thumb = models.ImageField(upload_to=get_upload_path,
        help_text=help_text_fix % (file_size, OPTIMUM_NEWS_THUMB_WIDTH, OPTIMUM_NEWS_THUMB_HEIGHT), null=True, blank=True, verbose_name='haberin küçük fotoğrafı')
    carousel_text = models.CharField(max_length=100, blank=True, null=True,verbose_name=u'carousel metin alanı')
    slug = models.SlugField(unique=True)
    keywords = models.CharField(max_length=1000, blank=True, null=True,verbose_name=u'meta keywords')
    categories = models.ManyToManyField(Category, verbose_name='kategoriler')
    publish_date = models.DateTimeField(default = datetime.today(),verbose_name=u'Yayımlanma Tarihi')
    second = models.IntegerField(default=5, verbose_name='Vitrinde kalma süresi')
    tags = TaggableManager()

    _slug_cache = None

    def get_url(self):
        if not self._slug_cache:
            self._slug_cache = reverse('news-detail',kwargs={'slug': self.slug})
        return self._slug_cache

    def related_project_count(self):
        return self.project_set.all().count()
    related_project_count.short_description = _(u'Proje Sayısı')

    def __unicode__(self):
        return "%s" % self.title

    class Meta:
        verbose_name_plural = _(u"Haberler")
        verbose_name = _(u"Haber")

    def get_photo(self):
        if self.photo:
            return u'<img src="%s" style="width:80px; height:80px;" />' % self.photo.url
        else:
            return ''
    def get_thumb(self):
        if self.thumb:
            return u'<img src="%s" style="width:78px; height:78px;" />' % self.thumb.url
        else:
            return ''
    get_photo.allow_tags = True
    get_photo.short_description = _(u'Haber Foto')
    get_thumb.allow_tags = True
    get_thumb.short_description = _(u'Thumbnail' )

    @models.permalink
    def get_absolute_url(self):
        return ('core.views.news.news_detail', (), {'slug': self.slug})

    def get_categories(self):
        return ', '.join([c.name for c in self.categories.all()])
    get_categories.short_description = _(u'Kategoriler')


class NewsPhoto(BaseModel):
    photo = models.ImageField(upload_to=get_upload_path, default="photos/noimage.png",verbose_name= u'Fotoğraf')
    news = models.ForeignKey(News, verbose_name=u'Haber')
    width = models.IntegerField(verbose_name='Genişlik')
    height = models.IntegerField(verbose_name='Yükseklik')
    def get_photo(self):
        if self.photo:
            return u'<img src="%s" style="width:%dpx; height:%dpx;" />' % (self.photo.url, self.width, self.height)
        else:
            return ''
    get_photo.allow_tags = True
    get_photo.short_description = u'Fotoğraf'

    class Meta:
        verbose_name_plural = u"Haber Fotoğrafları"
        verbose_name = u"Haber Fotoğrafı"

    def __unicode__(self):
        return "%s %s" % (self.id, self.news.title)

class ProjectBuildingType(BaseModel):
    name = models.CharField(max_length=50)
    type = models.PositiveSmallIntegerField(choices=PROJECT_TYPE)
    slug = models.SlugField()

    class Meta:
        verbose_name_plural = _(u"Proje Kategorileri")
        verbose_name = _(u"Proje Kategorisi")

    def __unicode__(self):
        return "%s" % self.name


class HouseSpecification(BaseModel):
    name = models.CharField(max_length=50)
    def __unicode__(self):
        return "%s" % self.name
    class Meta:
        verbose_name_plural = _(u"Konut Özellikleri")
        verbose_name = _(u"Konut Özelliği")

class RoomCount(BaseModel):
    name = models.CharField(max_length=10)
    def __unicode__(self):
        return "%s" % self.name
    class Meta:
        verbose_name_plural = _(u"Oda Sayıları")
        verbose_name = _(u"Oda Sayısı")

class SpecificationCategory(BaseModel):
    name = models.CharField( max_length=50)
    def __unicode__(self):
        return "%s" % self.name

class Specification(BaseModel):
    name = models.CharField( max_length=50)
    category = models.ForeignKey(SpecificationCategory)
    def __unicode__(self):
        return "%s" % self.name
    class Meta:
        verbose_name_plural = _(u"Özellikler")
        verbose_name = _(u"Özellik")

class SpecificationGroup(BaseModel):
    SPECIFICATION_TYPE = (
                 (0, _(u'Konut')),
                 (1, _(u'Proje')),
                 )
    type = models.PositiveSmallIntegerField(choices=SPECIFICATION_TYPE)
    group = models.PositiveSmallIntegerField(choices=SPECIFICATION_GROUP_TYPE, blank=True, null=True)
    name = models.CharField( max_length=50)
    specifications = models.ManyToManyField(Specification)
    building_types = models.ManyToManyField(ProjectBuildingType)

    def related_buildingtypes(self):
        return ", ".join([bt.__str__() for bt in self.building_types.all()])

    def related_specifications(self):
        return ", ".join([specification.__str__() for specification in self.specifications.all()])

    def __unicode__(self):
        return "%s" % self.id

    class Meta:
        verbose_name_plural = _(u"Özellik Grupları")
        verbose_name = _(u"Özellik Grubu")

class Region(BaseModel):
    name = models.CharField(max_length=50)
    latitude = models.FloatField()
    longitude = models.FloatField()
    def __unicode__(self):
        return "%s" % self.name
    class Meta:
        verbose_name_plural = _(u"Bölgeler")
        verbose_name = _(u"Bölge")

class Project(BaseWithStatus):
    removal_reason = models.PositiveSmallIntegerField(choices=PASSIVE_CHOICES, default = None, blank=True, null=True, verbose_name= u'Pasife Alınma Sebebi')
    name = models.CharField(_(u'Proje Adı'), max_length=50)
    catchword  = models.CharField(max_length=500, blank=True, null=True, verbose_name = u'Projenin Sloganı')
    logo = models.ImageField(upload_to=get_upload_path, blank=True, null=True,
        help_text=help_text_fix%(file_size, OPTIMUM_PROJECT_LOGO_WIDTH, OPTIMUM_PROJECT_LOGO_HEIGHT))
    project_thumb = models.ImageField(upload_to=get_upload_path, blank=True, null=True,
                             help_text=help_text_fix%(file_size, OPTIMUM_PROJECT_THUMB_WIDTH, OPTIMUM_PROJECT_THUMB_HEIGHT))
    banner = models.ImageField(upload_to=get_upload_path, blank=True, null=True,
        help_text=help_text_flexible %(file_size, OPTIMUM_BANNER_WIDTH-20, OPTIMUM_BANNER_WIDTH+20, OPTIMUM_BANNER_HEIGHT-20, OPTIMUM_BANNER_HEIGHT + 20 ))
    glass_window_photo = models.ImageField(_(u'Vitrin Foto'), upload_to=get_upload_path, blank=True, null=True,
        help_text=help_text_fix%(file_size, OPTIMUM_GLASSWINDOW_WIDTH, OPTIMUM_GLASSWINDOW_HEIGHT))
    carousel_photo = models.ImageField(_(u'Carousel Foto'), upload_to=get_upload_path, blank=True, null=True,
        help_text=help_text_fix%(file_size, OPTIMUM_CAROUSEL_WIDTH, OPTIMUM_CAROUSEL_HEIGHT))
    cover_photo = models.ImageField(upload_to=get_upload_path, blank=True, null=True, verbose_name=u'kapak fotoğrafı',
                                    help_text=help_text_fix%(file_size, OPTIMUM_COVER_WIDTH, OPTIMUM_COVER_HEIGHT ))
    carousel_text = models.CharField(_(u'Carousel Metin Alanı'), max_length=100, blank=True, null=True)
    company = models.ForeignKey(Company, verbose_name=_(u'Proje Sahibi Firma'), default=None, null=True, blank=True)
    joint_company = models.ForeignKey(JointCompany, verbose_name=_(u'Ortaklı Proje Sahibi Firma'), default=None, null=True, blank=True)
    website = models.URLField(_(u'Web Sitesi'), max_length=200, blank=True, null=True, verify_exists=False)
    is_completed = models.BooleanField(_(u'Proje Tamamlandı Mı?'), default=False, blank=True)
    total_area = models.CharField(_(u'Toplam Proje Alanı'), max_length=50, blank=True, null=True)
    total_external_area = models.CharField(_(u'Toplam Proje Açık Alanı'), max_length=50, blank=True, null=True)
    price_min = models.FloatField(_(u'Fiyat (min)'), null=True, blank=True)
    price_max = models.FloatField(_(u'Fiyat (max)'), null=True, blank=True)
    currency = models.CharField(_(u'Fiyat Birimi'), max_length=4, null=True, blank=True)
    is_credit_compatible  = models.BooleanField(_(u'Krediye Uygun Mu?'), default=False, blank=True)
    detail = models.TextField(_(u'Proje Hakkında'), blank=True, default=' ')
    delivery_date = models.DateField(_(u'Teslim Tarihi'), blank=True, null=True)
    delivery_immediate = models.BooleanField(_(u'Hemen Teslim'), default=False, blank=True)
    address = models.TextField(_(u'Açık Adres'))
    region = models.ForeignKey(Region, verbose_name=_(u"Bölge"), blank=True, null=True)
    city = models.ForeignKey(City, verbose_name=_(u"İl"))
    town = models.ForeignKey(Town, verbose_name=_(u"İlçe"))
    district = models.ForeignKey(District, verbose_name=_(u'Mahalle'), blank=True, null=True)
    specifications = models.ManyToManyField(Specification, verbose_name=_(u'Proje Özellikleri'))
    latitude = models.FloatField()
    longitude = models.FloatField()
    news = models.ManyToManyField(News)
    related_news = models.ManyToManyField(News, through='RelatedProject', related_name='related_projects')
    sales_office_phone = models.CharField(_(u'Telefon'), max_length=11, help_text=_(u'11 Haneli Telefon Numarası'))
    sales_office_phone_2 = models.CharField(_(u'Telefon 2'), max_length=11, help_text=_(u'11 Haneli Telefon Numarası'), blank=True, null=True)
    sales_mobile_phone = models.CharField(_(u'Cep No'), max_length=11, help_text=_(u'11 Haneli Cep Numarası'), blank=True, null=True)
    sales_fax = models.CharField(_(u'Fax'), max_length=11, help_text=_(u'11 Haneli Fax Numarası'), blank=True, null=True)
    sales_email = models.EmailField(verbose_name = 'Email' )
    sales_contact = models.CharField(_(u'İletişim Kurulacak Kişi'), max_length=50, blank=True, null=True)
    slug = models.SlugField(unique=True)
    introducing_text = models.TextField(_(u'Tanıtım Metni'), validators=[MaxLengthValidator(10000)], blank=True, null=True)
    price_info = models.ImageField(upload_to=get_upload_path, blank=True, null=True, verbose_name=u'Fiyat Fotoğraf',
                              help_text=help_text_fix%(file_size, OPTIMUM_PRICE_WIDTH, OPTIMUM_PRICE_HEIGHT ))
    price_info_big = models.ImageField(upload_to=get_upload_path, blank=True, null=True, verbose_name=u'Fiyat Büyük Fotoğraf',
                                       help_text=help_text_flexible %(file_size, OPTIMUM_PRICE_WIDTH, OPTIMUM_PRICE_WIDTH+400, OPTIMUM_PRICE_HEIGHT, OPTIMUM_PRICE_HEIGHT + 750 ))
    status_plan_photo = models.ImageField(upload_to=get_upload_path, blank=True, null=True, verbose_name=u'vaziyet planı fotoğraf',
                                   help_text=help_text_fix%(file_size, OPTIMUM_STATUSPLAN_WIDTH, OPTIMUM_STATUSPLAN_HEIGHT ))
    status_plan_photo_big = models.ImageField(upload_to=get_upload_path, blank=True, null=True, verbose_name=u'vaziyet planı büyük fotoğraf',
                                       help_text=help_text_flexible %(file_size, OPTIMUM_STATUSPLAN_WIDTH, OPTIMUM_PRICE_WIDTH+400, OPTIMUM_STATUSPLAN_HEIGHT, OPTIMUM_STATUSPLAN_HEIGHT + 750 ))
    house_count = models.PositiveIntegerField(null=True, blank=True, verbose_name=u'Konut Sayısı')

    contract = models.TextField(validators=[MaxLengthValidator(10000)], blank=True, null=True, verbose_name = u'Şartname')
    _package = models.ForeignKey('Package',null=True,blank=True,related_name=u'aktif paket')

    @property
    def package(self):
        return self._package

    @package.setter
    def package(self, value):
        try:
            active_package= self.package_set.filter(start_date__lte = datetime.today().date(), end_date__gt= datetime.today().date()).order_by('-type')[0]
        except IndexError:
            active_package = None
        self._package = active_package
        self.save()

    @package.deleter
    def package(self):
        self._package = None

    def save(self, *args, **kwargs):
        super(Project, self).save(*args, **kwargs) # Call the "real" save() method.

    def __unicode__(self):
        return "%s" % self.name

    class Meta:
        verbose_name_plural = _(u"Projeler")
        verbose_name = _(u"Proje")

    def get_package(self):
        return 'STANDART' if not self.package else self.package.get_type_display()
    get_package.short_description = u'Paket'

    def get_location(self):
        # Remember, longitude FIRST!
        return Point(self.longitude, self.latitude)

    def get_min_area(self):
        area_dict = self.housetype_set.all().aggregate(Min('total_area'))
        if area_dict.has_key('total_area__min') and area_dict['total_area__min'] != None:
            return area_dict['total_area__min']
        else :
            return 0

    def get_max_area(self):
        area_dict = self.housetype_set.all().aggregate(Max('total_area'))
        if area_dict.has_key('total_area__max') and area_dict['total_area__max'] != None:
            return area_dict['total_area__max']
        else :
            return 0

    def get_company(self):
        if self.joint_company:
            return self.joint_company
        else:
            return self.company
    get_company.short_description = _(u'Proje Sahibi Firma')

    _type_cache = None
    def get_type(self):
        if self._type_cache is None:
            is_residential = self.housetype_set.filter(project_building_type__in=ProjectBuildingType.objects.filter(type=0)).count()
            is_commercial = self.housetype_set.filter(project_building_type__in=ProjectBuildingType.objects.filter(type=1)).count()
            if is_residential and is_commercial:
                typ = 2
            elif is_residential:
                typ = 0
            elif is_commercial:
                typ = 1
            else:
                typ = None
            self._type_cache = typ

        return self._type_cache

    def get_default_photo_url(self):
        ordered_photos = self.projectphoto_set.all().order_by('create_date')
        try:
            return ordered_photos[0].photo.url
        except:
            return STATIC_URL+'images/noimage.png'

    def get_status_plan_photo_url(self):
        status_plan_photos = self.floorplanphoto_set.all()
        try:
            return status_plan_photos[0].photo.url
        except:
            return None

    def get_default_photo(self):
        ordered_photos = self.projectphoto_set.all().order_by('create_date')
        try:
            return ordered_photos[0].photo
        except:
            return 'photos/noimage.png'

    def get_glass_window_photo(self):
        if self.glass_window_photo:
            return u'<img src="%s" style="width:40px; height:40px;" />' % self.glass_window_photo.url
        else:
            return ''

    def get_caption(self):
        data = {'project_name':self.name, 'city_name':self.city.name, 'town_name': self.town.name}

        if self.get_type() == 1:
            # Translators: Proje tipi ofis olan projeler için başlık metni
            caption = _(u"%(project_name)s %(city_name)s %(town_name)s Projesi") % data
        else:
            # Translators: Proje tipi konut olan projeler için başlık metni
            caption = _(u"%(project_name)s %(city_name)s %(town_name)s Konut Projesi") % data

        return caption

    get_glass_window_photo.allow_tags = True
    get_glass_window_photo.short_description = _(u'Vitrin Foto')

    def get_pbts(self):
        return ProjectBuildingType.objects.filter(id__in=self.housetype_set.values_list('project_building_type', flat=True)).values_list('id', flat=True)

    #def get_pack(self):
     #   return self.package_set.all().filter(start_date__lte= datetime.now().date(), end_date__gte = datetime.now().date())

    def get_as_json(self):
        from django.template.loader import render_to_string
        from django.core.cache import cache
        key = 'get_as_json_' + str(self.id)
        response = cache.get(key)
        timeout = 60 * 60 * 6
        if response:
            return response
        else:
            pbts = self.get_pbts()
            response = render_to_string('core/project.json', { 'project': self, 'pbts':pbts, 'SERVER_ROOT': SERVER_ROOT, 'MEDIA_URL': MEDIA_URL })
            cache.set(key, response, timeout)
            return response

    @models.permalink
    def get_absolute_url(self):
        return ('project', (), {'company_slug': self.get_company().slug, 'project_slug':self.slug})

#Kat Planı
class HouseType(BaseModel):
    project = models.ForeignKey(Project, verbose_name=u'Proje')
    name = models.CharField(max_length=50, verbose_name = u'konut tipi adı')
    room_count = models.ForeignKey(RoomCount, verbose_name=u'Oda Sayısı')
    bathroom_count = models.PositiveSmallIntegerField(choices=BATHROOM_COUNT, null=True, blank=True, default=0,verbose_name=u'Banyo Sayısı')
    price_min = models.FloatField(null=True, blank=True, verbose_name=u'Fiyat (min)')
    price_max = models.FloatField(null=True, blank=True, verbose_name=u'Fiyat (max)')
    total_area = models.PositiveIntegerField(null=True, blank=True, verbose_name=u'toplam alan')
    project_building_type = models.ForeignKey(ProjectBuildingType, verbose_name=u'proje kategorisi')
    specifications = models.ManyToManyField(Specification, verbose_name=u'konut tipi özellikleri')
    photo = models.ImageField(upload_to=get_upload_path, blank=True, null=True, verbose_name=u'konut tipi fotoğrafı',
                              help_text=help_text_flexible %(file_size, OPTIMUM_STATUSPLAN_WIDTH, OPTIMUM_STATUSPLAN_WIDTH+400, OPTIMUM_STATUSPLAN_HEIGHT, OPTIMUM_STATUSPLAN_HEIGHT + 750 ))

    description = models.TextField( blank=True, null=True, verbose_name=u'konut tipi açıklama/bilgi')
    slug = models.CharField(max_length=50)
    def __unicode__(self):
        return "%s" % self.name

    class Meta:
        verbose_name_plural = u"Konut Tipleri"
        verbose_name = u"Konut Tipi"

    def house_type_name(self):
        return u'<a href="/projeler/admin/core/housetype/%s" >%s</a>' % (self.name, self.id)

    house_type_name.allow_tags = True
    house_type_name.short_description = u'konut tipi adı'

    @models.permalink
    def get_absolute_url(self):
        return ('core.views.house', (), {'company_slug': self.project.get_company().slug, 'project_slug':self.project.slug, 'house_slug':self.slug, 'house_id':str(self.id)})

class Package(BaseModel):
    project = models.ForeignKey(Project, verbose_name=u'Proje')
    type = models.PositiveSmallIntegerField(choices=PACKAGE_TYPE, default=1, verbose_name=u'paket tipi')
    start_date = models.DateField(default=datetime.today().date(),verbose_name=u'Başlangıç Tarihi')
    validity_as_months = models.PositiveSmallIntegerField(default=3,choices=VALIDITY_TYPE,verbose_name=u'Geçerlilik Süresi')
    end_date = models.DateField(default=datetime.today().date(),verbose_name=u'Bitiş Tarihi')
    description = models.TextField(blank=True, null=True,verbose_name=u'Not')

    class Meta:
        verbose_name_plural = u"Paketler"
        verbose_name = u"Paket"

    def __unicode__(self):
        return "%s %s" % (self.id, self.get_type_display())

#Konut tipi Photo (kat plan)
class HousePlanPhoto(BaseModel):
    photo = models.ImageField(upload_to=get_upload_path, help_text=_(help_text_fix) % (file_size, MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT), default="photos/noimage.png")
    house = models.ForeignKey(HouseType, verbose_name=_(u'Konut Tipi'))
    class Meta:
        verbose_name_plural = _(u"Kat Planı Fotoğrafları")
        verbose_name = _(u"Kat Planı Fotoğrafı")
    def __unicode__(self):
        return "%s" % self.id

class ProjectPhoto(BaseModel):
    photo = models.ImageField(upload_to=get_upload_path,
                             help_text=help_text_fix%(file_size, OPTIMUM_PROJECT_PHOTO_WIDTH, OPTIMUM_PROJECT_PHOTO_HEIGHT), default="photos/noimage.png",verbose_name= u'Fotoğraf')
    project = models.ForeignKey(Project, verbose_name=u'Proje')
    def get_photo(self):
        if self.photo:
            return u'<img src="%s" style="width:40px; height:40px;" />' % self.photo.url
        else:
            return ''
    get_photo.allow_tags = True
    get_photo.short_description = u'Fotoğraf'

    class Meta:
        verbose_name_plural = u"Proje Fotoğrafları"
        verbose_name = u"Proje Fotoğrafı"

    def __unicode__(self):
        return "%s %s" % (self.id, self.project.name)

class FloorPlanPhoto(BaseModel):
    photo = models.ImageField('Foto', upload_to=get_upload_path, default="photos/noimage.png")
    project = models.ForeignKey(Project, verbose_name='Proje')
    def __unicode__(self):
        return "%s" % self.id
    class Meta:
        verbose_name_plural = "Yerleşim Planı Fotoğrafları"
        verbose_name = "Yerleşim Planı Foto"


class GlassWindow(BaseModel):
    project = models.ForeignKey(Project, verbose_name='Proje')
    type = models.PositiveSmallIntegerField(choices=GLASS_WINDOW_TYPE, default=0, verbose_name='Vitrin Sayfası')
    priority = models.PositiveSmallIntegerField(choices=PRIORITY, default=1, verbose_name='Görüntüleneceği Sayfa')
    start_date = models.DateField(verbose_name='Başlangıç Tarihi')
    validity_as_months = models.PositiveSmallIntegerField(choices=GLASS_WINDOW_VALIDITY_TYPE, verbose_name='Geçerlilik Süresi')
    end_date = models.DateField(verbose_name='Bitiş Tarihi')
    description = models.TextField(blank=True, null=True, verbose_name='Not')
    class Meta:
        verbose_name_plural = "Vitrinler"
        verbose_name = "Vitrin"
        unique_together = (("project", "type","start_date"),)
    def __unicode__(self):
        return "%s" % self.id

class Page(BaseModel):
    name = models.CharField('Görüntülenecek Alan', max_length=50)
    class Meta:
        verbose_name_plural = "Sayfalar"
        verbose_name = "Sayfa"
    def __unicode__(self):
        return "%s" % self.name

class Gallery(BaseWithStatus):
    name = models.CharField('Galeri Adı', max_length=50)
    photo = models.ImageField(upload_to=get_upload_path, verbose_name='Galeri Fotoğrafı',
                             help_text=help_text_fix%(file_size, OPTIMUM_GALLERY_WIDTH, OPTIMUM_GALLERY_HEIGHT ))
    display_in = models.ManyToManyField(Page, verbose_name='Görüntüleneceği Alan')
    projects = models.ManyToManyField(Project, verbose_name='Projeler', blank=True, null=True)
    description = models.TextField('Galerinin Açıklaması', blank=True, null=True)
    slug = models.SlugField(unique=True)
    def __unicode__(self):
        return "%s" % self.name
    def related_project_count(self):
        return self.projects.count()
    related_project_count.short_description = 'Proje Sayısı'
    def where_to_display(self):
        return  ", ".join([page.__str__() for page in self.display_in.all()])
    where_to_display.short_description = 'Görüntüleneceği Alan'
    def edit_button(self):
        return '<input type="button" onclick="location.href=\'/projeler/admin/core/gallery/%s/project\'" value="Projeleri Yönet"/>' % self.id
    edit_button.allow_tags = True
    edit_button.short_description = 'Galeride Görüntülenecek Projeler'

    _slug_cache = None
    def get_url(self):
        if not self._slug_cache:
            self._slug_cache = reverse('gallery-main',kwargs={'slug': self.slug})
        return self._slug_cache

    @models.permalink
    def get_absolute_url(self):
        return ('core.views.gallery', (), {'slug': self.slug})

    class Meta:
        verbose_name_plural = "Galeriler"
        verbose_name = "Galeri"

class NewsWidget(BaseModel):
    display_in = models.ForeignKey(Page, verbose_name='Görüntüleneceği Alan')
    news_list = models.ManyToManyField(News, verbose_name='Haberler')
    def related_news_count(self):
        return self.news_list.count()
    related_news_count.short_description = 'Haber Sayısı'
    class Meta:
        verbose_name_plural = "Haber Alanları Yönetimi"
        verbose_name = "Haber Alanı Yönetimi"

    def edit_button(self):
        return '<input type="button" onclick="location.href=\'/projeler/admin/core/newswidget/%s/news\'" value="Haberleri Yönet"/>' % self.id
    edit_button.allow_tags = True
    edit_button.short_description = 'Haberleri Yönet'
    def __unicode__(self):
        return "%s" % self.display_in.name


class Carousel(BaseModel):
    display_in = models.ForeignKey(Page, verbose_name='Görüntüleneceği Alan')
    news_list = models.ManyToManyField(News, verbose_name='Haberler', through='CarouselNewsOrder')
    project_list = models.ManyToManyField(Project, verbose_name='Projeler')
    def related_news_count(self):
        return self.news_list.count()
    related_news_count.short_description = 'Haber Sayısı'
    def related_project_count(self):
        return self.project_list.count()
    related_project_count.short_description = 'Proje Sayısı'
    def edit_buttons(self):
        if self.display_in.name.lower().find('haber') != -1:
            return '<input type="button" onclick="location.href=\'/projeler/admin/core/carousel/%s/news\'" value="Haber Yönetimi"/>' % self.id
        else:
            return '<input type="button" onclick="location.href=\'/projeler/admin/core/carousel/%s/news\'" value="Haber Yönetimi"/>&nbsp;&nbsp;&nbsp;<input type="button" onclick="location.href=\'/projeler/admin/core/carousel/%s/project\'" value="Proje Yönetimi"/>' % (self.id, self.id)
    edit_buttons.allow_tags = True
    edit_buttons.short_description = 'Haber-Proje Yönet'
    class Meta:
        verbose_name_plural = "Carousel Alanları Yönetimi"
        verbose_name = "Carousel"
    def __unicode__(self):
        return "%s" % self.display_in.name


class CarouselNewsOrder(BaseModel):
    news  = models.ForeignKey(News)
    carousel = models.ForeignKey(Carousel)
    order = models.PositiveIntegerField(blank=True, null=True)
    def __unicode__(self):
        return "%s" % self.id

class GuestBook(BaseModel):
    name = models.CharField(max_length=32,verbose_name = u'ad')
    surname = models.CharField(max_length=32, verbose_name = u'soyad')
    occupation = models.CharField(max_length=32, blank=True, null=True, verbose_name = u'meslek')
    email = models.EmailField(verbose_name = u'e-mail')
    phone = models.CharField(max_length=13, blank=True, null=True, verbose_name = u'telefon')
    message = models.TextField(max_length=512, blank=True, null=True, verbose_name = u'mesaj')
    city = models.ForeignKey(City, blank=True, null=True, )
    country = models.ForeignKey(Country, blank=True, null=True, )
    confirmation = models.PositiveSmallIntegerField(choices=CONFIRMATION_TYPE, default = 0, verbose_name = u'onay durumu')
    project = models.ForeignKey(Project)

    class Meta:
        verbose_name_plural = "ziyaretçiler"
        verbose_name = "ziyaretçi"

    def __unicode__(self):
        return "%s  %s" % (self.name,self.surname)

class ProjectRegistration(BaseModel):
    company_name = models.CharField(max_length=64,verbose_name = u'Firma Adı')
    project_name = models.CharField(max_length=128,verbose_name = u'Proje Adı')
    contact_name = models.CharField(max_length=64,verbose_name = u'Yetkili Adı / Soyadı')
    contact_phone = models.CharField(max_length=13,verbose_name = u'Yetkili Telefon Numarası')
    contact_email = models.EmailField(verbose_name = u'Yetkili E-Posta')

    class Meta:
        verbose_name_plural = "Proje Başvuruları"
        verbose_name = "Proje Başvurusu"

    def __unicode__(self):
        return "%s %s" % (self.company_name, self.project_name)

class RelatedProject(BaseWithStatus):
    project = models.ForeignKey(Project)
    news = models.ForeignKey(News)
    send_message = models.BooleanField(default=False)

    class Meta:
        unique_together = (("project", "news"),)
