# Generated by Django 4.2.19 on 2025-02-20 16:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_dish_remove_order_items_alter_order_total_price_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='dishes',
        ),
        migrations.DeleteModel(
            name='Dish',
        ),
        migrations.AddField(
            model_name='order',
            name='dishes',
            field=models.JSONField(default=list, help_text='Список ID блюд из JSON (например, [1, 2])', verbose_name='Блюда'),
        ),
    ]
