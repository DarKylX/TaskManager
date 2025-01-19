from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = get_user_model()
        fields = (
            "username",
            "password",
            "password2",
            "email",
            "first_name",
            "last_name",
        )
        extra_kwargs = {
            "first_name": {"required": False},
            "last_name": {"required": False},
        }

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Пароли не совпадают"})

        email = attrs.get("email")
        if get_user_model().objects.filter(email=email).exists():
            raise serializers.ValidationError(
                {"email": "Пользователь с таким email уже существует"}
            )

        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        user = get_user_model().objects.create_user(**validated_data)
        user.is_active = True  # Устанавливаем пользователя активным сразу
        user.save()
        return user
