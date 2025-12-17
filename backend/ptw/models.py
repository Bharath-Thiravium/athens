from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from authentication.models import Project
import json
import uuid

User = get_user_model()

class PermitType(models.Model):
    RISK_LEVEL_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('extreme', 'Extreme'),
    ]

    PERMIT_CATEGORY_CHOICES = [
        ('hot_work', 'Hot Work'),
        ('confined_space', 'Confined Space'),
        ('electrical', 'Electrical Work'),
        ('height', 'Work at Height'),
        ('excavation', 'Excavation'),
        ('chemical', 'Chemical Work'),
        ('crane_lifting', 'Crane & Lifting Operations'),
        ('cold_work', 'Cold Work'),
        ('specialized', 'Specialized Work'),
        ('marine', 'Marine Operations'),
        ('diving', 'Diving Operations'),
        ('blasting', 'Blasting & Explosives'),
        ('radiation', 'Radiation Work'),
        ('biological', 'Biological Hazards'),
        ('environmental', 'Environmental Work'),
        ('mining', 'Mining Operations'),
        ('oil_gas', 'Oil & Gas Operations'),
        ('nuclear', 'Nuclear Operations'),
        ('aerospace', 'Aerospace Operations'),
        ('airline', 'Airline Operations'),
        ('pharmaceutical', 'Pharmaceutical Work'),
        ('food_processing', 'Food Processing'),
        ('construction', 'Construction Work'),
        ('manufacturing', 'Manufacturing Operations'),
        ('utilities', 'Utilities Work'),
        ('transportation', 'Transportation Operations'),
    ]

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=PERMIT_CATEGORY_CHOICES)
    description = models.TextField(blank=True, null=True)
    color_code = models.CharField(max_length=20, default='#1890ff')
    is_active = models.BooleanField(default=True)
    risk_level = models.CharField(max_length=10, choices=RISK_LEVEL_CHOICES, default='low')
    validity_hours = models.PositiveIntegerField(default=24)
    requires_approval_levels = models.PositiveIntegerField(default=1)
    active = models.BooleanField(default=True)
    
    # Advanced configurations
    requires_gas_testing = models.BooleanField(default=False)
    requires_fire_watch = models.BooleanField(default=False)
    requires_isolation = models.BooleanField(default=False)
    requires_medical_surveillance = models.BooleanField(default=False)
    requires_training_verification = models.BooleanField(default=False)
    mandatory_ppe = models.JSONField(default=list, blank=True)
    safety_checklist = models.JSONField(default=list, blank=True)
    risk_factors = models.JSONField(default=list, blank=True)
    control_measures = models.JSONField(default=list, blank=True)
    emergency_procedures = models.JSONField(default=list, blank=True)
    escalation_time_hours = models.PositiveIntegerField(default=4)
    min_personnel_required = models.PositiveIntegerField(default=1)
    max_validity_extensions = models.PositiveIntegerField(default=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Permit(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
        ('rejected', 'Rejected'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    WORK_NATURE_CHOICES = [
        ('day', 'Day Work'),
        ('night', 'Night Work'),
        ('both', 'Day & Night Work'),
    ]
    
    # Basic Information
    permit_number = models.CharField(max_length=50, unique=True)
    permit_type = models.ForeignKey(PermitType, on_delete=models.CASCADE, related_name='permits')
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField()
    work_order_id = models.CharField(max_length=50, blank=True)
    
    # Location Information
    location = models.CharField(max_length=255)
    gps_coordinates = models.CharField(max_length=100, blank=True)
    site_layout = models.FileField(upload_to='permit_layouts/', blank=True, null=True)
    
    # Time Information
    planned_start_time = models.DateTimeField()
    planned_end_time = models.DateTimeField()
    actual_start_time = models.DateTimeField(null=True, blank=True)
    actual_end_time = models.DateTimeField(null=True, blank=True)
    
    # Work Nature
    work_nature = models.CharField(max_length=10, choices=WORK_NATURE_CHOICES, default='day')
    
    # People Information
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='permits_created')
    issuer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='permits_issued')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='permits_received')
    
    # Contact Information
    issuer_designation = models.CharField(max_length=100, blank=True)
    issuer_department = models.CharField(max_length=100, blank=True)
    issuer_contact = models.CharField(max_length=20, blank=True)
    receiver_designation = models.CharField(max_length=100, blank=True)
    receiver_department = models.CharField(max_length=100, blank=True)
    receiver_contact = models.CharField(max_length=20, blank=True)
    
    # Status and Priority
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    current_approval_level = models.PositiveSmallIntegerField(default=1)
    
    # Risk Assessment
    risk_assessment_id = models.CharField(max_length=50, blank=True)
    risk_assessment_completed = models.BooleanField(default=False)
    probability = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], default=1)
    severity = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], default=1)
    risk_score = models.PositiveSmallIntegerField(default=1)
    risk_level = models.CharField(max_length=10, choices=PermitType.RISK_LEVEL_CHOICES, default='low')
    
    # Safety Information
    control_measures = models.TextField(blank=True)
    ppe_requirements = models.JSONField(default=list, blank=True)
    special_instructions = models.TextField(blank=True)
    safety_checklist = models.JSONField(default=dict, blank=True)
    
    # Isolation Requirements
    requires_isolation = models.BooleanField(default=False)
    isolation_details = models.TextField(blank=True)
    isolation_verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='isolation_verifications')
    isolation_certificate = models.FileField(upload_to='isolation_certificates/', blank=True, null=True)
    
    # Authorization
    approver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='permits_to_approve')
    area_incharge = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='area_permits')
    department_head = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='dept_permits')
    
    # Documentation
    work_procedure = models.FileField(upload_to='work_procedures/', blank=True, null=True)
    method_statement = models.FileField(upload_to='method_statements/', blank=True, null=True)
    risk_assessment_doc = models.FileField(upload_to='risk_assessments/', blank=True, null=True)
    
    # QR Code and Mobile
    qr_code = models.CharField(max_length=500, blank=True)
    mobile_created = models.BooleanField(default=False)
    offline_id = models.CharField(max_length=100, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    
    # Approval tracking
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='permits_approved')
    approval_comments = models.TextField(blank=True)
    
    # Verification tracking
    verifier = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='permits_verified')
    verified_at = models.DateTimeField(null=True, blank=True)
    verification_comments = models.TextField(blank=True)
    
    # Project association
    project = models.ForeignKey('authentication.Project', on_delete=models.CASCADE, related_name='permits', null=True, blank=True)
    
    # Compliance and Audit
    compliance_standards = models.JSONField(default=list, blank=True)
    audit_trail = models.JSONField(default=list, blank=True)
    
    def __str__(self):
        return f"{self.permit_number} - {self.permit_type.name}"

    def calculate_risk_score(self):
        self.risk_score = self.probability * self.severity
        if self.risk_score <= 4:
            self.risk_level = 'low'
        elif self.risk_score <= 9:
            self.risk_level = 'medium'
        elif self.risk_score <= 16:
            self.risk_level = 'high'
        else:
            self.risk_level = 'extreme'
        return self.risk_score

    def can_transition_to(self, new_status):
        valid_transitions = {
            'draft': ['submitted', 'cancelled'],
            'submitted': ['under_review', 'draft'],
            'under_review': ['approved', 'rejected', 'submitted'],
            'approved': ['active', 'cancelled'],
            'active': ['completed', 'suspended'],
            'suspended': ['active', 'cancelled'],
            'completed': [],
            'cancelled': [],
            'expired': [],
            'rejected': ['draft']
        }
        return new_status in valid_transitions.get(self.status, [])

    def is_expired(self):
        return timezone.now() > self.planned_end_time and self.status == 'active'

    def get_duration_hours(self):
        if self.actual_start_time and self.actual_end_time:
            return (self.actual_end_time - self.actual_start_time).total_seconds() / 3600
        return (self.planned_end_time - self.planned_start_time).total_seconds() / 3600
    
    def is_within_work_hours(self, check_time=None):
        """Check if current time is within allowed work hours based on master settings"""
        from .utils import get_work_time_settings
        
        if not check_time:
            check_time = timezone.now().time()
        
        settings = get_work_time_settings()
        
        if self.work_nature == 'day':
            return settings['day_start'] <= check_time <= settings['day_end']
        elif self.work_nature == 'night':
            return check_time >= settings['night_start'] or check_time <= settings['night_end']
        else:  # both
            day_valid = settings['day_start'] <= check_time <= settings['day_end']
            night_valid = check_time >= settings['night_start'] or check_time <= settings['night_end']
            return day_valid or night_valid
    
    def get_work_hours_display(self):
        """Get human readable work hours from master settings"""
        from .utils import get_work_time_settings
        
        settings = get_work_time_settings()
        
        if self.work_nature == 'day':
            return f"Day Work: {settings['day_start'].strftime('%I:%M %p')} - {settings['day_end'].strftime('%I:%M %p')}"
        elif self.work_nature == 'night':
            return f"Night Work: {settings['night_start'].strftime('%I:%M %p')} - {settings['night_end'].strftime('%I:%M %p')}"
        else:
            return f"Day: {settings['day_start'].strftime('%I:%M %p')}-{settings['day_end'].strftime('%I:%M %p')}, Night: {settings['night_start'].strftime('%I:%M %p')}-{settings['night_end'].strftime('%I:%M %p')}"

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['permit_number']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['permit_type']),
        ]

class WorkflowTemplate(models.Model):
    name = models.CharField(max_length=100)
    permit_type = models.ForeignKey(PermitType, on_delete=models.CASCADE, related_name='workflow_templates')
    risk_level = models.CharField(max_length=10, choices=PermitType.RISK_LEVEL_CHOICES)
    steps = models.JSONField(default=list)
    auto_escalation = models.BooleanField(default=True)
    parallel_processing = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.permit_type.name}"

class WorkflowInstance(models.Model):
    permit = models.OneToOneField(Permit, on_delete=models.CASCADE, related_name='workflow')
    template = models.ForeignKey(WorkflowTemplate, on_delete=models.CASCADE, related_name='instances', null=True, blank=True)
    current_step = models.PositiveSmallIntegerField(default=0)
    status = models.CharField(max_length=20, default='active')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Workflow for {self.permit.permit_number}"

class WorkflowStep(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('skipped', 'Skipped'),
    ]
    
    workflow = models.ForeignKey(WorkflowInstance, on_delete=models.CASCADE, related_name='steps')
    step_id = models.CharField(max_length=50)
    name = models.CharField(max_length=100)
    step_type = models.CharField(max_length=20)  # approval, review, verification, notification
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='workflow_assignments')
    role = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    order = models.PositiveSmallIntegerField()
    escalation_time = models.PositiveSmallIntegerField(null=True, blank=True)  # hours
    required = models.BooleanField(default=True)
    conditions = models.JSONField(default=list, blank=True)
    
    # Action tracking
    completed_at = models.DateTimeField(null=True, blank=True)
    comments = models.TextField(blank=True)
    signature = models.TextField(blank=True)
    attachments = models.JSONField(default=list, blank=True)
    
    def __str__(self):
        return f"{self.name} - {self.workflow.permit.permit_number}"
    
    class Meta:
        ordering = ['order']
        unique_together = ['workflow', 'step_id']

class PermitExtension(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    permit = models.ForeignKey(Permit, on_delete=models.CASCADE, related_name='extensions')
    requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='requested_extensions')
    requested_at = models.DateTimeField(auto_now_add=True)
    original_end_time = models.DateTimeField()
    new_end_time = models.DateTimeField()
    extension_hours = models.PositiveIntegerField()
    reason = models.TextField()
    justification = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='approved_extensions')
    approved_at = models.DateTimeField(null=True, blank=True)
    comments = models.TextField(blank=True, null=True)
    
    # Work nature specific fields
    affects_work_nature = models.BooleanField(default=False)
    new_work_nature = models.CharField(max_length=10, choices=Permit.WORK_NATURE_CHOICES, blank=True)
    safety_reassessment_required = models.BooleanField(default=False)
    safety_reassessment_completed = models.BooleanField(default=False)
    additional_safety_measures = models.TextField(blank=True)
    
    def __str__(self):
        return f"Extension for {self.permit.permit_number} (+{self.extension_hours}h)"
    
    def save(self, *args, **kwargs):
        # Auto-calculate extension hours
        if self.original_end_time and self.new_end_time:
            self.extension_hours = int((self.new_end_time - self.original_end_time).total_seconds() / 3600)
        
        # Check if extension affects work nature (day to night or vice versa)
        if self.permit and self.new_end_time:
            original_nature = self.permit.work_nature
            # Logic to determine if extension crosses into different work hours
            self.affects_work_nature = self._check_work_nature_change()
            
        super().save(*args, **kwargs)
    
    def _check_work_nature_change(self):
        """Check if time extension changes work nature requirements"""
        # If extending beyond day work hours (6 PM) or before night work end (6 AM)
        end_time = self.new_end_time.time()
        
        if self.permit.work_nature == 'day':
            # Day work extending into night hours
            return end_time > self.permit.day_work_end or end_time < self.permit.night_work_end
        elif self.permit.work_nature == 'night':
            # Night work extending into day hours  
            return self.permit.day_work_start <= end_time <= self.permit.day_work_end
        
        return False

# Removed WorkTimeExtension model - time management handled centrally

class PermitWorker(models.Model):
    permit = models.ForeignKey(Permit, on_delete=models.CASCADE, related_name='assigned_workers')
    worker = models.ForeignKey('worker.Worker', on_delete=models.CASCADE, related_name='permit_assignments')
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='worker_assignments')
    assigned_at = models.DateTimeField(auto_now_add=True)
    role = models.CharField(max_length=50, blank=True)  # lead, assistant, observer
    competency_verified = models.BooleanField(default=False)
    training_valid = models.BooleanField(default=False)
    medical_clearance = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('permit', 'worker')
    
    def __str__(self):
        return f"{self.worker} assigned to {self.permit.permit_number}"

class HazardLibrary(models.Model):
    category = models.CharField(max_length=50)
    hazard_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    control_measures = models.JSONField(default=list)
    ppe_requirements = models.JSONField(default=list)
    risk_level = models.CharField(max_length=10, choices=PermitType.RISK_LEVEL_CHOICES)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.hazard_id} - {self.name}"
    
    class Meta:
        ordering = ['category', 'name']

class PermitHazard(models.Model):
    permit = models.ForeignKey(Permit, on_delete=models.CASCADE, related_name='identified_hazards')
    hazard = models.ForeignKey(HazardLibrary, on_delete=models.CASCADE, related_name='permit_instances')
    likelihood = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    severity = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    risk_score = models.PositiveSmallIntegerField()
    control_measures_applied = models.JSONField(default=list)
    residual_risk = models.PositiveSmallIntegerField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        self.risk_score = self.likelihood * self.severity
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.hazard.name} - {self.permit.permit_number}"

class GasReading(models.Model):
    GAS_TYPE_CHOICES = [
        ('O2', 'Oxygen'),
        ('CO', 'Carbon Monoxide'),
        ('H2S', 'Hydrogen Sulfide'),
        ('CH4', 'Methane'),
        ('CO2', 'Carbon Dioxide'),
        ('NH3', 'Ammonia'),
        ('Cl2', 'Chlorine'),
        ('SO2', 'Sulfur Dioxide'),
    ]
    
    permit = models.ForeignKey(Permit, on_delete=models.CASCADE, related_name='gas_readings')
    gas_type = models.CharField(max_length=10, choices=GAS_TYPE_CHOICES)
    reading = models.FloatField()
    unit = models.CharField(max_length=10)
    acceptable_range = models.CharField(max_length=50)
    status = models.CharField(max_length=10, choices=[('safe', 'Safe'), ('unsafe', 'Unsafe')])
    tested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='gas_tests')
    tested_at = models.DateTimeField(auto_now_add=True)
    equipment_used = models.CharField(max_length=100, blank=True)
    calibration_date = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.gas_type}: {self.reading}{self.unit} - {self.permit.permit_number}"
    
    class Meta:
        ordering = ['-tested_at']

class PermitPhoto(models.Model):
    PHOTO_TYPE_CHOICES = [
        ('before', 'Before Work'),
        ('during', 'During Work'),
        ('after', 'After Work'),
        ('incident', 'Incident'),
        ('equipment', 'Equipment'),
        ('ppe', 'PPE Verification'),
    ]
    
    permit = models.ForeignKey(Permit, on_delete=models.CASCADE, related_name='photos')
    photo = models.ImageField(upload_to='permit_photos/')
    photo_type = models.CharField(max_length=20, choices=PHOTO_TYPE_CHOICES)
    description = models.CharField(max_length=200, blank=True)
    taken_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='photos_taken')
    taken_at = models.DateTimeField(auto_now_add=True)
    gps_location = models.CharField(max_length=100, blank=True)
    offline_id = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"{self.photo_type} photo for {self.permit.permit_number}"
    
    class Meta:
        ordering = ['-taken_at']

class DigitalSignature(models.Model):
    SIGNATURE_TYPE_CHOICES = [
        ('issuer', 'Permit Issuer'),
        ('receiver', 'Permit Receiver'),
        ('approver', 'Approver'),
        ('safety_officer', 'Safety Officer'),
        ('area_manager', 'Area Manager'),
        ('witness', 'Witness'),
    ]
    
    permit = models.ForeignKey(Permit, on_delete=models.CASCADE, related_name='signatures')
    signature_type = models.CharField(max_length=20, choices=SIGNATURE_TYPE_CHOICES)
    signatory = models.ForeignKey(User, on_delete=models.CASCADE, related_name='signatures')
    signature_data = models.TextField()  # Base64 encoded signature
    signed_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    device_info = models.JSONField(default=dict, blank=True)
    
    def __str__(self):
        return f"{self.signature_type} signature by {self.signatory} for {self.permit.permit_number}"
    
    class Meta:
        unique_together = ['permit', 'signature_type', 'signatory']
        ordering = ['-signed_at']

class PermitAudit(models.Model):
    ACTION_CHOICES = [
        ('created', 'Created'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('activated', 'Activated'),
        ('suspended', 'Suspended'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('extended', 'Extended'),
        ('modified', 'Modified'),
        ('viewed', 'Viewed'),
        ('printed', 'Printed'),
        ('exported', 'Exported'),
    ]
    
    permit = models.ForeignKey(Permit, on_delete=models.CASCADE, related_name='audit_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    comments = models.TextField(blank=True, null=True)
    old_values = models.JSONField(default=dict, blank=True)
    new_values = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['permit', '-timestamp']),
            models.Index(fields=['action']),
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"{self.action} on {self.permit.permit_number} by {self.user}"

class PermitApproval(models.Model):
    ACTION_CHOICES = [
        ('approve', 'Approve'),
        ('reject', 'Reject'),
        ('request_changes', 'Request Changes'),
        ('delegate', 'Delegate'),
    ]
    
    permit = models.ForeignKey(Permit, on_delete=models.CASCADE, related_name='approvals')
    approver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='permit_approvals')
    approval_level = models.PositiveSmallIntegerField(default=1)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, null=True, blank=True)
    approved = models.BooleanField(null=True, blank=True)
    comments = models.TextField(blank=True, null=True)
    conditions = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    escalated_from = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='escalated_approvals')
    delegated_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='delegated_approvals')
    
    class Meta:
        ordering = ['approval_level', 'timestamp']
        unique_together = ['permit', 'approver', 'approval_level']
    
    def __str__(self):
        status = self.action or ("approved" if self.approved else "rejected" if self.approved is False else "pending")
        return f"Level {self.approval_level} {status} by {self.approver}"

class EscalationRule(models.Model):
    permit_type = models.ForeignKey(PermitType, on_delete=models.CASCADE, related_name='escalation_rules')
    step_name = models.CharField(max_length=100)
    time_limit_hours = models.PositiveIntegerField()
    escalate_to_role = models.CharField(max_length=50)
    notification_method = models.CharField(max_length=20, choices=[('email', 'Email'), ('sms', 'SMS'), ('both', 'Both')])
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.permit_type.name} - {self.step_name} escalation"

class NotificationTemplate(models.Model):
    TRIGGER_CHOICES = [
        ('permit_created', 'Permit Created'),
        ('approval_required', 'Approval Required'),
        ('permit_approved', 'Permit Approved'),
        ('permit_rejected', 'Permit Rejected'),
        ('permit_expired', 'Permit Expired'),
        ('escalation', 'Escalation'),
        ('reminder', 'Reminder'),
    ]
    
    name = models.CharField(max_length=100)
    trigger = models.CharField(max_length=30, choices=TRIGGER_CHOICES)
    subject = models.CharField(max_length=200)
    body = models.TextField()
    method = models.CharField(max_length=20, choices=[('email', 'Email'), ('sms', 'SMS'), ('push', 'Push'), ('all', 'All')])
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} - {self.trigger}"

class SystemIntegration(models.Model):
    INTEGRATION_TYPE_CHOICES = [
        ('erp', 'ERP System'),
        ('maintenance', 'Maintenance System'),
        ('safety', 'Safety System'),
        ('hr', 'HR System'),
        ('iot', 'IoT System'),
        ('notification', 'Notification System'),
        ('analytics', 'Analytics System'),
    ]
    
    STATUS_CHOICES = [
        ('connected', 'Connected'),
        ('disconnected', 'Disconnected'),
        ('error', 'Error'),
        ('syncing', 'Syncing'),
    ]
    
    name = models.CharField(max_length=100)
    integration_type = models.CharField(max_length=20, choices=INTEGRATION_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='disconnected')
    config = models.JSONField(default=dict)
    endpoints = models.JSONField(default=list)
    data_flow = models.CharField(max_length=20, choices=[('inbound', 'Inbound'), ('outbound', 'Outbound'), ('bidirectional', 'Bidirectional')])
    last_sync = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} - {self.integration_type}"

class ComplianceReport(models.Model):
    REPORT_TYPE_CHOICES = [
        ('daily', 'Daily Report'),
        ('weekly', 'Weekly Report'),
        ('monthly', 'Monthly Report'),
        ('audit', 'Audit Report'),
        ('incident', 'Incident Report'),
    ]
    
    name = models.CharField(max_length=100)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='generated_reports')
    generated_at = models.DateTimeField(auto_now_add=True)
    date_from = models.DateTimeField()
    date_to = models.DateTimeField()
    data = models.JSONField(default=dict)
    file_path = models.CharField(max_length=500, blank=True)
    
    def __str__(self):
        return f"{self.name} - {self.generated_at.strftime('%Y-%m-%d')}"

# Signals for audit trail and workflow management
@receiver(pre_save, sender=Permit)
def store_original_permit_data(sender, instance, **kwargs):
    if instance.pk:
        try:
            original = Permit.objects.get(pk=instance.pk)
            instance._original_status = original.status
            instance._original_data = {
                'status': original.status,
                'risk_score': original.risk_score,
                'risk_level': original.risk_level,
                'planned_start_time': original.planned_start_time.isoformat() if original.planned_start_time else None,
                'planned_end_time': original.planned_end_time.isoformat() if original.planned_end_time else None,
                'work_nature': original.work_nature,
            }
        except Permit.DoesNotExist:
            instance._original_status = None
            instance._original_data = {}
    else:
        instance._original_status = None
        instance._original_data = {}
    
    # Auto-calculate risk score
    instance.calculate_risk_score()
    
    # Generate permit number if not provided
    if not instance.permit_number:
        from datetime import datetime, time
        year = datetime.now().year
        count = Permit.objects.filter(created_at__year=year).count() + 1
        instance.permit_number = f"PTW-{year}-{count:06d}"
    
    # Generate QR code data (actual QR image will be generated on demand)
    if not instance.qr_code and instance.pk:
        from .qr_utils import generate_permit_qr_data
        instance.qr_code = generate_permit_qr_data(instance)

@receiver(post_save, sender=Permit)
def create_audit_log(sender, instance, created, **kwargs):
    user = getattr(instance, '_current_user', None)
    
    if created:
        PermitAudit.objects.create(
            permit=instance,
            action='created',
            user=user,
            comments=f"Permit {instance.permit_number} created",
            new_values={
                'status': instance.status,
                'permit_type': instance.permit_type.name if instance.permit_type else None,
                'location': instance.location,
            }
        )
    else:
        # Track status changes
        if hasattr(instance, '_original_status') and instance._original_status != instance.status:
            PermitAudit.objects.create(
                permit=instance,
                action=instance.status,
                user=user,
                comments=f"Status changed from {instance._original_status} to {instance.status}",
                old_values={'status': instance._original_status},
                new_values={'status': instance.status}
            )

@receiver(post_save, sender=WorkflowStep)
def handle_workflow_step_completion(sender, instance, created, **kwargs):
    if not created and instance.status in ['approved', 'completed']:
        # Check if all required steps are completed
        workflow = instance.workflow
        required_steps = workflow.steps.filter(required=True)
        completed_steps = required_steps.filter(status__in=['approved', 'completed'])
        
        if required_steps.count() == completed_steps.count():
            # All required steps completed, approve permit
            permit = workflow.permit
            if permit.can_transition_to('approved'):
                permit.status = 'approved'
                permit.approved_at = timezone.now()
                permit.save()

@receiver(pre_save, sender=PermitExtension)
def store_original_extension_status(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._original_status = PermitExtension.objects.get(pk=instance.pk).status
        except PermitExtension.DoesNotExist:
            instance._original_status = None
    else:
        instance._original_status = None
    
    # Calculate extension hours
    if instance.original_end_time and instance.new_end_time:
        instance.extension_hours = int((instance.new_end_time - instance.original_end_time).total_seconds() / 3600)

# Removed time extension signal handlers