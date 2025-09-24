from django.utils import timezone

from api.repositories.account_repository import AccountRepository
from api.repositories.collection_repository import CollectionRepository
from api.repositories.problem_repository import ProblemRepository
from ...models import *
from .serializers import *
from ...errors.common import *

class CollectionService:

    def __init__(self, collection_repo: CollectionRepository, account_repo: AccountRepository, problem_repo: ProblemRepository):
        self.collection_repo = collection_repo
        self.account_repo = account_repo
        self.problem_repo = problem_repo

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
        collection.group_permissions = CollectionGroupPermission.objects.filter(collection=collection)

        for cp in collection.problems:
            cp.problem.testcases = self.problem_repo.get_testcases(cp.problem_id)
            cp.problem.group_permissions = ProblemGroupPermission.objects.filter(problem=cp.problem)

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
        problemCollections = CollectionProblem.objects.filter(collection__in=collections)

        populated_collections = []
        for collection in collections:
            collection.problems = problemCollections.filter(collection=collection)
            populated_collections.append(collection)

        return populated_collections

    def get_all_collections_by_account(self, account_id: str):
        account = self.account_repo.get(account_id)
        collections = Collection.objects.filter(creator=account).order_by('-updated_date')
        collections = self.populated_problems(collections)
        serialize = CollectionPopulateCollectionProblemsPopulateProblemSerializer(collections, many=True)

        manageableCollections = Collection.objects.filter(
            collectiongrouppermission__permission_manage_collections=True,
            collectiongrouppermission__group__in=GroupMember.objects.filter(account=account).values_list("group", flat=True)
        ).order_by('-updated_date')
        manageableCollections = self.populated_problems(manageableCollections)
        manageableSerialize = CollectionPopulateCollectionProblemsPopulateProblemSerializer(manageableCollections, many=True)

        return {
            'collections': serialize.data,
            'manageable_collections': manageableSerialize.data
        }

    def update_collection(self, collection_id: str, request):
        collection = Collection.objects.get(collection_id=collection_id)
        collection.name = request.data.get('name', collection.name)
        collection.description = request.data.get('description', collection.description)
        collection.is_private = request.data.get('is_private', collection.is_private)
        collection.is_active = request.data.get('is_active', collection.is_active)
        collection.updated_date = timezone.now()

        collection.save()
        collection_ser = CollectionSerializer(collection)

        return collection_ser.data

    def update_group_permissions_collection(self, collection_id: str, request):
        collection = Collection.objects.get(collection_id=collection_id)
        CollectionGroupPermission.objects.filter(collection=collection).delete()

        print(request.data['groups'])

        collection_group_permissions = []
        for collection_request in request.data['groups']:
            group = Group.objects.get(group_id=collection_request['group_id'])
            collection_group_permissions.append(
                CollectionGroupPermission(
                    collection=collection,
                    group=group,
                    **collection_request
            ))

        CollectionGroupPermission.objects.bulk_create(collection_group_permissions)

        collection.group_permissions = collection_group_permissions
        serialize = CollectionPopulateCollectionGroupPermissionsPopulateGroupSerializer(collection)

        return serialize.data

    def update_problems_to_collection(self, collection_id: str, request):
        collection = Collection.objects.get(collection_id=collection_id)
        CollectionProblem.objects.filter(collection=collection).delete()

        collection_problems = []
        order = 0
        for problem_id in request.data['problem_ids']:
            problem = Problem.objects.get(problem_id=problem_id)
            collection_problem = CollectionProblem(
                problem=problem,
                collection=collection,
                order=order
            )
            collection_problems.append(collection_problem)
            order += 1

        CollectionProblem.objects.bulk_create(collection_problems)
        collection.updated_date = timezone.now()
        collection.save()
        problem_serialize = CollectionProblemPopulateProblemSecureSerializer(collection_problems, many=True)
        collection_serialize = CollectionSerializer(collection)

        return {
            **collection_serialize.data,
            'problems': problem_serialize.data
        }

    def add_problems_to_collection(self, collection_id: str, request):
        collection = Collection.objects.get(collection_id=collection_id)
        populated_problems = []

        index = 0
        for problem_id in request.data['problem_ids']:
            problem = Problem.objects.get(problem_id=problem_id)

            alreadyExist = CollectionProblem.objects.filter(problem=problem, collection=collection)
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
        
        collection.updated_date = timezone.now()
        collection.save()
        problem_serialize = CollectionProblemPopulateProblemSecureSerializer(populated_problems, many=True)
        collection_serialize = CollectionSerializer(collection)

        return {
            **collection_serialize.data,
            'problems': problem_serialize.data
        }

    def remove_problems_from_collection(self, collection_id: str, request):
        collection = Collection.objects.get(collection_id=collection_id)
        CollectionProblem.objects.filter(collection=collection, problem_id__in=request.data['problem_ids']).delete()
        collection.updated_date = timezone.now()
        collection.save()
        return None
