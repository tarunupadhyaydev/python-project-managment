from django.db import models
from projects.models import Project
from tasks.models import Task
from django.utils.translation import gettext_lazy as _
from django.conf import settings

# Create your models here.
class TimeTracker(models.Model):
  class TimelineStatus(models.TextChoices):
      PENDING = "PD", _("Pending")
      APPROVE = "AP", _("Approve")
      REJECT = "RJ", _("Reject")

  project =  models.ForeignKey(Project,null=True, on_delete=models.CASCADE, related_name='timeline_project_model')
  task =  models.ForeignKey(Task, on_delete=models.CASCADE,null=True)
  date = models.DateField(null=True,blank=True, verbose_name="Date")
  start_time = models.TimeField(null=True) 
  end_time = models.TimeField(null=True) 
  duration = models.CharField(max_length=200,null=True,blank=True, verbose_name="Duration")
  description = models.TextField(blank=True,null=True, verbose_name="Description")
  created_by = models.ForeignKey(settings.AUTH_USER_MODEL,null=True, on_delete=models.CASCADE, related_name='create_by_timeline_user_model')
  status = models.CharField(
    max_length=2,
    choices=TimelineStatus,
    default=TimelineStatus.PENDING,
  )
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  deleted_at = models.DateTimeField(null=True, blank=True)

  class Meta:
        verbose_name = 'Timesheet'
        verbose_name_plural = 'Timesheet'


  def __str__(self):
    return f"{self.description}"