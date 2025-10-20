from rest_framework import serializers
from .models import CustomUser, OTP
from django.contrib.auth import authenticate

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone', 'user_type', 'password']

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if user and user.is_active:
            return {'user': user}
        raise serializers.ValidationError("Invalid credentials")

class VerifyOTPSerializer(serializers.Serializer):
    phone = serializers.CharField()
    otp = serializers.CharField()

    def validate(self, data):
        try:
            otp_obj = OTP.objects.filter(phone=data['phone'], otp=data['otp']).latest('created_at')
            if otp_obj.is_expired():
                raise serializers.ValidationError("OTP expired")
            user = CustomUser.objects.filter(phone=data['phone']).first()
            return {'user': user}
        except OTP.DoesNotExist:
            raise serializers.ValidationError("Invalid OTP")

class ForgotPasswordSerializer(serializers.Serializer):
    phone = serializers.CharField()

    def validate(self, data):
        user = CustomUser.objects.filter(phone=data['phone']).first()
        if not user:
            raise serializers.ValidationError("Phone number not registered")
        # Generate OTP or something
        return {'message': 'OTP sent'}