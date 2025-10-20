from django.db import migrations, models
from django.db.models import Q
import django.db.models.deletion


def fill_missing_phone(apps, schema_editor):
    User = apps.get_model('naalikeraapp', 'CustomUser')
    for user in User.objects.filter(Q(phone__isnull=True) | Q(phone='')):
        placeholder = f"999{user.id:012d}"[-15:]
        user.phone = placeholder
        user.save(update_fields=['phone'])


def assign_user_to_otp(apps, schema_editor):
    OTP = apps.get_model('naalikeraapp', 'OTP')
    CustomUser = apps.get_model('naalikeraapp', 'CustomUser')
    for otp in OTP.objects.filter(user__isnull=True):
        user = CustomUser.objects.filter(phone=otp.phone).first()
        if user:
            otp.user = user
            otp.save(update_fields=['user'])


class Migration(migrations.Migration):

    dependencies = [
        ('naalikeraapp', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(fill_missing_phone, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='customuser',
            name='phone',
            field=models.CharField(max_length=15, unique=True),
        ),
        migrations.AddField(
            model_name='otp',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='otps', to='naalikeraapp.customuser'),
        ),
        migrations.AddField(
            model_name='otp',
            name='purpose',
            field=models.CharField(choices=[('registration', 'Registration'), ('login', 'Login'), ('password_reset', 'Password Reset')], default='registration', max_length=20),
        ),
        migrations.AddField(
            model_name='otp',
            name='session_token',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='otp',
            name='is_used',
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(assign_user_to_otp, migrations.RunPython.noop),
    ]
