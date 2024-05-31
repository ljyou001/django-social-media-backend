from django_hbase import models


class HBaseFollowing(models.HBaseModel):
    """
    Store from_user_id's following, row_key is sorted by from_user_id + created_at

    which means it can support
     - one's following list sorted by time
     - one's following list in a range of time
     - one's following after/before a certain time
    """
    # row keys
    from_user_id = models.IntegerField(reverse=True)
    created_at = models.TimestampField()
    # column keys
    to_user_id = models.IntegerField(column_family='cf')

    class Meta:
        table_name = 'twitter_followings'
        row_key = ('from_user_id', 'created_at')
        # The order of row_key is important since we need to confirm 
        # which one uses `==` operation and which one uses range query

class HBaseFollower(models.HBaseModel):
    """
    Store from_user_id's followers/fans, row_key is sorted by to_user_id + created_at

    which means it can support
     - one's follower list sorted by time
     - one's follower list in a range of time
     - one's follower after/before a certain time
    """
    # row keys
    to_user_id = models.IntegerField(reverse=True)
    created_at = models.TimestampField()
    # column keys
    from_user_id = models.IntegerField(column_family='cf')

    class Meta:
        table_name = 'twitter_followers'
        row_key = ('to_user_id', 'created_at')


# Comparing the normal model with this one, you will find:
# In HBase, although two pieces of data are same
# But to support two sorting requirement, we need to use two tables to store the data
# Actually, this is similar as indices of relational database, which also requires 2 index tables for data sorting.