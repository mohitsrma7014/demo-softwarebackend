# masters/urls.py
from django.urls import path,include
from .views import *
from rest_framework.routers import DefaultRouter
router = DefaultRouter()

router.register(r'tags', TagGenerationViewSet, basename='tags')
urlpatterns = [
    path('api/', include(router.urls)),
    path('', MasterDropdownView.as_view(), name='master-dropdown'),
    path('rmreceiving/', RMReceivingListCreateAPIView.as_view(), name='rmreceiving-list-create'),
    path("rmreceiving/<uuid:uid>/", RMReceivingDetailAPIView.as_view(), name="rmreceiving-detail"),
    path('holdmaterial/', HoldMaterialListCreateAPIView.as_view(), name='holdmaterial-list-create'),
    path('batchtracking/', BatchTrackingListCreateAPIView.as_view(), name='batchtracking-list-create'),
    path("masterlist/suggestions/", ComponentSuggestionAPIView.as_view(), name="component_suggestions"),
    path("masterlist/details/", ComponentDetailAPIView.as_view(), name="component_details"),
    path("rmreceiving/filter/", RMReceivingFilteredAPIView.as_view(), name="rmreceiving_filter"),
    path("batch/suggestions/", BatchSuggestionAPIView.as_view(), name="BatchSuggestionAPIView"),
    path("batch/details/", BatchDetailAPIView.as_view(), name="BatchDetailAPIView"),
    path("issuebatch/suggestions/", IssueBatchSuggestionAPIView.as_view(), name="IssueBatchSuggestionAPIView"),
    path('batch_details/', batch_details, name='batch_details'),
    path('batch_remaining_qty/', batch_remaining_qty, name='batch_remaining_qty'),
    path('get_child_components/', get_child_components, name='get_child_components'),
    path('batch_remaining_qty_forging/', batch_remaining_qty_forging, name='batch_remaining_qty_forging'),
    path('export/', BatchTrackingExportAPIView.as_view(), name='BatchTrackingExportAPIView'),
    path('fields/', BatchTrackingFieldsAPIView.as_view(), name='issue-fields'),
    path('recivingexport/', RMReceivingExportAPIView.as_view(), name='RMReceivingExportAPIView'),
    path('recivingfields/', RMReceivingFieldsAPIView.as_view(), name='reciving-fields'),
    path('holdexport/', HoldMaterialExportAPIView.as_view(), name='HoldMaterialExportAPIView'),
    path('holdfields/', HoldMaterialFieldsAPIView.as_view(), name='hold-fields'),
    path('batch_remaining_qty_heat_treatment/', batch_remaining_qty_heat_treatment, name='batch_remaining_qty_heat_treatment'),
    path('batch_remaining_qty_pre_mc/', batch_remaining_qty_pre_mc, name='batch_remaining_qty_pre_mc'),
    path('batch_remaining_machining/', batch_remaining_machining, name='batch_remaining_machining'),
    path('batch_remaining_fi/', batch_remaining_fi, name='batch_remaining_fi'),
    path('batch_remaining_qty_marking/', batch_remaining_qty_marking, name='batch_remaining_qty_marking'),
    path('batch_remaining_qty_visual/', batch_remaining_qty_visual, name='batch_remaining_qty_visual'),
    path('batch_remaining_qty_dispatch/', batch_remaining_qty_dispatch, name='batch_remaining_qty_dispatch'),
    path('get_operation_target/', get_operation_target, name='get_operation_target'),
    path('masterlist/', MasterlistAPIView.as_view(), name='masterlist'),
    path('invoice-list/', invoice_list, name='invoice_list'),
    path('invoice-details/', invoice_details, name='invoice_details'),
    path('schedules/', ScheduleAPIView1.as_view(), name='schedule-api'),
    path('schedules/<int:pk>/update-planned/', ScheduleUpdatePlannedView.as_view(), name='update-planned'),
    path('schedules/<int:pk>/', ScheduleAPIView1.as_view(), name='schedule-detail'),
    path('rmreceiving/open-partial/',  OpenAndPartialRMReceiving.as_view(), name='open_partial_rmreceiving'),
    path('forging-blockmt-comparison/', production_data_api, name='forging_blockmt_comparison'),

    path('masterlistn/', masterlist_list_create, name='masterlist-list-create'),
    path('masterlistn/<int:pk>/', masterlist_retrieve_update_delete, name='masterlist-retrieve-update-delete'),
    
    # Masterlist history
    path('masterlistn/<int:pk>/history/',masterlist_history, name='masterlist-history'),
    
    # Document endpoints
    path('masterlistn/<int:masterlist_pk>/documents/', document_list, name='document-list'),
    path('masterlistn/<int:masterlist_pk>/documents/upload/', document_upload, name='document-upload'),
    path('masterlistn/<int:masterlist_pk>/documents/<str:doc_type>/',document_type_history, name='document-type-history'),
    path('masterlistn/<int:masterlist_pk>/documents/<int:doc_pk>/set-current/', document_set_current, name='document-set-current'),
    path('api/masterlist/missing_documents_report/', missing_documents_report, name='missing_documents_report'),
    path('api/masterlist/create/', MasterlistCreateAPIView.as_view(), name='masterlist-create'),
    path('spc/component/<str:component>/', ComponentSPCDetailView.as_view(), name='component-spc-detail'),
    path('spc-dimensions/bulk-create/', BulkSPCDimensionCreateAPIView.as_view(), name='bulk-spc-dimension-create'),








]
