from ..models import *
def canManageTopic(topic:Topic,account:Account):
    is_creator = topic.creator.account_id == account.account_id
    has_permission = len(TopicGroupPermission.objects.filter(permission_manage_topics=True,topic=topic,group__in=[gm.group for gm in GroupMember.objects.filter(account=account)])) > 0
    print(TopicGroupPermission.objects.filter(topic=topic,group__in=[gm.group for gm in GroupMember.objects.filter(account=account)]))
    return is_creator or has_permission