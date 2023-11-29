from django.urls import path
from .views import account,auth,problem, script,submission,topic,collection


urlpatterns = [
    path("login",auth.login_view),
    path("logout",auth.logout_view),
    path('token',auth.authorization_view),

    path("accounts",account.all_accounts_view),
    path("accounts/<int:account_id>",account.one_account_view),
    path("accounts/<int:account_id>/daily-submissions",account.get_daily_submission),
    path("accounts/<int:account_id>/password",account.change_password),

    path('accounts/<int:account_id>/problems',problem.create_problem_view),
    path('problems',problem.all_problems_view),
    path('problems/<int:problem_id>',problem.one_problem_view),

    # path('problems/<int:problem_id>/<int:account_id>',submission.submit_problem_view),
    path('submissions',submission.all_submission_view),
    path("accounts/<int:account_id>/problems/<int:problem_id>/submissions",submission.account_problem_submission_view),

    path('accounts/<int:account_id>/topics',topic.create_topic_view),
    path('topics',topic.all_topics_view),
    path('topics/<int:topic_id>',topic.one_topic_view),
    path('topics/<int:topic_id>/access',topic.account_access),
    path('topics/<int:topic_id>/collections/<str:method>',topic.topic_collections_view),

    path('accounts/<int:account_id>/collections',collection.create_collection_view),
    path('collections',collection.all_collections_view),
    path('collections/<int:collection_id>',collection.one_collection_view),
    path('collections/<int:collection_id>/problems/<str:method>',collection.collection_problems_view),

    path('script',script.run_script),
]