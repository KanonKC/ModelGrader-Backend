# CSR Repository Separation Guide

## Overview
This guide outlines the step-by-step process for refactoring Django ORM calls from service layers to repository layers, ensuring proper separation of concerns and maintainable code architecture.

## Step-by-Step Refactoring Process

### Step 1: Analyze Current Service Code
1. **Identify Django ORM Calls**: Search for patterns like `<ModelName>.objects.<Method>`
2. **Categorize ORM Operations**: Group by model types and operation types (CRUD)
3. **Map Dependencies**: Identify which models are being accessed and their relationships
4. **Document Current Methods**: List all service methods that contain direct ORM calls

### Step 2: Determine Repository Responsibilities
1. **Model-Based Separation**: Each repository should handle only its specific model domain
2. **Permission Models**: All models containing "permission" go to `PermissionRepository`
3. **Group Models**: All models containing "group" (but not "permission") go to `GroupRepository`
4. **Core Models**: Each main model gets its own repository (e.g., `CollectionRepository`, `ProblemRepository`)

### Step 3: Design Repository Methods
1. **Method Naming Convention**:
   - Repository methods must NOT contain their repository name (❌ `get_collection_by_id` → ✅ `get`)
   - Methods that get items by ID should NOT have "_by_id" suffix (❌ `get_by_id` → ✅ `get`)
   - Use descriptive names for complex operations (✅ `get_by_creator`, `get_manageable_collections`)

2. **Parameter Guidelines**:
   - Repository functions must NOT accept Django model objects as parameters
   - Always use IDs or primitive types instead of model instances
   - Example: ❌ `delete_permissions(collection: Collection)` → ✅ `delete_permissions(collection_id: str)`

### Step 4: Create/Update Repository Files

#### A. Import Required Models
```python
from api.models import ModelName1, ModelName2
from typing import List
```

#### B. Implement Repository Methods
```python
class ExampleRepository:
    def __init__(self):
        pass
    
    def get(self, item_id: str):
        return ModelName.objects.get(id=item_id)
    
    def list(self, filters: dict = {}):
        queryset = ModelName.objects.all()
        # Apply filters
        return queryset
    
    def create(self, data: dict):
        instance = ModelName.objects.create(**data)
        return instance
    
    def delete(self, item_id: str):
        ModelName.objects.filter(id=item_id).delete()
```

### Step 5: Update Service Layer

#### A. Add Repository Dependencies
```python
def __init__(self, primary_repo: PrimaryRepository, permission_repo: PermissionRepository, group_repo: GroupRepository):
    self.primary_repo = primary_repo
    self.permission_repo = permission_repo
    self.group_repo = group_repo
```

#### B. Replace ORM Calls
Replace direct ORM calls with repository method calls:
```python
# Before
collection = Collection.objects.get(collection_id=collection_id)
permissions = CollectionGroupPermission.objects.filter(collection=collection)

# After
collection = self.collection_repo.get(collection_id)
permissions = self.permission_repo.get_collection_group_permissions(collection_id)
```

### Step 6: Handle Model Instantiation
1. **Direct Save Calls**: Always call `.save()` immediately when creating/updating instances
2. **No Wrapper Methods**: Don't create repository methods just to call `.save()`
3. **Bulk Operations**: Use repository methods for bulk create/update operations

Example:
```python
# ✅ Correct approach
collection_problem = CollectionProblem(
    problem=problem,
    collection=collection,
    order=index
)
collection_problem.save()

# ❌ Wrong approach - unnecessary wrapper
def save_problem(self, collection_problem):
    collection_problem.save()
    return collection_problem
```

## Strict Rules to Follow

### 1. Repository Naming Rules
- ✅ `get(id)` - Get single item by ID
- ✅ `list()` - Get multiple items
- ✅ `create(data)` - Create new item
- ✅ `update(id, data)` - Update existing item
- ✅ `delete(id)` - Delete item by ID
- ❌ `get_collection_by_id()` - Contains repository name
- ❌ `get_by_id()` - Unnecessary "_by_id" suffix

### 2. Parameter Rules
- ✅ Use primitive types: `str`, `int`, `dict`, `List[str]`
- ✅ Use IDs instead of model objects: `collection_id: str`
- ❌ Never use Django model objects as parameters: `collection: Collection`

### 3. Model Separation Rules
- ✅ Each repository handles only its domain models
- ✅ Permission models → `PermissionRepository`
- ✅ Group models (non-permission) → `GroupRepository`
- ❌ Cross-repository ORM calls
- ❌ Repository accessing models outside its domain

### 4. Service Layer Rules
- ✅ No direct Django ORM calls (`ModelName.objects.*`)
- ✅ All data access through repository methods
- ✅ Call `.save()` directly on model instances
- ❌ Django ORM patterns in service methods
- ❌ Wrapper methods just for `.save()` calls

### 5. Import Rules
- ✅ Import only necessary models in repositories
- ✅ Remove unused model imports after refactoring
- ❌ Importing models not used by the repository

## Verification Checklist

After refactoring, verify:

1. **No ORM in Services**: Search for `\.objects\.` patterns in service files
2. **No "_by_id" Suffixes**: Search for `def get.*_by_id` patterns
3. **No Model Parameters**: Check repository method signatures
4. **Proper Separation**: Ensure each repository handles only its models
5. **No Linter Errors**: Run linter on all modified files
6. **Functionality Intact**: Test that all operations still work correctly

## Benefits of Proper Separation

1. **Maintainability**: Clear separation of concerns
2. **Testability**: Repository methods are easier to mock and test
3. **Consistency**: Uniform naming and structure across repositories
4. **Modularity**: Each repository handles its specific domain
5. **Scalability**: Easy to add new repositories and methods
6. **Type Safety**: Clear parameter types and return values

## Common Pitfalls to Avoid

1. **Repository Name in Methods**: Don't include repository name in method names
2. **Model Objects as Parameters**: Always use IDs instead of model instances
3. **Cross-Repository ORM**: Don't access other models directly
4. **Unnecessary Wrappers**: Don't create methods just to call `.save()`
5. **Mixed Responsibilities**: Keep each repository focused on its domain
6. **Inconsistent Naming**: Follow the naming conventions strictly

---

*This guide should be followed strictly to ensure consistent and maintainable repository architecture across the entire codebase.*