from decouple import AutoConfig
from api.config import Configuration
from api.repositories.account_repository import AccountRepositoryImpl
from api.services.account.account_service import AccountService, AccountServiceImpl
from api.services.auth.auth_service import AuthService, AuthServiceImpl
from api.services.collection.collection_service import CollectionService
from api.services.problem.problem_service import ProblemService
from api.services.topic.topic_service import TopicService
from api.services.submission.submission_service import SubmissionService
from api.services.group.group_service import GroupService

config = Configuration(AutoConfig())
account_repo = AccountRepositoryImpl()

account_service = AccountServiceImpl(account_repo)
auth_service = AuthServiceImpl(config,account_repo)
collection_service = CollectionService()
group_service = GroupService()
problem_service = ProblemService()
submission_service = SubmissionService()
topic_service = TopicService()
