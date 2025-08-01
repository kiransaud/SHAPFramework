# Generated by Django 5.1.7 on 2025-06-05 13:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Frontend', '0005_studysession_scenarioresponse'),
    ]

    operations = [
        migrations.AddField(
            model_name='scenarioresponse',
            name='is_correct',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='scenarioresponse',
            name='confidence',
            field=models.PositiveSmallIntegerField(help_text='User’s confidence rating (1=not confident … 7=very confident).'),
        ),
        migrations.AlterField(
            model_name='scenarioresponse',
            name='decision_key',
            field=models.CharField(help_text="Which choice the user clicked (e.g. 'immediate', 'algorithm', 'scaling', etc.)", max_length=50),
        ),
        migrations.AlterField(
            model_name='scenarioresponse',
            name='scenario_number',
            field=models.PositiveSmallIntegerField(help_text='1..6; 1–3 = first block, 4–6 = second block.'),
        ),
        migrations.AlterField(
            model_name='studysession',
            name='order',
            field=models.CharField(choices=[('A_first', 'Baseline first → then SHAP'), ('B_first', 'SHAP first → then Baseline')], help_text='A_first: scenarios 1–3 are Baseline (no SHAP) and 4–6 are SHAP.\nB_first: scenarios 1–3 are SHAP and 4–6 are Baseline.', max_length=10),
        ),
    ]
