from django.db import models
from django.conf import settings
from django.utils import timezone

# Create your models here.
class Organization(models.Model):
  name = models.CharField(max_length=255)
  description = models.TextField(blank=True,)
  is_active = models.BooleanField(default=True)
  created_by = models.ForeignKey(settings.AUTH_USER_MODEL,null=True, on_delete=models.CASCADE, related_name='create_by_organization_model')
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  deleted_at = models.DateTimeField(null=True, blank=True)

  def delete(self, using=None, keep_parents=False):
    self.deleted_at = timezone.now()
    self.save()

  def hard_delete(self, using=None, keep_parents=False):
        super().delete(using, keep_parents)

  # def restore(self):
  #     self.deleted_at = None
  #     self.save()

  def __str__(self):
    return f"{self.name}"


class OrganizationManager(models.Manager):
  def get_queryset(self):
      return super().get_queryset().filter(deleted_at=null)