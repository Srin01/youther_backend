from django.http import HttpRequest
from django.shortcuts import render
from core.models import Transaction
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework import permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404, redirect
from transaction.serializers import TransactionSerializer

# Create your views here.
class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    queryset = Transaction.objects.all()
    permission_classes = (permissions.AllowAny,)

    def perform_create(self, serializer):
        serializer.save()


# class CreateTransaction(APIView):
#     renderer_classes = [TemplateHTMLRenderer]
#     template_name = 'transaction_list.html'

#     def get(self, request):
#         queryset = Transaction.objects.all()
#         return Response({'profiles': queryset})

#     def post(self, request, pk):
#         serializer = TransactionSerializer( data=request.data)
#         if not serializer.is_valid():
#             return Response({'serializer': serializer})
#         serializer.save()
#         return redirect('transaction-list')


def createTransaction(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer(queryset,many=True)
    #datan = {"title":"Test Title"}
    return render(
        request,
        'transaction_list.html',
        {
            'data':serializer_class.data,
        }
    )