from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import Users, Roles
from django.contrib.auth.hashers import check_password
class UserSerializer(serializers.ModelSerializer):
    # Thêm trường role_id, nếu không được cung cấp sẽ mặc định là 2
    role_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Users
        fields = ['user_name', 'passwordhash', 'fullname', 'birthday', 'email', 'phone', 'image_user', 'role_id']
        extra_kwargs = {
            'passwordhash': {'write_only': True}
        }
    
    def create(self, validated_data):
        # Lấy role_id nếu có, ngược lại mặc định là 2
        role_id = validated_data.pop('role_id', 2)
        # Mã hóa mật khẩu trước khi lưu
        validated_data['passwordhash'] = make_password(validated_data['passwordhash'])
        # Lấy instance của Roles dựa trên role_id
        try:
            role_instance = Roles.objects.get(pk=role_id)
        except Roles.DoesNotExist:
            raise serializers.ValidationError(f"Role với role_id={role_id} không tồn tại.")
        validated_data['role'] = role_instance
        return super(UserSerializer, self).create(validated_data)
class LoginSerializer(serializers.Serializer):
    user_name = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user_name = data.get('user_name')
        password = data.get('password')

        try:
            user = Users.objects.get(user_name=user_name)
        except Users.DoesNotExist:
            raise serializers.ValidationError("Người dùng không tồn tại.")

        if not check_password(password, user.passwordhash):
            raise serializers.ValidationError("Mật khẩu không đúng.")

        data['user'] = user
        return data
