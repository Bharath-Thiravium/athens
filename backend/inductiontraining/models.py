from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class InductionTraining(models.Model):
    STATUS_CHOICES = (
        ('planned', _('Planned')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    )
    
    title = models.CharField(_('Title'), max_length=255)
    description = models.TextField(_('Description'), blank=True)
    date = models.DateField(_('Date'))
    location = models.CharField(_('Location'), max_length=255, blank=True)
    conducted_by = models.CharField(_('Conducted By'), max_length=255)
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='planned')
    project = models.ForeignKey(
        'authentication.Project',
        on_delete=models.CASCADE,
        related_name='induction_trainings',
        null=True,
        blank=True
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='created_induction_trainings'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-date']
        verbose_name = _('Induction Training')
        verbose_name_plural = _('Induction Trainings')

class InductionAttendance(models.Model):
    STATUS_CHOICES = (
        ('present', _('Present')),
        ('absent', _('Absent')),
    )
    
    induction = models.ForeignKey(
        InductionTraining,
        on_delete=models.CASCADE,
        related_name='attendances'
    )
    worker_id = models.IntegerField(_('Worker ID'))
    worker_name = models.CharField(_('Worker Name'), max_length=255)
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='present')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.worker_name} - {self.induction.title}"
    
    class Meta:
        unique_together = ('induction', 'worker_id')
        verbose_name = _('Induction Attendance')
        verbose_name_plural = _('Induction Attendances')
