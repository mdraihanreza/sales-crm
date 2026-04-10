from django.urls import path

from .views import AdminReportPDFView, AdminReportView, BidCreateView, BidDetailView, BidOptionsView, KPIView, MyBidsView

urlpatterns = [
    path("bids/", BidCreateView.as_view(), name="bid-create"),
    path("bids/<int:pk>/", BidDetailView.as_view(), name="bid-detail"),
    path("bids/my/", MyBidsView.as_view(), name="my-bids"),
    path("bid-options/", BidOptionsView.as_view(), name="bid-options"),
    path("kpi/", KPIView.as_view(), name="kpi"),
    path("admin/report/", AdminReportView.as_view(), name="admin-report"),
    path("admin/report/pdf/", AdminReportPDFView.as_view(), name="admin-report-pdf"),
]
