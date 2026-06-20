from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='BudgetScenario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=180)),
                ('period', models.CharField(max_length=64)),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='BudgetLineItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('department', models.CharField(max_length=120)),
                ('category', models.CharField(max_length=120)),
                ('budget_amount', models.DecimalField(decimal_places=2, max_digits=14)),
                ('actual_amount', models.DecimalField(decimal_places=2, max_digits=14)),
                ('notes', models.TextField(blank=True)),
                ('risk_rating', models.CharField(blank=True, max_length=32)),
                ('scenario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='line_items', to='api.BudgetScenario')),
            ],
        ),
    ]
