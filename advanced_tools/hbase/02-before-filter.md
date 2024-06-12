# Steps Before Filter

## Create some sample data

In this course, you need to execute the following code in the Django shell for better learning experience via `python manage.py shell`

Comment these two lines in `HBaseModel.create_table` function

```python
    if not settings.TESTING:
        raise Exception('You can only create tables in testing mode')
```

Add a create_table function first, then create the tables for the Friendships models

```python
from friendships.models import HBaseFollowing
from friendships.models import HBaseFollower
# import models 
HBaseFollowing.create_table()
HBaseFollower.create_table()
# create tables according the models
import time
def ts_now():
    return int(time.time() * 1000000)
# Give a function that can provde time utility
HBaseFollowing.create(from_user_id=1, to_user_id=2, created_at=ts_now())
HBaseFollowing.create(from_user_id=1, to_user_id=3, created_at=ts_now())
HBaseFollowing.create(from_user_id=1, to_user_id=4, created_at=ts_now())
HBaseFollowing.create(from_user_id=1, to_user_id=5, created_at=ts_now())
```

You can check HBase panel to check whether the data got created. 

You can also use the following code to get the data you created in shell

```python
from django_hbase.client import HBaseClient
from friendships.models import HBaseFollowing

prefix = b'1000000000000000:' # 15x0
table = HBaseFollowing.get_table()
rows = table.scan(row_prefix = prefix)
list(rows)

rows = table.scan(row_prefix = prefix)
for row_key, row_data in rows:
    print(row_key)
    print(row_data)
```

Then you should see

```python
[(b'1000000000000000:1717133960574585', {b'cf:to_user_id': b'0000000000000002'}), (b'1000000000000000:1717133963262555', {b'cf:to_user_id': b'0000000000000003'}), (b'1000000000000000:1717133966859392', {b'cf:to_user_id': b'0000000000000004'}), (b'1000000000000000:1717133968476508', {b'cf:to_user_id': b'0000000000000005'})]

b'1000000000000000:1717133960574585'
{b'cf:to_user_id': b'0000000000000002'}
b'1000000000000000:1717133963262555'
{b'cf:to_user_id': b'0000000000000003'}
b'1000000000000000:1717133966859392'
{b'cf:to_user_id': b'0000000000000004'}
b'1000000000000000:1717133968476508'
{b'cf:to_user_id': b'0000000000000005'}
```

## Understanding scan function in happybase

Let's understand the function with actualy data and code, using the data created above.

Please note, `happybase` have max connection duration and it will got cut after you don't use the connection shortly.
That's why we have provided the full block of code for each block below.  

```python
from django_hbase.client import HBaseClient
from friendships.models import HBaseFollowing
table = HBaseFollowing.get_table()
def print_rows(rows):
    for row_key, row_value in rows:
        print(row_key, row_value)
        
rows = table.scan()
print_rows(rows) # [1]

rows = table.scan(row_start=b'1000000000000000:1717133963262555')
print_rows(rows) # [2]

rows = table.scan(row_start=b'1000000000000000:1717133963262555', limit=2)
print_rows(rows) # [3]
```

Then you will see the output is like

```python
# [1]
b'1000000000000000:1717133960574585' {b'cf:to_user_id': b'0000000000000002'}
b'1000000000000000:1717133963262555' {b'cf:to_user_id': b'0000000000000003'}
b'1000000000000000:1717133966859392' {b'cf:to_user_id': b'0000000000000004'}
b'1000000000000000:1717133968476508' {b'cf:to_user_id': b'0000000000000005'}
# [2]
b'1000000000000000:1717133963262555' {b'cf:to_user_id': b'0000000000000003'}
b'1000000000000000:1717133966859392' {b'cf:to_user_id': b'0000000000000004'}
b'1000000000000000:1717133968476508' {b'cf:to_user_id': b'0000000000000005'}
# [3]
b'1000000000000000:1717133963262555' {b'cf:to_user_id': b'0000000000000003'}
b'1000000000000000:1717133966859392' {b'cf:to_user_id': b'0000000000000004'}
```

It is quite obvious that the data already sorted by row key in HBase DB.

Besides using the `row_start` and `limit`, you can also define a `row_prefix` to filter all the data with such prefix.

```python
from django_hbase.client import HBaseClient
from friendships.models import HBaseFollowing
prefix = b'1000000000000000:' # 15x0
table = HBaseFollowing.get_table()
def print_rows(rows):
    for row_key, row_value in rows:
        print(row_key, row_value)
        
rows = table.scan(row_prefix = prefix)
print_rows(rows) 

# b'1000000000000000:1717133960574585' {b'cf:to_user_id': b'0000000000000002'}
# b'1000000000000000:1717133963262555' {b'cf:to_user_id': b'0000000000000003'}
# b'1000000000000000:1717133966859392' {b'cf:to_user_id': b'0000000000000004'}
# b'1000000000000000:1717133968476508' {b'cf:to_user_id': b'0000000000000005'}
```

`row_stop` means where to stop, but with `limit`, you will find a trick thing:

```python
from django_hbase.client import HBaseClient
from friendships.models import HBaseFollowing
table = HBaseFollowing.get_table()
def print_rows(rows):
    for row_key, row_value in rows:
        print(row_key, row_value)

rows = table.scan(row_stop=b'1000000000000000:1717133966859392', limit=2)
print_rows(rows) # [1]

rows = table.scan(row_stop=b'1000000000000000:1717133968476508', limit=2)
print_rows(rows) # [2]
```

Output is like

```python
# [1]
b'1000000000000000:1717133960574585' {b'cf:to_user_id': b'0000000000000002'}
b'1000000000000000:1717133963262555' {b'cf:to_user_id': b'0000000000000003'}
# [2]
b'1000000000000000:1717133960574585' {b'cf:to_user_id': b'0000000000000002'}
b'1000000000000000:1717133963262555' {b'cf:to_user_id': b'0000000000000003'}
```

It means if you did not define the `row_start`, scan function will take the first row key as the start

If we only need the last 2 pieces of data, you need to use `reverse=True` while using the function.
By using `reverse`, you will find the `row_start` and `row_end` has also got reversed, which means `row_start` should take the newer value, or bigger number, while scanning.

```python
from django_hbase.client import HBaseClient
from friendships.models import HBaseFollowing
table = HBaseFollowing.get_table()
def print_rows(rows):
    for row_key, row_value in rows:
        print(row_key, row_value)

rows = table.scan(row_stop=b'1000000000000000:1717133968476508', limit=2, reverse=True)
print_rows(rows) # [1]

rows = table.scan(row_start=b'1000000000000000:1717133968476508', limit=2, reverse=True)
print_rows(rows) # [2]

prefix = b'1000000000000000:' # 15x0
rows = table.scan(row_prefix=prefix, limit=2, reverse=True)
print_rows(rows) # [3]
```

Output is like:

```python
# [1]
# Yes, no data 

# [2]
b'1000000000000000:1717133968476508' {b'cf:to_user_id': b'0000000000000005'}
b'1000000000000000:1717133966859392' {b'cf:to_user_id': b'0000000000000004'}
# Yes, and it is the reverse ordered 

# [3]
b'1000000000000000:1717133968476508' {b'cf:to_user_id': b'0000000000000005'}
b'1000000000000000:1717133966859392' {b'cf:to_user_id': b'0000000000000004'}
```
