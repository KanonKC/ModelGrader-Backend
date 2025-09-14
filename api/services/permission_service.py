from ..models import Account, GroupMember, Problem, Topic, TopicGroupPermission
from django.forms.models import model_to_dict

def canManageProblem(token, problem_id):
    """
    Check if user has permission to edit this problem
    Return: True/False
    """
    try:
        account = Account.objects.get(token=token)
        account = model_to_dict(account)
        problem = Problem.objects.get(problem_id=problem_id)
        problem = model_to_dict(problem)
        if account['account_id'] == problem['creator']:
            return True # Only creator can manage
    except (Account.DoesNotExist, Problem.DoesNotExist):
        return False

def canManageTopic(topic:Topic,account:Account):
    is_creator = topic.creator.account_id == account.account_id
    has_permission = len(TopicGroupPermission.objects.filter(permission_manage_topics=True,topic=topic,group__in=[gm.group for gm in GroupMember.objects.filter(account=account)])) > 0
    return is_creator or has_permission