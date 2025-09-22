from api.models import GroupMember


class GroupRepository:
    def __init__(self):
        pass

    def list_by_account_id(self, account_id: str) -> list[str]:
        return GroupMember.objects.filter(account_id=account_id).values_list("group", flat=True)