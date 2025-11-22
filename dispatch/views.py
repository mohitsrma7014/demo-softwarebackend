from django.shortcuts import render
from rest_framework import generics
from .models import dispatch
# Create your views here.
from .serializers import DispatchSerializer

class DispatchListCreateAPIView(generics.ListCreateAPIView):
    queryset = dispatch.objects.all()
    serializer_class = DispatchSerializer



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

import logging
logger = logging.getLogger(__name__)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.db.models.fields.files import FieldFile
import openpyxl
from rest_framework.pagination import PageNumberPagination
import uuid
from django.utils.dateparse import parse_date
from django.http import HttpResponse
import datetime

class LargeResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 5000


class DispatchListAPIView(APIView):
    pagination_class = LargeResultsSetPagination

    def get(self, request):
        try:
            queryset = dispatch.objects.all().order_by('-date')

            # 🔍 Filters
            filters = {
                'component': request.query_params.get('component'),
                
                'heat_no': request.query_params.get('heat_no'),
                'invoiceno': request.query_params.get('invoiceno'),
                'batch_number': request.query_params.get('batch_number'),
            }

            # Apply filters dynamically
            for field, value in filters.items():
                if value:
                    if field in ['id', 'target', 'qty']:  # numeric fields
                        queryset = queryset.filter(**{field: value})
                    else:
                        queryset = queryset.filter(**{f"{field}__icontains": value})

            # 🔹 Date range filter
            date_from = request.query_params.get('date_from')
            date_to = request.query_params.get('date_to')

            if date_from:
                queryset = queryset.filter(date__gte=parse_date(date_from))
            if date_to:
                queryset = queryset.filter(date__lte=parse_date(date_to))

            # Pagination
            paginator = self.pagination_class()
            paginated_qs = paginator.paginate_queryset(queryset, request)
            serializer = DispatchSerializer(paginated_qs, many=True)
            return paginator.get_paginated_response(serializer.data)

        except Exception as e:
            logger.error("Error fetching Forging list", exc_info=True)
            return Response(
                {"error": f"Failed to fetch Forging data: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        
class DispatchFieldsAPIView(APIView):
    def get(self, request):
        """Return all field names and verbose names from the Forging model"""
        fields_info = [
            {
                "name": f.name,
                "label": f.verbose_name.replace("_", " ").title(),
                "type": f.get_internal_type()
            }
            for f in dispatch._meta.fields
        ]
        return Response(fields_info)
    
class DispatchExportAPIView(APIView):
    def get(self, request):
        try:
            queryset = dispatch.objects.all().order_by('-date')

            # 🔍 Filters
            filters = {
                'component': request.query_params.get('component'),
                
                'heat_no': request.query_params.get('heat_no'),
                'invoiceno': request.query_params.get('invoiceno'),
                'batch_number': request.query_params.get('batch_number'),
            }
            for field, value in filters.items():
                if value:
                    if field in ['id', 'target', 'qty']:
                        queryset = queryset.filter(**{field: value})
                    else:
                        queryset = queryset.filter(**{f"{field}__icontains": value})

            # 🔹 Date range
            date_from = request.query_params.get('date_from')
            date_to = request.query_params.get('date_to')
            if date_from:
                queryset = queryset.filter(date__gte=parse_date(date_from))
            if date_to:
                queryset = queryset.filter(date__lte=parse_date(date_to))

            # ✅ Selected fields (comma separated)
            selected_fields = request.query_params.get('fields')
            if selected_fields:
                selected_fields = [f.strip() for f in selected_fields.split(',')]
            else:
                # default: all fields
                selected_fields = [f.name for f in dispatch._meta.fields]

            # ✅ Workbook
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Heat Treatment Data"

            # Headers
            ws.append([f.replace('_', ' ').title() for f in selected_fields])

            # Rows
            for obj in queryset:
                row = []
                for field in selected_fields:
                    value = getattr(obj, field, '')

                    # 🔹 Convert unsupported types
                    if isinstance(value, datetime.date):
                        value = value.strftime('%Y-%m-%d')

                    elif isinstance(value, uuid.UUID):
                        value = str(value)

                    elif isinstance(value, FieldFile):  # ✅ Safely handle FileField / ImageField
                        if value and value.name:
                            try:
                                value = request.build_absolute_uri(value.url)
                            except Exception:
                                value = value.name
                        else:
                            value = ''  # No file uploaded

                    elif hasattr(value, 'id') and hasattr(value, '__str__'):
                        # ✅ Handles ForeignKey or related objects
                        value = str(value)

                    elif isinstance(value, (list, dict, set)):
                        value = str(value)

                    row.append(value)
                ws.append(row)

            response = HttpResponse(
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            )
            response['Content-Disposition'] = 'attachment; filename=Heat_treatment_data.xlsx'
            wb.save(response)
            return response

        except Exception as e:
            logger.error("Error exporting ht data", exc_info=True)
            return Response(
                {"error": f"Failed to export ht data: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
