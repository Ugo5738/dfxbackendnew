from rest_framework import serializers

from account import models


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Profile
        # fields = '__all__'
        fields = ['country']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=128, min_length=6, write_only=True)
    profile = ProfileSerializer()

    class Meta:
        model = models.User
        # fields = '__all__'
        # fields = ['id', 'name', 'email', 'password']
        exclude = ['groups', 'user_permissions']

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        user = models.User.objects.create_user(**validated_data)
        models.Profile.objects.create(user=user, **profile_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    user_role = serializers.CharField(source='get_user_role', read_only=True)
    
    class Meta:
        model = models.User
        # fields = '__all__'
        exclude = ["password", "phone_verified", 'groups', 'user_permissions']


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class ResetPasswordRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()