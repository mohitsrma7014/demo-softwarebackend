from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Fi
import logging
logger = logging.getLogger(__name__)
from django.db import transaction
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status


class BulkAddFiAPIView(APIView):
    """
    API endpoint to add multiple HeatTreatment records in bulk.
    """

    def post(self, request, *args, **kwargs):
        # Log the received data
        logger.info("Received request to bulk add HeatTreatment records.")
        logger.debug(f"Request data: {request.data}")

        data = request.data  # Expecting a list of dictionaries

        if not isinstance(data, list):
            logger.error("Request data is not a list.")
            return Response({"error": "Expected a list of dictionaries."}, status=status.HTTP_400_BAD_REQUEST)

        invalid_entries = []
        valid_entries = []

        for i, entry in enumerate(data):
            logger.debug(f"Processing entry {i}: {entry}")

            required_fields = [
                "batch_number", "date", "shift", "component","target1", "target","chaker","production", "remark", "cnc_height",
                "cnc_od","cnc_bore","cnc_groove","cnc_dent","forging_height","forging_od","forging_bore","forging_crack","forging_dent",
                "pre_mc_height", "pre_mc_od", "pre_mc_bore", "rework_height", "rework_od", "rework_bore","rework_groove","rework_dent", "heat_no", 
                "total_produced", "verified_by","rust"
            ]

            # Check for missing fields
            missing_fields = [field for field in required_fields if field not in entry]
            if missing_fields:
                logger.warning(f"Entry {i} is missing required fields: {missing_fields}")
                invalid_entries.append({"index": i, "missing_fields": missing_fields})
                continue


            # Validate data types and constraints
            try:
                logger.debug(f"Validating entry {i}...")
                obj = Fi(**entry)
                obj.full_clean()  # Validate using Django's model validation
                valid_entries.append(obj)
                logger.debug(f"Entry {i} validated successfully.")
            except ValidationError as e:
                logger.error(f"Validation error for entry {i}: {str(e)}")
                invalid_entries.append({"index": i, "error": str(e)})
            except Exception as e:
                logger.error(f"Unexpected error for entry {i}: {str(e)}")
                invalid_entries.append({"index": i, "error": str(e)})

        if invalid_entries:
            logger.error(f"Invalid entries found: {invalid_entries}")
            return Response(
                {"error": "Invalid entries found.", "details": invalid_entries},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                logger.info(f"Attempting to bulk create {len(valid_entries)} HeatTreatment records.")
                Fi.objects.bulk_create(valid_entries)
                logger.info("Bulk creation successful.")
            return Response(
                {"message": "Bulk data added successfully.", "processed": len(valid_entries)},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            logger.critical(f"Critical error during bulk creation: {str(e)}")
            return Response(
                {"error": "An error occurred while adding data.", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

from django.db.models.fields.files import FieldFile
import openpyxl
from rest_framework.pagination import PageNumberPagination
import uuid
from django.utils.dateparse import parse_date
from django.http import HttpResponse
import datetime
from .serializers import FiSerializer

class LargeResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 5000


class FiListAPIView(APIView):
    pagination_class = LargeResultsSetPagination

    def get(self, request):
        try:
            queryset = Fi.objects.all().order_by('-date')

            # 🔍 Filters
            filters = {
                'component': request.query_params.get('component'),
                
                'shift': request.query_params.get('shift'),
                'chaker': request.query_params.get('chaker'),
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
            serializer = FiSerializer(paginated_qs, many=True)
            return paginator.get_paginated_response(serializer.data)

        except Exception as e:
            logger.error("Error fetching Forging list", exc_info=True)
            return Response(
                {"error": f"Failed to fetch Forging data: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
class FiFieldsAPIView(APIView):
    def get(self, request):
        """Return all field names and verbose names from the Forging model"""
        fields_info = [
            {
                "name": f.name,
                "label": f.verbose_name.replace("_", " ").title(),
                "type": f.get_internal_type()
            }
            for f in Fi._meta.fields
        ]
        return Response(fields_info)
    
class FiExportAPIView(APIView):
    def get(self, request):
        try:
            queryset = Fi.objects.all().order_by('-date')

            # 🔍 Filters
            filters = {
                'component': request.query_params.get('component'),
                
                'shift': request.query_params.get('shift'),
                'chaker': request.query_params.get('chaker'),
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
                selected_fields = [f.name for f in Fi._meta.fields]

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
