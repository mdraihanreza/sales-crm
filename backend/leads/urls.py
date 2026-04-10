from django.urls import path

from .views import LeadStatusArchiveView, LeadStatusDetailView, LeadStatusListCreateView, LeadStatusUnarchiveView

urlpatterns = [
    path("leads/status/", LeadStatusListCreateView.as_view(), name="lead-status-list-create"),
    path("leads/status/<int:pk>/", LeadStatusDetailView.as_view(), name="lead-status-detail"),
    path("leads/status/<int:pk>/archive/", LeadStatusArchiveView.as_view(), name="lead-status-archive"),
    path("leads/status/<int:pk>/unarchive/", LeadStatusUnarchiveView.as_view(), name="lead-status-unarchive"),
]
