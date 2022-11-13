from django.urls import path
from .views import account,auth,problem,submission


urlpatterns = [
    path("login",auth.login),
    path("logout",auth.logout),
    path('token',auth.get_authorization),

    path("accounts",account.create_account),
    path("accounts/<int:account_id>",account.get_account),

    path('accounts/<int:account_id>/problems',problem.create_problem),
    path('problems',problem.getall_problem),
    path('problems/<int:problem_id>',problem.one_problem),

    path('problems/<int:problem_id>/<int:account_id>',submission.submit_problem),
    path('submissions',submission.view_all_submission),
]