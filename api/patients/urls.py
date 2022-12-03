from django.urls import path
from . import views

urlpatterns = [
    path('search-card', views.patients_search_card),
    path('search-individual', views.patients_search_individual),
    path('search-l2-card', views.patients_search_l2_card),
    path('create-l2-individual-from-card', views.create_l2_individual_from_card),
    path('card/<int:card_id>', views.patients_get_card_data),
    path('card/save', views.patients_card_save),
    path('card/archive', views.patients_card_archive),
    path('card/unarchive', views.patients_card_unarchive),
    path('card/harmful-factors', views.patients_harmful_factors),
    path('card/save-harmful-factors', views.patients_save_harmful_factors),
    path('individuals/search', views.individual_search),
    path('individuals/sex', views.get_sex_by_param),
    path('individuals/edit-doc', views.edit_doc),
    path('individuals/edit-agent', views.edit_agent),
    path('individuals/update-cdu', views.update_cdu),
    path('individuals/update-wia', views.update_wia),
    path('individuals/sync-rmis', views.sync_rmis),
    path('individuals/sync-tfoms', views.sync_tfoms),
    path('individuals/load-anamnesis', views.load_anamnesis),
    path('individuals/load-dreg', views.load_dreg),
    path('individuals/load-screening', views.load_screening),
    path('individuals/load-control-param', views.load_control_param),
    path('individuals/load-selected-control-params', views.load_selected_control_params),
    path('individuals/save-selected-control-params', views.save_patient_control_params),
    path('individuals/load-vaccine', views.load_vaccine),
    path('individuals/load-ambulatory-data', views.load_ambulatory_data),
    path('individuals/load-benefit', views.load_benefit),
    path('individuals/load-dreg-detail', views.load_dreg_detail),
    path('individuals/load-vaccine-detail', views.load_vaccine_detail),
    path('individuals/load-ambulatorydata-detail', views.load_ambulatory_data_detail),
    path('individuals/load-ambulatory-history', views.load_ambulatory_history),
    path('individuals/load-benefit-detail', views.load_benefit_detail),
    path('individuals/save-dreg', views.save_dreg),
    path('individuals/save-plan-dreg', views.update_dispensary_reg_plans),
    path('individuals/save-vaccine', views.save_vaccine),
    path('individuals/save-ambulatory-data', views.save_ambulatory_data),
    path('individuals/save-benefit', views.save_benefit),
    path('individuals/save-anamnesis', views.save_anamnesis),
    path('is-card', views.is_l2_card),
    path('save-screening-plan', views.update_screening_reg_plan),
]
