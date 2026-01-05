from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "email", "is_pro", "pro_expiry_date"]
        read_only_fields = ["is_pro", "pro_expiry_date"]
