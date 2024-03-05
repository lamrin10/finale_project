# Generated by Django 5.0.2 on 2024-03-04 12:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0017_book_alter_comment_id_alter_follower_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='sentiment',
            field=models.CharField(choices=[('Positive', 'positive'), ('Negative', 'negative')], default='Positive', max_length=10),
            preserve_default=False,
        ),
    ]
