from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator

class SystemSettings(models.Model):
    USER_ROLE_CHOICES = (
        ('clientuser', 'Client User'),
        ('epcuser', 'EPC User'),
        ('contractoruser', 'Contractor User'),
    )
    
    BACKUP_FREQUENCY_CHOICES = (
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    )
    
    LOG_LEVEL_CHOICES = (
        ('DEBUG', 'Debug'),
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
        ('CRITICAL', 'Critical'),
    )
    
    siteName = models.CharField(max_length=200, default='EHS Management System')
    siteDescription = models.TextField(blank=True, default='')
    maintenanceMode = models.BooleanField(default=False)
    allowRegistration = models.BooleanField(default=False)
    defaultUserRole = models.CharField(max_length=50, choices=USER_ROLE_CHOICES, default='clientuser')
    sessionTimeout = models.PositiveIntegerField(default=60, validators=[MinValueValidator(5), MaxValueValidator(480)])
    maxFileSize = models.PositiveIntegerField(default=10, validators=[MinValueValidator(1), MaxValueValidator(100)])
    emailNotifications = models.BooleanField(default=True)
    smsNotifications = models.BooleanField(default=False)
    backupFrequency = models.CharField(max_length=50, choices=BACKUP_FREQUENCY_CHOICES, default='daily')
    logLevel = models.CharField(max_length=20, choices=LOG_LEVEL_CHOICES, default='INFO')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'System Settings'

class Backup(models.Model):
    BACKUP_TYPES = (
        ('full', 'Full'),
        ('incremental', 'Incremental'),
        ('differential', 'Differential'),
    )
    STATUS_CHOICES = (
        ('completed', 'Completed'),
        ('in_progress', 'In Progress'),
        ('failed', 'Failed'),
    )

    name = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=BACKUP_TYPES, default='full')
    description = models.TextField(blank=True, default='')
    file = models.FileField(upload_to='backups/', blank=True, null=True)
    size = models.CharField(max_length=50, blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')
    progress = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(100)])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
