from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import LeadStatus
from .serializers import LeadStatusSerializer


class LeadStatusListCreateView(generics.ListCreateAPIView):
    serializer_class = LeadStatusSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        queryset = LeadStatus.objects.select_related("created_by", "last_updated_by")
        include_archived = self.request.query_params.get("include_archived") == "true"
        if not include_archived:
            queryset = queryset.filter(is_archived=False)
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, last_updated_by=self.request.user)


class LeadStatusDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LeadStatusSerializer
    permission_classes = [IsAuthenticated]
    queryset = LeadStatus.objects.select_related("created_by", "last_updated_by")
    http_method_names = ["get", "patch", "delete", "head", "options"]

    def perform_update(self, serializer):
        serializer.save(last_updated_by=self.request.user)


class LeadStatusArchiveView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        lead = generics.get_object_or_404(LeadStatus, pk=pk)
        lead.is_archived = True
        lead.last_updated_by = request.user
        lead.save(update_fields=["is_archived", "last_updated_by", "updated_at"])
        return Response(LeadStatusSerializer(lead).data, status=status.HTTP_200_OK)


class LeadStatusUnarchiveView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        lead = generics.get_object_or_404(LeadStatus, pk=pk)
        lead.is_archived = False
        lead.last_updated_by = request.user
        lead.save(update_fields=["is_archived", "last_updated_by", "updated_at"])
        return Response(LeadStatusSerializer(lead).data, status=status.HTTP_200_OK)
