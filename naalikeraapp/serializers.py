from rest_framework import serializers
from .models import CustomUser, OTP
from django.contrib.auth import authenticate

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    phone = serializers.CharField(required=True, allow_blank=False)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone', 'user_type', 'password']

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user

    def validate_phone(self, value):
        if value is None:
            raise serializers.ValidationError('Phone number is required')
        value = value.strip()
        if not value:
            raise serializers.ValidationError('Phone number is required')
        return value

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if not user or not user.is_active:
            raise serializers.ValidationError("Invalid credentials")
        if not user.phone:
            raise serializers.ValidationError("Phone number not set for this account")
        return {'user': user}
    
class LoginOTPConfirmSerializer(serializers.Serializer):
    username = serializers.CharField()
    otp = serializers.CharField()
    session_token = serializers.CharField()

    def validate(self, data):
        try:
            user = CustomUser.objects.get(username=data['username'])
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("User not found")

        otp_qs = OTP.objects.filter(
            user=user,
            purpose=OTP.PURPOSE_LOGIN,
            session_token=data['session_token']
        ).order_by('-created_at')

        otp_obj = otp_qs.first()
        if not otp_obj or otp_obj.otp != data['otp']:
            raise serializers.ValidationError("Invalid OTP")
        if otp_obj.is_expired():
            raise serializers.ValidationError("OTP expired")

        data['user'] = user
        data['otp_obj'] = otp_obj
        return data

class VerifyOTPSerializer(serializers.Serializer):
    phone = serializers.CharField()
    otp = serializers.CharField()
    purpose = serializers.ChoiceField(choices=OTP.PURPOSE_CHOICES, default=OTP.PURPOSE_REGISTRATION)
    session_token = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        purpose = data.get('purpose', OTP.PURPOSE_REGISTRATION)
        session_token = data.get('session_token')
        otp_qs = OTP.objects.filter(
            phone=data['phone'],
            otp=data['otp'],
            purpose=purpose
        )
        if session_token:
            otp_qs = otp_qs.filter(session_token=session_token)

        otp_obj = otp_qs.order_by('-created_at').first()
        if not otp_obj:
            raise serializers.ValidationError("Invalid OTP")
        if otp_obj.is_expired():
            raise serializers.ValidationError("OTP expired")

        user = otp_obj.user or CustomUser.objects.filter(phone=data['phone']).first()
        data['user'] = user
        data['otp_obj'] = otp_obj
        return data

class ForgotPasswordSerializer(serializers.Serializer):
    phone = serializers.CharField()

    def validate(self, data):
        user = CustomUser.objects.filter(phone=data['phone']).first()
        if not user:
            raise serializers.ValidationError("Phone number not registered")
        # Generate OTP or something
        return {'message': 'OTP sent'}