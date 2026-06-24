# не используется в итоге

# from rest_framework import serializers

# from models import User, Role


# class RoleSerializer(serializers.ModelSerializer):
#     """Сериализатор роли пользователя"""
#     class Meta:
#         model = Role
#         fields = ('id', 'name')


# class UserCreateSerializer(serializers.ModelSerializer):
#     """ Сериализатор для передачи данных для создания пользователя."""
#     login = serializers.CharField(source='username')

#     class Meta:
#         model = User
#         fields = ('full_name', 'email', 'login', 'role_id')


# class UserResponseSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ('id', 'full_name', 'role')


# class UserLoginSerializer(serializers.ModelSerializer):
#     """ Сериализатор для входа в аккаунт."""
#     password = serializers.CharField(
#         write_only=True,
#         required=True,
#         style={'input_type': 'password'}
#     )

#     class Meta:
#         model = User
#         fields = ('login', 'password')


# class LoginResponseSerializer(serializers.ModelSerializer):
#     """ Сериализатор ответа при входе в аккаунт"""
#     access_token
#     refreshToken
#     user = serializers.

#     class Meta:
#         model = User
#         fields = ('id', 'full_name', 'role_id')