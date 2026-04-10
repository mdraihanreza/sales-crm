from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ChatRoom",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(blank=True, max_length=255)),
                ("is_group", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("created_by", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="created_chat_rooms", to="users.user")),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="Message",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("content", models.TextField()),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                ("is_read", models.BooleanField(default=False)),
                ("room", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="messages", to="chat.chatroom")),
                ("sender", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="sent_messages", to="users.user")),
            ],
            options={"ordering": ["timestamp"]},
        ),
        migrations.CreateModel(
            name="ChatParticipant",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("joined_at", models.DateTimeField(auto_now_add=True)),
                ("last_read_at", models.DateTimeField(blank=True, null=True)),
                ("room", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="participants", to="chat.chatroom")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="chat_participations", to="users.user")),
            ],
            options={"ordering": ["joined_at"], "unique_together": {("user", "room")}},
        ),
        migrations.CreateModel(
            name="Mention",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("is_resolved", models.BooleanField(default=False)),
                ("mentioned_user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="mentions", to="users.user")),
                ("message", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="mentions", to="chat.message")),
            ],
            options={"unique_together": {("message", "mentioned_user")}},
        ),
    ]
