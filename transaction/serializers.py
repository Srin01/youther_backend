from dataclasses import fields
from rest_framework import serializers
from core.models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for object transaction"""

    class Meta:
        model = Transaction
        fields = ('transactionamount','transactionresult','user_idbuyer','user_idseller','post')