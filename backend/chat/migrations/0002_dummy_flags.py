from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("chat", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="chatroom",
            name="is_dummy",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="chatparticipant",
            name="is_dummy",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="mention",
            name="is_dummy",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="message",
            name="is_dummy",
            field=models.BooleanField(default=False),
        ),
    ]
