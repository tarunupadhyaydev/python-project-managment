from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

# Create your models here.
class Project(models.Model):

  class ProjectStatus(models.TextChoices):
        OPEN = "OP", _("Open")
        IN_PROGRESS = "IP", _("In-Progress")
        COMPLETED = "CP", _("Completed")

  name = models.CharField(max_length=255,verbose_name='Project Name')
  project_number = models.CharField(null=True,max_length=255)
  administrator_name = models.CharField(blank=True,max_length=255, verbose_name="Administrator Name")
  administrator_email = models.CharField(blank=True,max_length=200, verbose_name="Administrator Email")
  description = models.TextField(blank=True, verbose_name="Project Description")
  project_address = models.TextField(blank=True, verbose_name="Project Address")
  reception_telephone = models.CharField(max_length=200,blank=True, verbose_name="Reception Telephone")
  start_date = models.DateField(null=True,blank=True, verbose_name="Start Date")
  # duration = models.DurationField(null=True,blank=True, verbose_name="Project Duration")
  duration = models.CharField(max_length=200,null=True,blank=True, verbose_name="Project Duration")
  value = models.CharField(null=True,max_length=255,blank=True, verbose_name="Project Value")
  cost_center = models.CharField(null=True,max_length=255,blank=True, verbose_name="Project Cost Center")
  cost_center_description = models.TextField(null=True,blank=True, verbose_name="Project Cost Center Description")
  cost_center_number = models.CharField(null=True,max_length=255,blank=True, verbose_name="Project Cost Centre Number")
  status = models.CharField(
    max_length=2,
    choices=ProjectStatus,
    default=ProjectStatus.OPEN,
  )
  created_by = models.ForeignKey(settings.AUTH_USER_MODEL,null=True, on_delete=models.CASCADE, related_name='create_by_project_user_model')
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  deleted_at = models.DateTimeField(null=True, blank=True)


  def __str__(self):
    return self.name