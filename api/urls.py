from django.urls import path
from .views import account,auth, script,submission,topic,group
from .controllers import problem_controller, collection_controller
from api.controllers import account_controller,auth_controller


urlpatterns = [
    path("login",auth_controller.login),
    path("logout",auth_controller.logout),
    path('token',auth_controller.authorization),

    path("accounts",account_controller.all_accounts),
    path("accounts/<str:account_id>",account_controller.one_creator),
    # path("accounts/<str:account_id>/daily-submissions",account_controller.get_daily_submission),
    path("accounts/<str:account_id>/password",account_controller.change_password),

    path('accounts/<str:account_id>/problems',problem_controller.all_problems_creator_view),
    path('accounts/<str:account_id>/problems/<str:problem_id>',problem_controller.one_problem_creator_view),
    path('accounts/<str:account_id>/problems/<str:problem_id>/groups',problem_controller.problem_group_view),
    path("accounts/<str:account_id>/problems/<str:problem_id>/submissions",submission.creator_problem_submissions_view),
    path("accounts/<str:account_id>/topics/<str:topic_id>/problems/<str:problem_id>/submissions",submission.topic_account_problem_submission_view),

    path('accounts/<str:account_id>/collections',collection_controller.all_collections_creator_view),
    path('accounts/<str:account_id>/collections/<str:collection_id>',collection_controller.one_collection_creator_view),
    path('accounts/<str:account_id>/collections/<str:collection_id>/groups',collection_controller.collection_groups_view),
    
    path('accounts/<str:account_id>/topics',topic.all_topics_creator_view),
    path('accounts/<str:account_id>/topics/<str:topic_id>',topic.one_topic_creator_view),
    path('accounts/<str:account_id>/topics/<str:topic_id>/groups',topic.topic_groups_view),
    
    path('accounts/<str:account_id>/access/topics',topic.all_topics_access_view),

    path('accounts/<str:account_id>/groups',group.all_groups_creator_view),
    
    path('problems',problem_controller.all_problems_view),
    path('problems/list',problem_controller.all_problems_list_view),
    path('problems/validate',problem_controller.validation_view),
    path('problems/<str:problem_id>',problem_controller.one_problem_view),
    path('problems/<str:problem_id>/import/pdf',problem_controller.import_pdf_view),
    path("problems/<str:problem_id>/accounts/<str:account_id>/submissions",submission.account_problem_submission_view),
    path('topics/<str:topic_id>/problems/<str:problem_id>/accounts/<str:account_id>',problem_controller.problem_in_topic_account_view),

    path('collections',collection_controller.all_collections_view),
    path('collections/<str:collection_id>',collection_controller.one_collection_view),
    path('collections/<str:collection_id>/problems/<str:method>',collection_controller.collection_problems_view),

    path('topics',topic.all_topics_view),
    path('topics/<str:topic_id>',topic.one_topic_view),
    path('topics/<str:topic_id>/access',topic.account_access),
    path('topics/<str:topic_id>/collections/<str:method>',topic.topic_collections_view),

    path('groups/<str:group_id>',group.one_group_view),
    path('groups/<str:group_id>/members/<str:method>',group.group_members_view),

    path('submissions',submission.all_submission_view),

    # New Versions
    # path('v1/problems/<str:problem_id>',problem_controller.get_or_update_problem),
    # path('v1/problems/<str:problem_id>/import/pdf',problem_controller.upload_pdf),
    # path('v1/problems/<str:problem_id>/pdf',problem_controller.get_problem_pdf),
    # path('v1/problems', problem_controller.create_problem),

    path('script',script.run_script),
]