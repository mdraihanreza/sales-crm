from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Bid",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("platform", models.CharField(choices=[("upwork", "Upwork"), ("freelancer", "Freelancer")], max_length=20)),
                ("profile", models.CharField(max_length=100)),
                ("job_link", models.URLField()),
                ("connects", models.PositiveIntegerField()),
                ("status", models.CharField(choices=[("pending", "Pending"), ("reply", "Reply"), ("call", "Call"), ("closed", "Closed")], default="pending", max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="bids", to="users.user")),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]
