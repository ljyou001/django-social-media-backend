# HBase

## Understand Distributed and Non-relational DB

### Why Distributed Database?

We want to use multiple database instances to serve the queries to the database, rather than 1.

The process to split data into multiple instance also called data sharding or sharding.

Normally, we have vertical sharding and horizontal sharding:

- Vertical sharding: split data by table/columns
  - User table in instance 1, Tweet table in instance 2
  - UserProfile split into UserPreference and UserProfile
- Horizontal sharding: split DB rows into multiple tables
  - NewsFeed(user_id, tweet_id, timestamp)
    - user_id % 10: =0 to instance 0, =1 go to instance 1...
    - user_id here is called sharding key/row keyhash key/partition key
    - Why normally use user_id?
    - Because most actions involves user and many entities are the record of user. One user does not have a heavy operation load, thus, sharding in this way could have a better distribution. During the split, we don't want all requests still goes to one DB during the production, therefore, it is very important to select your sharding key based on the business and code logic.
  - Consistent Hashing

MySQL and etc. also supports distributed but just have a lot of work to do.

### Why Non-relational DB?

Just like MySQL, relational DBs shows data in tables.

However, data in non-relational databases are stored in key-value forms:

1. key-value
   1. Redis
   2. RocksDB
2. Key-document, document based
   1. MongoDB
3. Key-key-value, wide-column or column based
   1. HBase
   2. BigTable
   3. Cassandra
   4. DynamoDB

There also a [ranking table](https://db-engines.com/en/ranking) for popular databases and many of them are non-relational DB.

Most non-relational databases are distributed. That's why some of companies will just use a non-relational DB rather than using the relational DBs.

Non-relational databases is a good fit for the following scenarios:

1. Simple data structure
2. Large amount of data
3. Write a lot, but read little
4. Queries are not complex

## What is HBase?

HBase is an non-relational key-value distributed database.

### Why HBase?

1. Easy structure: High performance and High Concurrency
2. Distrubuted design: Good security
3. Prioritize write operation: best for write more, read less. (cache inverse)

Why not Redis:

1. Take Newsfeed as example, its structure is <user_id, timestamp, tweet_id>
2. If it is stored in Redis, it should be like `key = "newsfeeds::<user_id>"` and `value = list(<timestamp, tweet_id>)`
3. If I would like to make a range query based on `timestamp`, Redis cannot help us with it

In MySQL, indexed columns are sorted in B+ Tree, therefore, it supports range query.

### How does the wrtie prioritization work?

1. Among multiple HBase instances, data are hashed and distrubuted in the instances
2. New inserted data will not immediately added into the hashed instance immediately
3. It will goes to a new instance, using Skiplist, to append the new data in the new instance
4. While reading, the system need to check two pieces of data based on timestamp and return the newest

### Learning suggestion

1. Read - Bigtable: A Distributed Storage System for Structured Data
2. Read - HDFS

```shell
 /  GFS   ->  Big table  ->   Map reduce
/
\
 \  HDFS  ->  HBase      ->   Hadoop MapReduce
```

### About the Key-value storage in HBase

1. Basically it is the hash-table in a hard-drive
2. In HBase, there is a row key, in string, you can take it as the key in key-value
3. There is another hastable in HBase, which is row key to column key, then column keys are mapping to values, which is just like:

    ```python
    value = hashtable['row_key']['column_key']
    ```

    or in Java

    ```java
    HBase = TreeMap<String, HashMap<String, String>>
    //      row_key(sorted)   column_key(unsorted)
    ```

Therefore:

1. All instances and data are sorted in row key
2. Column keys are unsorted and there could be multiple column keys under row key
3. We can make range query for row key but column key cannot

**Example: Tweet in HBase and MySQL**

In HBase

| `row_key = {user_id} + {timestamp}` | `row_data = {'content': <content>, 'likes_count': <likes_count>, 'comments_count': <comments_count>}` |
| --------------------------------- | --------------------------------------------------------------------------------------------------- |
| `"00123+20240528-12:15:28"`       | `{'content': "hello", 'likes_count': 5, 'comments_count': 1}`                                         |
| `"00321+20240529-15:22:43"`       | `{'content': "world", 'likes_count': 2, 'comments_count': 0}`                                         |

NOTE:

1. Row keys are selected based on the what columns you want to make range query
2. Row keys must be in same length if you want to have a valid range query, you need to fill-up user_id before it add one more digit
3. Structural or fill-up modification in row keys will cause a whole table migration, you cannot update on the existing table
4. Row key is the primary key equivalence in HBase, it could be non-unique. 
    - That's why we need a precise timestamp here in the project
    - Another solution in real world is to use [snowflake algorithm](https://github.com/search?q=snowflake&type=repositories)
        - Why still use UUID more widely rather than snowflake in real world: Safety concern: UUID does not contain timestamp, worker number or serial number
        

In MySQL

| id(pk) | user_id | content | likes_count | comments_count |
| ------ | ------- | ------- | ----------- | -------------- |
| 100    | 123     | hello   | 5           | 1              |
| 200    | 321     | world   | 2           | 0              |

### Designing techniques for HBase

#### Reversing

This is a important design to avoid hotspotting problem

for example:
row_key for Following/Follower (user_id, timestamp)
since user_id is a increasing integer, newer use will have a larger number
In most cases, newer ones are more active say following, tweeting...
Since most of the newest data are in the newest HBase instance.
Then most of the request will goes to the newest HBase instance.

In a distributed database, a **hotspot** is an overworked node – in other words, a part of the database that’s processing or storing a greater share of the total workload than it is meant to handle.

Since we will not send range queries to user_id but only use == for it
So we can turn user_id from 123 to 321

Reverse user_id digit by digit will largely boost its performance

**What to reverse**

The value in raw key that:

1. Timely related
    - newer user have a larger user_id
2. No need to support range query
    - all qeueries related to user_id are `==`

DO NOT use reverse on row keys you need to make range query

#### Fill-up 0s

Row key's type is string. If you want to have valid sorting, then all the strings must be at the same length. 
Thus, we need to add enough 0s to the row key.

For example, `"23"` is larger than `"123"` while sorting, but `"023"` < `"123"`

#### Salting

Salting means to add fixed length and random characters/digits as row key's prefix.

It can preserve the order and solve the hotspot problem.

But, it will cause a longer query time while making range query.

```python
For example
To find range_query(123*), you need to find
 - range_query(a123*)
 - range_query(b123*)
 - ...
 - range_query(z123*)
```

In some cases, we will take some part of the row key to hash, and make the hashed value as prefix. 

`new_row_key = hash(old_row_key) + old_row_key`

But still, it is more difficult to find the prefix using this salting method.

#### Summary and Compare to Cassandra

It is very important to design a good row key based on the usage in HBase.

Compare to Cassandra

HBase is using `TreeMap<String, HashMap<String, String>>`

Cassandra is `HashMap<String, TreeMap<String, String>>`

This means Cassandra requires you split part of row key in HBase into `==` query, to determine which DB node to store the data.

Second `String` in `HashMap<String, TreeMap<String, String>>` of Cassandra usually still a seralized dict. Therefore, in the real world usage, Cassandra is like `HashMap<String, TreeMap<String, HashMap<String, String>>>`

example:

```shell
HBase: Tweet
    row key: (user_id, timestamp)
    row data: {        # unsorted / hash table
        column key: ...
        column value: ...
    }
Cassandra: Tweet
    row key (hash key): user_id # <- must be == query
    column key: timestamp  # <- range query
    value: dict(row_data) # <- row data in HBase
```

## Deploy HBase

We will apply HBase to Friendship relationship.

### Install HBase

1. Download JDK from Oracle and Install it

    ```shell
    sudo mkdir /usr/lib/jvm
    sudo tar -zxvf jdk-8u401-linux-x64.tar.gz -C /usr/lib/jvm
    ```

2. Update the environoment by `sudo vi ~/.bashrc`, then `source ~/.bashrc`

    ```shell
    export JAVA_HOME=/usr/lib/jvm/jdk1.8.0_401
    export JRE_HOME=${JAVA_HOME}/jre
    export CLASSPATH=.:${JAVA_HOME}/lib:${JAVA_HOME}/lib
    export PATH=${JAVA_HOME}/bin:$PATH
    ```

    If successfully configured, you should see

    ```shell
    $ java -version
    java version "1.8.0_401"
    Java(TM) SE Runtime Environment (build 1.8.0_401-b10)
    Java HotSpot(TM) 64-Bit Server VM (build 25.401-b10, mixed mode)
    $ javac -version
    javac 1.8.0_401
    ```

3. Then, Download [HBase from apache](https://downloads.apache.org/hbase/) and extract, it can be directly used

    ```shell
    tar -xvzf hbase-2.6.0-bin.tar.gz
    cd hbase-2.6.0
    ```

4. Link JDK and HBase at `./hbase/conf/hbase-env.sh`, and put the JAVA_HOME into the shell

5. Go to `./hbase/conf/hbase-site.xml` and add the following lines into the configuration section:

    ```xml
    <property>
        <name>hbase.rootdir</name>
        <value>file:///home/ljyou001/hbase</value>
    </property>
    <property>
        <name>hbase.zookeeper.property.dataDir</name>
        <value>/home/ljyou001/zookeeper</value>
    </property>
    ```

    NOTE: `file:` follows with 3 `/` not 2 `/`

6. Start HBase, then you can access the system at 16010 port (by default, could be others)

    ```shell
    sudo ./bin/start-hbase.sh
    ```

7. Use `./bin/hbase shell` to open its shell

### Install Thrift

After HBase installed, you need a tool called `Thrift` to communicate HBase with Python (or other languages)

Thrift is a RPC, remote procedure call, interface. RPC means functions can be remotely called, executed and returned.

Why not HTTP? HTTP is a special type of RPC, it is too heavy for such operations.

1. Firstly [download](https://thrift.apache.org/download)

    ```shell
    wget http://archive.apache.org/dist/thrift/0.14.1/thrift-0.14.1.tar.gz
    tar -xvzf thrift-0.14.1.tar.gz
    sudo apt-get install automake bison flex g++ git libboost-all-dev libevent-dev libssl-dev libtool make pkg-config
    ```

    if got problem you can also follow these [steps](https://www.reddit.com/r/GNURadio/comments/9f8t0i/building_thrift_for_performance_counters_on/)

2. Then make install, Thrift need you to compile yourself.

    ```shell
    cd thrift-0.14.1
    ./configure
    make
    make install
    ```

3. Launch Thrift service for HBase

    ```shell
    bin/hbase-daemon.sh start thrift
    ```

### Install happybase for Python

1. Connect python and HBase with happybase

    ```shell
    pip install happybase
    ```

2. Ensure Hbase and Thrift are running and test

    ```python
    >>> import happybase
    >>> connection = happybase.Connection('0.0.0.0')
    >>> print(connection.tables())
    []
    >>> families = {'cf': dict()}
    >>> connection.create_table('mytable', families)
    >>> print(connection.tables())
    [b'mytable']
    ```
