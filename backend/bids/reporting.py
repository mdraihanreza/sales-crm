from datetime import datetime, time

from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncDay, TruncMonth, TruncWeek
from django.http import Http404
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from users.models import User

from .models import Bid


GROUP_BY_TRUNC_MAP = {
    "day": TruncDay,
    "week": TruncWeek,
    "month": TruncMonth,
}


def get_report_user(user_id):
    if not user_id:
        return None
    try:
        return User.objects.get(pk=user_id)
    except User.DoesNotExist as exc:
        raise Http404("Selected user does not exist.") from exc


def build_report_queryset(*, user_id=None, start_date=None, end_date=None):
    queryset = Bid.objects.select_related("user").all()

    if user_id:
        queryset = queryset.filter(user_id=user_id)

    if start_date:
        start_value = timezone.make_aware(datetime.combine(start_date, time.min))
        queryset = queryset.filter(created_at__gte=start_value)

    if end_date:
        end_value = timezone.make_aware(datetime.combine(end_date, time.max))
        queryset = queryset.filter(created_at__lte=end_value)

    return queryset


def build_summary(queryset):
    aggregate = queryset.aggregate(
        total_bids=Count("id"),
        total_connects=Sum("connects"),
        replies=Count("id", filter=Q(status=Bid.STATUS_REPLY)),
        calls=Count("id", filter=Q(status=Bid.STATUS_CALL)),
        closed=Count("id", filter=Q(status=Bid.STATUS_CLOSED)),
    )

    return {
        "total_bids": aggregate["total_bids"] or 0,
        "total_connects": aggregate["total_connects"] or 0,
        "replies": aggregate["replies"] or 0,
        "calls": aggregate["calls"] or 0,
        "closed": aggregate["closed"] or 0,
    }


def build_period_data(queryset, group_by):
    trunc_function = GROUP_BY_TRUNC_MAP[group_by]
    grouped = (
        queryset.annotate(period_value=trunc_function("created_at"))
        .values("period_value")
        .annotate(
            total_bids=Count("id"),
            total_connects=Sum("connects"),
            replies=Count("id", filter=Q(status=Bid.STATUS_REPLY)),
            calls=Count("id", filter=Q(status=Bid.STATUS_CALL)),
            closed=Count("id", filter=Q(status=Bid.STATUS_CLOSED)),
        )
        .order_by("period_value")
    )

    return [
        {
            "period": entry["period_value"].date().isoformat(),
            "total_bids": entry["total_bids"] or 0,
            "total_connects": entry["total_connects"] or 0,
            "replies": entry["replies"] or 0,
            "calls": entry["calls"] or 0,
            "closed": entry["closed"] or 0,
        }
        for entry in grouped
    ]


def build_report_payload(*, user_id=None, start_date=None, end_date=None, group_by="day"):
    report_user = get_report_user(user_id)
    queryset = build_report_queryset(user_id=user_id, start_date=start_date, end_date=end_date)

    return {
        "user": {
            "id": report_user.id if report_user else None,
            "name": report_user.name if report_user else "All users",
            "email": report_user.email if report_user else None,
        },
        "filters": {
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
            "group_by": group_by,
        },
        "summary": build_summary(queryset),
        "data": build_period_data(queryset, group_by),
    }


def generate_report_pdf(buffer, payload):
    document = SimpleDocTemplate(buffer, pagesize=A4, title="Sales CRM Report")
    styles = getSampleStyleSheet()
    story = [
        Paragraph("Sales CRM Admin Report", styles["Title"]),
        Spacer(1, 12),
        Paragraph(f"User: {payload['user']['name']}", styles["Normal"]),
        Paragraph(
            f"Date range: {payload['filters']['start_date'] or 'Beginning'} to {payload['filters']['end_date'] or 'Today'}",
            styles["Normal"],
        ),
        Paragraph(f"Grouped by: {payload['filters']['group_by'].title()}", styles["Normal"]),
        Spacer(1, 16),
        Paragraph("Summary Metrics", styles["Heading2"]),
        Spacer(1, 8),
    ]

    summary_table = Table(
        [
            ["Metric", "Value"],
            ["Total Bids", payload["summary"]["total_bids"]],
            ["Total Connects", payload["summary"]["total_connects"]],
            ["Replies", payload["summary"]["replies"]],
            ["Calls", payload["summary"]["calls"]],
            ["Closed", payload["summary"]["closed"]],
        ],
        hAlign="LEFT",
    )
    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f766e")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.HexColor("#f8fafc")]),
            ]
        )
    )
    story.extend([summary_table, Spacer(1, 18), Paragraph("Period Breakdown", styles["Heading2"]), Spacer(1, 8)])

    period_rows = [["Period", "Bids", "Connects", "Replies", "Calls", "Closed"]]
    for row in payload["data"]:
        period_rows.append(
            [row["period"], row["total_bids"], row["total_connects"], row["replies"], row["calls"], row["closed"]]
        )

    if len(period_rows) == 1:
        period_rows.append(["No data", 0, 0, 0, 0, 0])

    period_table = Table(period_rows, hAlign="LEFT")
    period_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563eb")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#eff6ff")]),
            ]
        )
    )
    story.append(period_table)
    document.build(story)
