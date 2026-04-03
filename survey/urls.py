from django.urls import path 
from . import views

app_name = 'survey'
urlpatterns = [
    
    path('',views.index , name='index'),
    path('create/',views.api_create_project , name='create_project'), # NEW URL
    path('api/delete_project/<int:project_id>/',views.api_delete_project , name='api_delete_project'), # NEW URL
    path('upload/raw-data/<int:project_id>/', views.api_upload_raw_data, name='upload_raw_data_excel'), # <-- TAMBAHKAN INI    
    path('api/bulk-update/<int:project_id>/', views.api_update_thread, name='api_update_thread'), # BARU
    path('api/bulk-delete/<int:project_id>/', views.api_delete_thread, name='api_bulk_delete'), # BARU
    path('api/update-project/<int:project_id>/', views.api_update_project, name='api_update_project'), # <-- Tambahkan baris ini
    path('api/toggle-status/<int:project_id>/', views.api_toggle_status, name='api_toggle_status'),
    path('api/save-design-data/<int:project_id>/', views.api_calculate_cut_fill, name='api_calculate_cutfill'),
    path('export/excel/<int:project_id>/',views.export_project_data_excel,name ='export_project_data_excel'),
    path('api/chart-data/<int:project_id>/', views.api_get_chart_data, name='api_get_chart_data'),
    path('details/<int:pk>/',views.details , name='details'),
    path('api/add-rows/<int:project_id>/', views.api_add_rows, name='api_add_rows'),
    path('api/create-c-section/<int:project_id>/', views.create_c_section, name='create_c_section'),
    path('api/calculate/<int:project_id>/', views.api_calculate_leveling, name='api_calculate'),
    path('api/update-c-section/<int:project_id>/', views.api_update_c_section_data, name='api_update_c_section'),
    path('api/calculate_CS/<int:project_id>/', views.calculate_CS , name='api_calculate_CS' ),
    path('api/analyze-anomaly/', views.analyze_anomaly_api, name='api_analyze_anomaly'),
    # Civilix-App/survey/urls.py
    path('api/project/<int:project_id>/generate-report/', views.api_generate_ai_report, name='generate_report'),
    path('project/<int:project_id>/download-report/', views.download_ai_report_word, name='download_report'),
    path('api/cross-section/add/<int:station_id>/', views.api_add_cross_section, name='api_add_cs'),
    path('api/cross-section/delete/<int:point_id>/', views.api_delete_cross_section, name='api_delete_cs'),
    path('api/get-sta-list/<int:project_id>/', views.api_get_station_list, name='api_get_sta_list'),
    path('api/export-dxf-advanced/<int:project_id>/', views.api_export_dxf_advanced, name='api_export_dxf_advanced'),
    path('api/upload-cs-excel/<int:project_id>/', views.api_upload_cs_excel, name='api_upload_cs_excel')
     
]
