from rest_framework import serializers

from .models import Bid, BidPlatform, BidProfile


class BidOptionSerializer(serializers.Serializer):
    name = serializers.CharField()
    value = serializers.CharField()


class BidSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.name", read_only=True)
    user_email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = Bid
        fields = (
            "id",
            "user",
            "user_name",
            "user_email",
            "platform",
            "profile",
            "job_link",
            "connects",
            "status",
            "created_at",
        )
        read_only_fields = ("id", "user", "user_name", "user_email", "created_at")

    def validate_platform(self, value):
        if not BidPlatform.objects.filter(value=value, is_active=True).exists():
            raise serializers.ValidationError("Select a valid active platform.")
        return value

    def validate_profile(self, value):
        if not BidProfile.objects.filter(value=value, is_active=True).exists():
            raise serializers.ValidationError("Select a valid active profile.")
        return value


class AdminReportQuerySerializer(serializers.Serializer):
    GROUP_BY_DAY = "day"
    GROUP_BY_WEEK = "week"
    GROUP_BY_MONTH = "month"
    GROUP_BY_CHOICES = (
        (GROUP_BY_DAY, "Daily"),
        (GROUP_BY_WEEK, "Weekly"),
        (GROUP_BY_MONTH, "Monthly"),
    )

    user_id = serializers.IntegerField(required=False)
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    group_by = serializers.ChoiceField(choices=GROUP_BY_CHOICES, default=GROUP_BY_DAY)

    def validate(self, attrs):
        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date")

        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError("start_date cannot be later than end_date.")

        return attrs


class ReportSummarySerializer(serializers.Serializer):
    total_bids = serializers.IntegerField()
    total_connects = serializers.IntegerField()
    replies = serializers.IntegerField()
    calls = serializers.IntegerField()
    closed = serializers.IntegerField()


class ReportPeriodSerializer(serializers.Serializer):
    period = serializers.CharField()
    total_bids = serializers.IntegerField()
    total_connects = serializers.IntegerField()
    replies = serializers.IntegerField()
    calls = serializers.IntegerField()
    closed = serializers.IntegerField()


class AdminReportResponseSerializer(serializers.Serializer):
    user = serializers.DictField()
    filters = serializers.DictField()
    summary = ReportSummarySerializer()
    data = ReportPeriodSerializer(many=True)
