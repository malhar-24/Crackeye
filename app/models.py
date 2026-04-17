from django.db import models






class DamageReport(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    # store full AI output
    data = models.JSONField()
    status = models.CharField(max_length=20, default="pending")  # 🔥 ADD THIS
    pdf = models.CharField(max_length=255, null=True, blank=True)
    # optional quick access fields (recommended)
    damage_type = models.CharField(max_length=50, null=True, blank=True)
    location = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.damage_type} - {self.created_at}"