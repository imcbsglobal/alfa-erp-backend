# apps/sales/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import InvoiceImportSerializer

class ImportInvoiceView(APIView):
    def post(self, request):
        serializer = InvoiceImportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success": True, "message": "Invoice imported successfully"}, status=status.HTTP_201_CREATED)
