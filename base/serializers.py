from rest_framework import serializers
from .models import Credit, User


class CreditSerializer(serializers.ModelSerializer):
    username = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='user.username', required=False)
    first_name = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='user.first_name', required=False)
    last_name = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='user.last_name', required=False)
    employee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='user.employee_id', required=False)

    class Meta:
        model = Credit
        fields = ['username', 'first_name', 'last_name', 'employee_id', 'owner_point',
                  'reuse_point', 'total_point', 'description', 'created_at', 'updated_at']
