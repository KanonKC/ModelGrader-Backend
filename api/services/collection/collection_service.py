from django.utils import timezone

from api.repositories.account_repository import AccountRepository
from api.repositories.collection_repository import CollectionRepository
from api.repositories.problem_repository import ProblemRepository
from api.repositories.permission_repository import PermissionRepository
from api.repositories.group_repository import GroupRepository
from ...models import *
from .serializers import *
from ...errors.common import *

class CollectionService:

    def __init__(self, collection_repo: CollectionRepository, account_repo: AccountRepository, problem_repo: ProblemRepository, permission_repo: PermissionRepository, group_repo: GroupRepository):
        self.collection_repo = collection_repo
        self.account_repo = account_repo
        self.problem_repo = problem_repo
        self.permission_repo = permission_repo
        self.group_repo = group_repo

    def create_collection(self, account_id: str, request):
        request.data['creator'] = account_id
        serialize = CollectionSerializer(data=request.data)
        
        if serialize.is_valid():
            serialize.save()
            return serialize.data
        else:
            raise BadRequestError(str(serialize.errors))

    def delete_collection(self, collection_id: str):
        collection = self.collection_repo.get(collection_id)
        collection.delete()
        return None

    def get_collection(self, collection_id: str):
        collection = self.collection_repo.get(collection_id)
        collection.problems = self.collection_repo.get_problems(collection_id)
        collection.group_permissions = self.permission_repo.get_collection_group_permissions(collection_id)

        for cp in collection.problems:
            cp.problem.testcases = self.problem_repo.get_testcases(cp.problem_id)
            cp.problem.group_permissions = self.permission_repo.get_problem_group_permissions(cp.problem_id)

        serializer = CollectionPopulateCollectionProblemsPopulateProblemPopulateAccountAndTestcasesAndProblemGroupPermissionsPopulateGroupAndCollectionGroupPermissionsPopulateGroupSerializer(collection)
        
        return serializer.data

    def get_all_collections(self, request):
        collections = self.collection_repo.list()

        account_id = request.query_params.get('account_id', 0)

        if account_id:
            collections = collections.filter(creator_id=account_id)

        populated_collections = []
        for collection in collections:
            con_probs = self.collection_repo.get_problems(collection)

            populated_cp = []
            for cp in con_probs:
                prob_serialize = ProblemSerializer(cp.problem)
                cp_serialize = CollectionProblemSerializer(cp)
                populated_cp.append({**cp_serialize.data, **prob_serialize.data})
        
            serialize = CollectionSerializer(collection)
            collection_data = serialize.data
            collection_data['problems'] = populated_cp

            populated_collections.append(collection_data)

        return {
            'collections': populated_collections
        }

    def populated_problems(self, collections: Collection):
        collection_ids = [collection.collection_id for collection in collections]
        problemCollections = self.collection_repo.get_problems_by_collection_ids(collection_ids)

        populated_collections = []
        for collection in collections:
            collection.problems = problemCollections.filter(collection=collection)
            populated_collections.append(collection)

        return populated_collections

    def get_all_collections_by_account(self, account_id: str):
        collections = self.collection_repo.get_by_creator(account_id)
        collections = self.populated_problems(collections)
        serialize = CollectionPopulateCollectionProblemsPopulateProblemSerializer(collections, many=True)

        group_ids = self.group_repo.get_group_ids_by_account(account_id)
        manageableCollections = self.collection_repo.get_manageable_by_account(group_ids)
        manageableCollections = self.populated_problems(manageableCollections)
        manageableSerialize = CollectionPopulateCollectionProblemsPopulateProblemSerializer(manageableCollections, many=True)

        return {
            'collections': serialize.data,
            'manageable_collections': manageableSerialize.data
        }

    def update_collection(self, collection_id: str, request):
        update_data = {
            'name': request.data.get('name'),
            'description': request.data.get('description'),
            'is_private': request.data.get('is_private'),
            'is_active': request.data.get('is_active')
        }
        # Remove None values to only update provided fields
        update_data = {k: v for k, v in update_data.items() if v is not None}
        
        collection = self.collection_repo.update_with_timestamp(collection_id, update_data)
        collection_ser = CollectionSerializer(collection)

        return collection_ser.data

    def update_group_permissions_collection(self, collection_id: str, request):
        collection = self.collection_repo.get(collection_id)
        self.permission_repo.delete_collection_group_permissions(collection_id)

        print(request.data['groups'])

        collection_group_permissions = []
        for collection_request in request.data['groups']:
            group = self.group_repo.get(collection_request['group_id'])
            collection_group_permissions.append(
                CollectionGroupPermission(
                    collection=collection,
                    group=group,
                    **collection_request
            ))

        self.permission_repo.bulk_create_collection_group_permissions(collection_group_permissions)

        collection.group_permissions = collection_group_permissions
        serialize = CollectionPopulateCollectionGroupPermissionsPopulateGroupSerializer(collection)

        return serialize.data

    def update_problems_to_collection(self, collection_id: str, request):
        collection = self.collection_repo.get(collection_id)
        self.collection_repo.delete_problems(collection_id)

        collection_problems = []
        order = 0
        for problem_id in request.data['problem_ids']:
            problem = self.problem_repo.get(problem_id)
            collection_problem = CollectionProblem(
                problem=problem,
                collection=collection,
                order=order
            )
            collection_problems.append(collection_problem)
            order += 1

        self.collection_repo.bulk_create_problems(collection_problems)
        collection = self.collection_repo.update_with_timestamp(collection_id, {})
        problem_serialize = CollectionProblemPopulateProblemSecureSerializer(collection_problems, many=True)
        collection_serialize = CollectionSerializer(collection)

        return {
            **collection_serialize.data,
            'problems': problem_serialize.data
        }

    def add_problems_to_collection(self, collection_id: str, request):
        collection = self.collection_repo.get(collection_id)
        populated_problems = []

        index = 0
        for problem_id in request.data['problem_ids']:
            problem = self.problem_repo.get(problem_id)

            alreadyExist = self.collection_repo.find_existing_problem(problem_id, collection_id)
            if alreadyExist:
                alreadyExist.delete()
            
            collection_problem = CollectionProblem(
                problem=problem,
                collection=collection,
                order=index
            )
            collection_problem.save()
            index += 1
            populated_problems.append(collection_problem)
        
        collection = self.collection_repo.update_with_timestamp(collection_id, {})
        problem_serialize = CollectionProblemPopulateProblemSecureSerializer(populated_problems, many=True)
        collection_serialize = CollectionSerializer(collection)

        return {
            **collection_serialize.data,
            'problems': problem_serialize.data
        }

    def remove_problems_from_collection(self, collection_id: str, request):
        self.collection_repo.delete_problems_by_problem_ids(collection_id, request.data['problem_ids'])
        self.collection_repo.update_with_timestamp(collection_id, {})
        return None
