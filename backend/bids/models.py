from django.conf import settings
from django.db import models


class BidPlatform(models.Model):
    name = models.CharField(max_length=100, unique=True)
    value = models.SlugField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name


class BidProfile(models.Model):
    name = models.CharField(max_length=100, unique=True)
    value = models.SlugField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name


class Bid(models.Model):
    PLATFORM_UPWORK = "upwork"
    PLATFORM_FREELANCER = "freelancer"
    PLATFORM_CHOICES = (
        (PLATFORM_UPWORK, "Upwork"),
        (PLATFORM_FREELANCER, "Freelancer"),
    )

    STATUS_PENDING = "pending"
    STATUS_REPLY = "reply"
    STATUS_CALL = "call"
    STATUS_CLOSED = "closed"
    STATUS_CHOICES = (
        (STATUS_PENDING, "Pending"),
        (STATUS_REPLY, "Reply"),
        (STATUS_CALL, "Call"),
        (STATUS_CLOSED, "Closed"),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bids")
    platform = models.CharField(max_length=100)
    profile = models.CharField(max_length=100)
    job_link = models.URLField()
    connects = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    is_dummy = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email} - {self.platform} - {self.status}"
