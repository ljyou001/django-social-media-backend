from .fields import *
from .hbase_models import *

# __init__.py
# To collect the components in multiple files with in this folder
# So importer can just call django_hbase.models
# They don't need to go all the way to the original file

# You must use relative directory in __init__.py
# Only relative directory suggested
# Why?
# If we want to `from django_hbase.models import XXXException` in fields.py
# It will goes to this __init__.py file first
# While running, a circular import problem will hit.