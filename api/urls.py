from django.urls import path
from .views import account,auth,problem,script,submission,topic,collection,testfile,testcase


urlpatterns = [
    # Authentication
    path("login",auth.login),
    path("logout",auth.logout),
    path('token',auth.get_authorization),

    # Account
    path("accounts",account.account_collection),
    path("accounts/<int:account_id>",account.get_account),
    path("accounts/<int:account_id>/daily-submissions",account.get_daily_submission),
    path("accounts/<int:account_id>/password",account.change_password),

    # Problem
    path('accounts/<int:account_id>/problems',problem.create_problem),
    # path('problems/<int:problem_id>/testcases',problem.create_problem),
    path('problems/<int:problem_id>/testfiles',testfile.upload_testfile),
    path('problems',problem.all_problem),
    path('problems/<int:problem_id>',problem.one_problem),

    # Testfile
    path('problems/<int:problem_id>/testfiles/add',problem.add_testfile),
    path('problems/<int:problem_id>/testfiles/remove',problem.remove_testfile),  

    # Resource File
    # path('accounts/<int:account_id>/resources',resourceFile.manage_resource),

    # Submission
    path('problems/<int:problem_id>/<int:account_id>',submission.submit_problem),
    path('submissions',submission.view_all_submission),

    # Topic
    path('accounts/<int:account_id>/topics',topic.create_topic),
    path('topics',topic.all_topic),
    path('topics/<int:topic_id>',topic.one_topic),
    path('topics/<int:topic_id>/access',topic.account_access),
    path('topics/<int:topic_id>/collections/<str:method>',topic.topic_collection),

    # Collection
    path('accounts/<int:account_id>/collections',collection.create_collections),
    path('collections',collection.all_collections),
    path('collections/<int:collection_id>',collection.one_collection),
    path('collections/<int:collection_id>/problems/<str:method>',collection.collection_problems),

    # DB Fetcher
    path('script',script.run_script),
]