from django.urls import path
from .views import problem,submission

urlpatterns = [
    path('problems',problem.create_problem),
    path('problems/<int:problem_id>',problem.get_problem),

    path('problems/<int:problem_id>/submission',submission.submit_problem),
]