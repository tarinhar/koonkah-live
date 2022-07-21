from email.policy import default
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.urls import reverse


class User(AbstractUser):
    employee_id = models.CharField(max_length=10, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    avatar = models.ImageField(
        upload_to='users/', null=True, blank=True, default="avatar.svg")
    section = models.CharField(max_length=200, null=True, blank=True)
    department = models.CharField(max_length=200, null=True, blank=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username


class Category(models.Model):
    name = models.CharField(max_length=200)
    name_th = models.CharField(max_length=200, null=True, blank=True)
    slug = models.SlugField(max_length=200, blank=True, null=True, unique=True)
    parent_category = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.DO_NOTHING)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='categories/',
                              blank=True, null=True, default="no-image.png")

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            return super().save(*args, **kwargs)

    #subcategories = Category.objects.filter(parent_category__id=target_category.id)


class Station(models.Model):
    name = models.CharField(max_length=100)
    location = models.TextField(null=True, blank=True)
    staff = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to='stations/',
                              null=True, blank=True, default="no-image.png")

    def __str__(self):
        return self.name

# Reusable Material


class Item(models.Model):
    name = models.CharField(max_length=200)
    owner = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)
    category = models.ForeignKey(
        Category, on_delete=models.DO_NOTHING, null=True)
    description = models.TextField(null=True, blank=True)
    station = models.ForeignKey(
        Station, on_delete=models.DO_NOTHING, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    quantity = models.IntegerField(default=1)
    size = models.CharField(max_length=50, null=True, blank=True)
    weight = models.FloatField(blank=True, null=True)
    image = models.ImageField(
        upload_to='items/%Y/%m/%d/', null=True, blank=True)
    reusable = models.BooleanField(default=True)  # Reusable
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return "{}: {}".format(self.id, self.name)

    # def save(self, *args, **kwargs):
    #     super().save(*args, **kwargs)

    #     img = Image.open(self.image.path)

    #     if img.height > 300 or img.width > 300:
    #         output_size = (300, 300)
    #         img.thumbnail(output_size)
    #         img.save(self.image.path)

    def get_absolute_url(self):
        return reverse("item-detail", args=[self.id])

    # def save(self, *args, **kwargs):
    #     if not self.slug:
    #         self.slug = slugify(self.name)
    #         return super().save(*args, **kwargs)


class Reuse(models.Model):
    DRAFT = 'DR'
    PENDING = 'PE'
    DONE = 'DO'
    CANCEL = 'CA'
    STATUS_CHOICES = [
        (DRAFT, 'Draft'),
        (PENDING, 'Pending'),
        (DONE, 'Done'),
        (CANCEL, 'Cancel'),
    ]
    item = models.ForeignKey(Item, on_delete=models.DO_NOTHING, null=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)
    quantity = models.IntegerField(blank=True, null=True)
    weight = models.FloatField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default=PENDING)

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return "{}".format(self.id)


class Credit(models.Model):
    user = models.OneToOneField(User, on_delete=models.DO_NOTHING)
    total_point = models.FloatField(null=True, blank=True, default=0)
    owner_point = models.FloatField(null=True, blank=True, default=0)
    reuse_point = models.FloatField(null=True, blank=True, default=0)
    description = models.CharField(
        max_length=100, null=True, blank=True, default='Koonkah')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True, null=True, blank=True)

    class Meta:
        ordering = ['-updated_at', '-created_at']
        db_table = 'credit'

    def save(self, *args, **kwargs):
        self.owner_point = self.user.item_set.count()
        self.reuse_point = self.user.reuse_set.count()
        self.total_point = self.owner_point + self.reuse_point
        super(Credit, self).save(*args, **kwargs)

    def __str__(self):
        return self.user.username
