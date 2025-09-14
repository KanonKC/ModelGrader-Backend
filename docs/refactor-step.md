# Django Module Refactoring Guide

This document provides step-by-step instructions for refactoring any Django module from a views-based architecture to a clean service-controller architecture.

## Overview

The refactoring process transforms the codebase from:
- **Old Pattern**: Views handle both HTTP concerns and business logic
- **New Pattern**: Controllers handle HTTP concerns, Services handle business logic

## Architecture Before vs After

### Before Refactoring:
```
api/
├── views/
│   └── {module}.py (HTTP + Business Logic)
├── controllers/
│   └── {module}/ (Individual function files)
└── serializers.py (All serializers mixed together)
```

### After Refactoring:
```
api/
├── controllers/
│   └── {module}_controller.py (HTTP handling only)
├── services/
│   └── {module}/
│       ├── {module}_service.py (Business logic only)
│       └── serializers.py (Module-specific serializers)
└── urls.py (Updated to use controllers)
```

**Example Modules**: `problem`, `account`, `auth`, `topic`, `collection`, `submission`, etc.

## Step-by-Step Refactoring Process

### Step 1: Consolidate Controller Functions into Service Layer

#### 1.1 Identify All Controller Functions
First, examine the controller directory to identify all functions:
```bash
# List all files in the target module controller directory
ls api/controllers/{module}/
```

Common function patterns:
- `create_{module}.py`
- `delete_{module}.py` 
- `get_{module}.py`
- `get_all_{modules}.py`
- `update_{module}.py`
- Plus additional module-specific functions...

#### 1.2 Read Each Controller Function
For each file, examine the function structure:
```python
# Example from create_{module}.py
def create_{module}(account_id: str, request):
    # Business logic here
    return Response(data, status=status.HTTP_201_CREATED)
```

#### 1.3 Create Service Module Structure
Create the service directory structure:
```bash
mkdir -p api/services/{module}/
touch api/services/{module}/__init__.py
touch api/services/{module}/{module}_service.py
```

#### 1.4 Extract Functions to Service Layer
Copy all functions from individual controller files into `{module}_service.py`:

```python
# api/services/{module}/{module}_service.py
from django.utils import timezone  # If needed for timestamps
from ...models import *
from .serializers import *
from ...errors.common import *
# Add other imports specific to your module

def create_{module}(account_id: str, request):
    # Extract business logic from original controller
    # Remove Response objects, return raw data
    account = Account.objects.get(account_id=account_id)
    # ... business logic ...
    return serialized_data  # Return raw data, not Response objects

def delete_{module}(entity: ModelClass):
    # Business logic only
    related_objects = RelatedModel.objects.filter(entity=entity)
    entity.delete()
    related_objects.delete()
    return None

def get_{module}(entity: ModelClass):
    # Business logic for retrieval
    serialize = EntitySerializer(entity)
    return serialize.data

# ... Add all other functions from individual controller files
```

**Key Changes During Extraction:**
- Remove `Response()` objects - return raw data instead
- Remove HTTP status codes - let controllers handle them
- Replace generic error responses with proper exception classes
- Keep all business logic intact

### Step 2: Create Module-Specific Serializers

#### 2.1 Create Serializers Module
```bash
touch api/services/{module}/serializers.py
```

#### 2.2 Extract Module-Related Serializers
From the main `serializers.py`, identify and extract all module-related serializers:

```python
# api/services/{module}/serializers.py
from rest_framework import serializers
from ...models import *

# Core Module Serializers
class {Module}Serializer(serializers.ModelSerializer):
    class Meta:
        model = {Module}
        fields = "__all__"

class {Module}SecureSerializer(serializers.ModelSerializer):
    class Meta:
        model = {Module}
        exclude = ['sensitive_field1', 'sensitive_field2']  # Exclude sensitive fields

# Related Entity Serializers (if applicable)
class RelatedEntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = RelatedEntity
        fields = "__all__"

# Complex Nested Serializers
class {Module}PopulateRelatedEntitiesSerializer(serializers.ModelSerializer):
    related_field = RelatedEntitySerializer()
    class Meta:
        model = {Module}
        fields = "__all__"
        include = ['related_field']
```

**How to Identify Module-Related Serializers:**
1. Search for `class.*{Module}.*Serializer` in main serializers.py
2. Look for serializers that reference your module's model
3. Include dependency serializers (Account, Group, etc.) if they're used
4. Move complex nested serializers that populate your module's relationships

**Common Serializer Categories:**
- Core module serializers (basic CRUD)
- Secure versions (excluding sensitive fields)
- Related entity serializers 
- Complex nested serializers (with relationships)
- Integration serializers (with other modules)

#### 2.3 Update Service Import
```python
# In {module}_service.py
from .serializers import *  # Use local serializers
```

### Step 3: Create Controller Layer

#### 3.1 Create Module Controller
```bash
touch api/controllers/{module}_controller.py
```

#### 3.2 Implement Controller Pattern
Follow the same pattern as `account_controller.py`:

```python
# api/controllers/{module}_controller.py
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.wrappers.auth_wrapper import authentication_required
from ..constant import GET, POST, PUT, DELETE
from ..models import *
from api.errors.common import InternalServerError
from api.errors.core.grader_exception import GraderException
import api.services.{module}.{module}_service as {module}_service

@api_view([POST, GET])
@authentication_required
def all_{modules}_creator_view(request, account_id):
    try:
        if request.method == POST:
            result = {module}_service.create_{module}(account_id, request)
        elif request.method == GET:
            account = Account.objects.get(account_id=account_id)
            result = {module}_service.get_all_{modules}_by_account(account, request)
        return Response(result, status=200)
    except GraderException as ge:
        return ge.django_response()
    except Exception as e:
        return InternalServerError(e).django_response()

@api_view([GET, PUT, DELETE])
@authentication_required
def one_{module}_view(request, {module}_id: str):
    try:
        entity = {Module}.objects.get({module}_id={module}_id)
        if request.method == GET:
            result = {module}_service.get_{module}(entity)
        elif request.method == PUT:
            result = {module}_service.update_{module}(entity, request)
        elif request.method == DELETE:
            {module}_service.delete_{module}(entity)
            return Response(status=204)
        return Response(result, status=200)
    except GraderException as ge:
        return ge.django_response()
    except Exception as e:
        return InternalServerError(e).django_response()

# ... Add more controller functions as needed
```

**Controller Responsibilities:**
- HTTP method handling (`request.method == POST`)
- Model object retrieval (`{Module}.objects.get()`)
- Service layer calls (`{module}_service.function_name()`)
- Response formatting (`Response(result, status=200)`)
- Error handling (try/catch with proper error responses)
- Authentication decorators (`@authentication_required`)

### Step 4: Update URL Configuration

#### 4.1 Update Imports
```python
# api/urls.py
from django.urls import path
from .views import account, auth, script, submission, topic, collection, group  # Remove '{module}'
from .controllers import {module}_controller  # Add controller import
from api.controllers import account_controller, auth_controller
```

#### 4.2 Map URLs to New Controller
Replace all old view references with controller references:

```python
urlpatterns = [
    # Old pattern:
    # path('{modules}', {module}.all_{modules}_view),
    
    # New pattern:
    path('{modules}', {module}_controller.all_{modules}_view),
    path('{modules}/<str:{module}_id>', {module}_controller.one_{module}_view),
    path('accounts/<str:account_id>/{modules}', {module}_controller.all_{modules}_creator_view),
    # ... Add more URL mappings as needed
]
```

### Step 5: Clean Up Unused Imports

#### 5.1 Clean Service Layer Imports
Remove imports not used in business logic:

```python
# COMMONLY REMOVED from {module}_service.py:
from django.forms.models import model_to_dict  # Usually not needed
from api.utility import passwordEncryption      # Usually not needed in services
from rest_framework.response import Response    # Controllers handle responses
from rest_framework.decorators import api_view  # Controllers handle decorators
from rest_framework import status               # Controllers handle status codes
# Keep only imports used for business logic
```

#### 5.2 Clean Controller Layer Imports
Remove imports not used in HTTP handling:

```python
# COMMONLY REMOVED from {module}_controller.py:
from api.utility import *                      # Usually not needed in controllers
from api.sandbox.grader import *               # Service layer handles complex logic
from rest_framework import status              # If using hardcoded status codes
from django.forms.models import model_to_dict  # Usually not needed
from ..services.{module}.serializers import *  # Service layer handles serialization
# Keep only imports used for HTTP handling
```

### Step 6: Error Handling Enhancement

#### 6.1 Add Missing Error Classes
If needed, add error classes to `api/errors/common.py`:

```python
class BadRequestError(GraderException):
    def __init__(self, message: str = "Bad request"):
        super().__init__(message, 400)
```

#### 6.2 Update Service Error Handling
Replace generic responses with proper exceptions:

```python
# OLD (in original controllers):
return Response({'message': 'Error!'}, status=status.HTTP_400_BAD_REQUEST)

# NEW (in services):
raise BadRequestError('Error!')
```

### Step 7: Verification & Testing

#### 7.1 Check Linting
```bash
# Verify no linting errors
python manage.py check
```

#### 7.2 Verify URL Mappings
Ensure all endpoints still work:
- `GET /problems` 
- `POST /accounts/{id}/problems`
- `PUT /problems/{id}`
- etc.

#### 7.3 Test Service Independence
Verify services can be tested independently from HTTP layer.

## Function Mapping Reference

| Original View Function | New Controller Function | Service Function |
|------------------------|-------------------------|------------------|
| `{module}.all_{modules}_creator_view` | `{module}_controller.all_{modules}_creator_view` | `{module}_service.create_{module}` + `get_all_{modules}_by_account` |
| `{module}.one_{module}_creator_view` | `{module}_controller.one_{module}_creator_view` | `{module}_service.get_{module}` + `update_{module}` + `delete_{module}` |
| `{module}.{specific}_view` | `{module}_controller.{specific}_view` | `{module}_service.{specific}_function` |
| Add mappings for your specific module... | | |

## Benefits Achieved

### 1. **Separation of Concerns**
- Controllers: HTTP handling only
- Services: Business logic only
- Clear boundaries between layers

### 2. **Maintainability**
- Single location for all problem logic
- Easier to test business logic
- Clear dependency management

### 3. **Scalability**
- Easy to add new endpoints
- Service functions reusable across controllers
- Clear pattern for other modules

### 4. **Code Quality**
- Eliminated duplicate code
- Consistent error handling
- Clean import dependencies

## Next Steps

Apply the same refactoring pattern to other modules in your project:

### **Common Django Module Types:**
1. **Auth module** - Authentication and authorization
2. **Account/User module** - User management 
3. **Content modules** - Main business entities (Topic, Collection, Problem, etc.)
4. **Transaction modules** - Actions and processes (Submission, Order, etc.)
5. **Configuration modules** - Settings and metadata

### **Prioritization Strategy:**
1. Start with **core business modules** (most used entities)
2. **High-complexity modules** benefit most from this pattern
3. **Modules with many individual controller files** are good candidates
4. **Modules with mixed serializers** in main serializers.py

### **Module Selection Criteria:**
- Has individual function files in `controllers/{module}/`
- Functions mixed in `views/{module}.py`
- Related serializers scattered in main `serializers.py`
- Business logic mixed with HTTP handling

## Files Modified Summary

### Created (Per Module):
- `api/services/{module}/{module}_service.py` (Contains all business logic)
- `api/services/{module}/serializers.py` (Module-specific serializers)
- `api/controllers/{module}_controller.py` (HTTP handling only)

### Modified (Global):
- `api/urls.py` (Updated URL patterns to use controllers)
- `api/errors/common.py` (Add new error classes if needed)

### Pattern Established:
This refactoring creates a **reusable pattern** that can be applied to any Django module for better architecture and maintainability.

## Template Checklist for Each Module

- [ ] Identify all controller functions in `controllers/{module}/`
- [ ] Create service directory structure
- [ ] Extract functions to service layer (remove HTTP concerns)
- [ ] Create module-specific serializers
- [ ] Create controller layer with proper error handling
- [ ] Update URL patterns
- [ ] Clean up unused imports
- [ ] Test endpoints still work
- [ ] Verify service functions work independently

**Estimated Time Per Module**: 2-4 hours depending on complexity
