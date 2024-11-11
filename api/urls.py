from django.urls import path
from .views import account,auth,problem, script,submission,topic,collection,group


urlpatterns = [
    path("login",auth.login_view),
    path("logout",auth.logout_view),
    path('token',auth.authorization_view),

    path("accounts",account.all_accounts_view),
    path("accounts/<str:account_id>",account.one_creator_view),
    path("accounts/<str:account_id>/daily-submissions",account.get_daily_submission),
    path("accounts/<str:account_id>/password",account.change_password),

    path('accounts/<str:account_id>/problems',problem.all_problems_creator_view),
    path('accounts/<str:account_id>/problems/<str:problem_id>',problem.one_problem_creator_view),
    path('accounts/<str:account_id>/problems/<str:problem_id>/groups',problem.problem_group_view),
    path("accounts/<str:account_id>/problems/<str:problem_id>/submissions",submission.creator_problem_submissions_view),
    path("accounts/<str:account_id>/topics/<str:topic_id>/problems/<str:problem_id>/submissions",submission.topic_account_problem_submission_view),

    path('accounts/<str:account_id>/collections',collection.all_collections_creator_view),
    path('accounts/<str:account_id>/collections/<str:collection_id>',collection.one_collection_creator_view),
    path('accounts/<str:account_id>/collections/<str:collection_id>/groups',collection.collection_groups_view),
    
    path('accounts/<str:account_id>/topics',topic.all_topics_creator_view),
    path('accounts/<str:account_id>/topics/<str:topic_id>',topic.one_topic_creator_view),
    path('accounts/<str:account_id>/topics/<str:topic_id>/groups',topic.topic_groups_view),
    
    path('accounts/<str:account_id>/access/topics',topic.all_topics_access_view),

    path('accounts/<str:account_id>/groups',group.all_groups_creator_view),
    
    path('problems',problem.all_problems_view),
    path('problems/validate',problem.validation_view),
    path('problems/<str:problem_id>',problem.one_problem_view),
    path('problems/<str:problem_id>/import/pdf',problem.import_pdf_view),
    path("problems/<str:problem_id>/accounts/<str:account_id>/submissions",submission.account_problem_submission_view),
    path('topics/<str:topic_id>/problems/<str:problem_id>/accounts/<str:account_id>',problem.problem_in_topic_account_view),

    path('collections',collection.all_collections_view),
    path('collections/<str:collection_id>',collection.one_collection_view),
    path('collections/<str:collection_id>/problems/<str:method>',collection.collection_problems_view),

    path('topics',topic.all_topics_view),
    path('topics/<str:topic_id>',topic.one_topic_view),
    path('topics/<str:topic_id>/access',topic.account_access),
    path('topics/<str:topic_id>/collections/<str:method>',topic.topic_collections_view),

    path('groups/<str:group_id>',group.one_group_view),
    path('groups/<str:group_id>/members/<str:method>',group.group_members_view),

    path('submissions',submission.all_submission_view),


    path('script',script.run_script),
]