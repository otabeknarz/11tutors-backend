from rest_framework import serializers

from users.models import User, OnboardingAnswer


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, allow_blank=True)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'password',
            'role',
            'is_email_verified',
            'created_at',
            'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'is_email_verified', 'role')

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data.get('password'))
        user.save()
        return user


class TutorSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        pass

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data.get('password'))
        user.role = User.RoleChoices.TUTOR
        user.save()
        return user


class StatisticsSerializer(serializers.ModelSerializer):
    number_of_payments = serializers.SerializerMethodField()
    number_of_completed_payments = serializers.SerializerMethodField()
    number_of_failed_payments = serializers.SerializerMethodField()
    number_of_pending_payments = serializers.SerializerMethodField()
    total_amount_of_completed_payments = serializers.SerializerMethodField()
    average_monthly_amount_of_completed_payments = serializers.SerializerMethodField()

    number_of_courses = serializers.SerializerMethodField()
    number_of_course_parts = serializers.SerializerMethodField()
    number_of_lessons = serializers.SerializerMethodField()

    class Meta:
        pass


class OnboardingAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnboardingAnswer
        fields = "__all__"
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')
