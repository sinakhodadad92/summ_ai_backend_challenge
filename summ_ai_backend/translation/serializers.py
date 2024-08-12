from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Translation

class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Handles creating a new User instance with the provided username, email, and password.
    """
    class Meta:
        model = User
        fields = ['username', 'password', 'email']
        extra_kwargs = {'password': {'write_only': True}}  

    def create(self, validated_data):
        """
        Create a new user with the validated data.
        
        Args:
            validated_data (dict): The validated data for creating a user.
        
        Returns:
            User: The newly created user instance.
        """
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.
    Provides convertion of User instances to and from JSON format.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email']  

class TranslationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Translation model.
    Handles serialization and deserialization of Translation instances.
    """
    class Meta:
        model = Translation
        fields = ['id', 'user', 'original_text', 'translated_text', 'content_type', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']  
