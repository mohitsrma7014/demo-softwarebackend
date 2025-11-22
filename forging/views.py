from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import openpyxl
from django.db import transaction
from .models import Forging
from rest_framework.pagination import PageNumberPagination
from .serializers import ForgingSerializer
import logging
from django.http import HttpResponse
import datetime
from datetime import timedelta, date
from django.utils.dateparse import parse_date
logger = logging.getLogger(__name__)
# ✅ Efficient pagination
class LargeResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 5000

class BulkAddForgingAPIView(APIView):
    """
    API endpoint to add multiple Forging records in bulk.
    """

    def post(self, request, *args, **kwargs):
        data = request.data  # Expecting a list of dictionaries

        if not isinstance(data, list):
            return Response({"error": "Expected a list of dictionaries."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate each entry in the list
        invalid_entries = []
        for i, entry in enumerate(data):
            if not isinstance(entry, dict):
                invalid_entries.append({"index": i, "error": "Entry is not a dictionary."})
            required_fields = [
                "batch_number", "date", "shift", "component", "customer", "slug_weight",
                "rm_grade", "heat_number", "line", "line_incharge", "forman", "target",
                "production", "rework", "up_setting", "half_piercing", "full_piercing",
                "ring_rolling", "sizing", "overheat", "bar_crack_pcs","verified_by"
            ]
            missing_fields = [field for field in required_fields if field not in entry]
            if missing_fields:
                invalid_entries.append({"index": i, "missing_fields": missing_fields})

        if invalid_entries:
            return Response({"error": "Invalid entries found.", "details": invalid_entries}, status=status.HTTP_400_BAD_REQUEST)

        # Try creating all entries in a single transaction
        try:
            with transaction.atomic():
                forging_objects = [Forging(**entry) for entry in data]
                Forging.objects.bulk_create(forging_objects)
            return Response({"message": "Bulk data added successfully."}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": "An error occurred while adding data.", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class ForgingListAPIView(APIView):
    pagination_class = LargeResultsSetPagination

    def get(self, request):
        try:
            queryset = Forging.objects.all().order_by('-date')

            # 🔍 Filters
            filters = {
                'component': request.query_params.get('component'),
                'customer': request.query_params.get('customer'),
                'heat_number': request.query_params.get('heat_number'),
                'line': request.query_params.get('line'),
                'shift': request.query_params.get('shift'),
                'batch_number': request.query_params.get('batch_number'),
            }

            # Apply filters dynamically
            for field, value in filters.items():
                if value:
                    if field in ['id', 'target', 'production']:  # numeric fields
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
            serializer = ForgingSerializer(paginated_qs, many=True)
            return paginator.get_paginated_response(serializer.data)

        except Exception as e:
            logger.error("Error fetching Forging list", exc_info=True)
            return Response(
                {"error": f"Failed to fetch Forging data: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
class ForgingFieldsAPIView(APIView):
    def get(self, request):
        """Return all field names and verbose names from the Forging model"""
        fields_info = [
            {
                "name": f.name,
                "label": f.verbose_name.replace("_", " ").title(),
                "type": f.get_internal_type()
            }
            for f in Forging._meta.fields
        ]
        return Response(fields_info)
    
class ForgingExportAPIView(APIView):
    def get(self, request):
        try:
            queryset = Forging.objects.all().order_by('-date')

            # 🔍 Filters
            filters = {
                'component': request.query_params.get('component'),
                'customer': request.query_params.get('customer'),
                'heat_number': request.query_params.get('heat_number'),
                'line': request.query_params.get('line'),
                'shift': request.query_params.get('shift'),
                'batch_number': request.query_params.get('batch_number'),
            }
            for field, value in filters.items():
                if value:
                    if field in ['id', 'target', 'production']:
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
                selected_fields = [f.name for f in Forging._meta.fields]

            # ✅ Workbook
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Forging Data"

            # Headers
            ws.append([f.replace('_', ' ').title() for f in selected_fields])

            # Rows
            for obj in queryset:
                row = []
                for field in selected_fields:
                    value = getattr(obj, field, '')
                    if isinstance(value, datetime.date):
                        value = value.strftime('%Y-%m-%d')
                    row.append(value)
                ws.append(row)

            response = HttpResponse(
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            )
            response['Content-Disposition'] = 'attachment; filename=forging_data.xlsx'
            wb.save(response)
            return response

        except Exception as e:
            logger.error("Error exporting Forging data", exc_info=True)
            return Response(
                {"error": f"Failed to export Forging data: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        
from django.db.models import Sum, F, FloatField
class ForgingDashboardAPIView(APIView):
    def get(self, request):
        try:
            queryset = Forging.objects.all().order_by('-date')

            # 🔍 Filters
            filters = {
                'component': request.query_params.get('component'),
                'customer': request.query_params.get('customer'),
                'heat_number': request.query_params.get('heat_number'),
                'line': request.query_params.get('line'),
                'shift': request.query_params.get('shift'),
                'batch_number': request.query_params.get('batch_number'),
            }

            # Apply filters dynamically
            for field, value in filters.items():
                if value:
                    if field in ['id', 'target', 'production']:  # numeric fields
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

            # ✅ Calculate totals
            totals = queryset.aggregate(
                total_production_pcs=Sum('production'),
                total_rejection_pcs=(
                    Sum('up_setting') +
                    Sum('half_piercing') +
                    Sum('full_piercing') +
                    Sum('ring_rolling') +
                    Sum('sizing') +
                    Sum('overheat') +
                    Sum('bar_crack_pcs')
                ),
                total_production_ton=Sum(
                    F('slug_weight') * F('production'),
                    output_field=FloatField()
                ) / 1000.0  # convert kg → ton
            )

            # Handle None values gracefully
            for key, value in totals.items():
                totals[key] = round(value or 0, 2)

            serializer = ForgingSerializer(queryset, many=True)

            return Response(
                {
                    "data": serializer.data,
                    "totals": totals
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error("Error fetching Forging list", exc_info=True)
            return Response(
                {"error": f"Failed to fetch Forging data: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
