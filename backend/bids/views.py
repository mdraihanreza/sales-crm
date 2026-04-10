from io import BytesIO

from django.db.models import Count, Q, Sum
from django.http import FileResponse
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User
from users.permissions import IsAdminUserRole

from .models import Bid
from .models import BidPlatform, BidProfile
from .pagination import BidActivityPagination
from .reporting import build_report_payload, generate_report_pdf
from .serializers import AdminReportQuerySerializer, AdminReportResponseSerializer, BidOptionSerializer, BidSerializer


class BidCreateView(generics.CreateAPIView):
    serializer_class = BidSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BidOptionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        platforms = BidPlatform.objects.filter(is_active=True)
        profiles = BidProfile.objects.filter(is_active=True)
        return Response(
            {
                "platforms": BidOptionSerializer(platforms, many=True).data,
                "profiles": BidOptionSerializer(profiles, many=True).data,
            }
        )


class BidDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BidSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "patch", "delete", "head", "options"]

    def get_queryset(self):
        queryset = Bid.objects.select_related("user")
        if self.request.user.role == User.ROLE_ADMIN:
            return queryset
        return queryset.filter(user=self.request.user)


class MyBidsView(generics.ListAPIView):
    serializer_class = BidSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = BidActivityPagination

    def get_queryset(self):
        queryset = Bid.objects.select_related("user")
        user = self.request.user

        if user.role != User.ROLE_ADMIN:
            queryset = queryset.filter(user=user)
        else:
            user_id = self.request.query_params.get("user_id")
            if user_id:
                queryset = queryset.filter(user_id=user_id)

        platform = self.request.query_params.get("platform")
        if platform:
            queryset = queryset.filter(platform=platform)

        status = self.request.query_params.get("status")
        if status:
            queryset = queryset.filter(status=status)

        start_date = self.request.query_params.get("start_date")
        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)

        end_date = self.request.query_params.get("end_date")
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)

        return queryset


class KPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = Bid.objects.all()
        if request.user.role != User.ROLE_ADMIN:
            queryset = queryset.filter(user=request.user)

        aggregate = queryset.aggregate(
            total_bids=Count("id"),
            total_connects=Sum("connects"),
            replies=Count("id", filter=Q(status=Bid.STATUS_REPLY)),
            calls=Count("id", filter=Q(status=Bid.STATUS_CALL)),
            closed=Count("id", filter=Q(status=Bid.STATUS_CLOSED)),
        )

        return Response(
            {
                "total_bids": aggregate["total_bids"] or 0,
                "total_connects": aggregate["total_connects"] or 0,
                "replies": aggregate["replies"] or 0,
                "calls": aggregate["calls"] or 0,
                "closed": aggregate["closed"] or 0,
            }
        )


class AdminReportView(APIView):
    permission_classes = [IsAdminUserRole]

    def get(self, request):
        serializer = AdminReportQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        payload = build_report_payload(**serializer.validated_data)
        response_serializer = AdminReportResponseSerializer(payload)
        return Response(response_serializer.data)


class AdminReportPDFView(APIView):
    permission_classes = [IsAdminUserRole]

    def get(self, request):
        serializer = AdminReportQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        payload = build_report_payload(**serializer.validated_data)

        buffer = BytesIO()
        generate_report_pdf(buffer, payload)
        buffer.seek(0)

        filename = f"sales-crm-report-{payload['filters']['group_by']}.pdf"
        return FileResponse(buffer, as_attachment=True, filename=filename, content_type="application/pdf")
