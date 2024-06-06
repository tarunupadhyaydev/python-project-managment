from django.db import models
from django.utils.translation import gettext_lazy as _
from projects.models import Project
from django.conf import settings

# Create your models here.
class Task(models.Model):
  class TaskStatus(models.TextChoices):
      OPEN = "OP", _("Open")
      IN_PROGRESS = "IP", _("In-Progress")
      COMPLETED = "CP", _("Completed")

  class TaskPriority(models.TextChoices):
      LOW = "LW", _("Low")
      MEDIUM = "MD", _("Medium")
      HIGH = "HG", _("High")

  name = models.CharField(max_length=255, verbose_name="Task Name")
  description = models.TextField(blank=True, verbose_name="Task Description")
  project =  models.ForeignKey(Project,null=True, on_delete=models.CASCADE, related_name='task_project_model')
  due_date = models.DateField(null=True,blank=True, verbose_name="Due Date")
  status = models.CharField(
    max_length=2,
    choices=TaskStatus,
    default=TaskStatus.OPEN,
  )
  priority = models.CharField(
    max_length=2,
    choices=TaskPriority,
    default=TaskPriority.LOW,
  )
  created_by = models.ForeignKey(settings.AUTH_USER_MODEL,null=True, on_delete=models.CASCADE, related_name='create_by_task_user_model')
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  deleted_at = models.DateTimeField(null=True, blank=True)


  def __str__(self):
    return self.name