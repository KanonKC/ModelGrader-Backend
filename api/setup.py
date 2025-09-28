from decouple import AutoConfig
from api.config import Configuration
from api.repositories.account_repository import AccountRepositoryImpl
from api.sandbox.grader import Grader
from api.services.account.account_service import AccountService, AccountServiceImpl
from api.services.auth.auth_service import AuthService, AuthServiceImpl
from api.services.collection.collection_service import CollectionService
from api.services.problem.problem_service import ProblemService
from api.services.topic.topic_service import TopicService
from api.services.submission.submission_service import SubmissionService
from api.services.group.group_service import GroupService
from api.repositories.problem_repository import ProblemRepository
from api.repositories.topic_repository import TopicRepository
from api.repositories.submission_repository import SubmissionRepository
from api.repositories.collection_repository import CollectionRepository
from api.repositories.group_repository import GroupRepository
from api.repositories.permission_repository import PermissionRepository

# Configuration
config = Configuration(AutoConfig())
grader = Grader

# Repositories
account_repo = AccountRepositoryImpl()
problem_repo = ProblemRepository()
topic_repo = TopicRepository()
submission_repo = SubmissionRepository()
collection_repo = CollectionRepository()
group_repo = GroupRepository()
permission_repo = PermissionRepository()

# Services
account_service = AccountServiceImpl(account_repo)
auth_service = AuthServiceImpl(config,account_repo)
collection_service = CollectionService(collection_repo, account_repo, problem_repo, permission_repo, group_repo)
group_service = GroupService(group_repo, account_repo)
problem_service = ProblemService(problem_repo, account_repo, permission_repo, group_repo, topic_repo, grader)
submission_service = SubmissionService(submission_repo, problem_repo, account_repo, topic_repo, problem_service, grader)
topic_service = TopicService(topic_repo, account_repo, permission_repo, group_repo, collection_repo)
