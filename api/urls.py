from django.urls import path
from .views import problem,submission

urlpatterns = [
    path('problems',problem.getall_create_problem),
    path('problems/<int:problem_id>',problem.get_problem),

    path('problems/<int:problem_id>/submission',submission.submit_problem),
    path('submissions',submission.view_all_submission),
]