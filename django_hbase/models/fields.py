class HBaseField:
    field_type = None

    def __init__(self, reverse=False, column_family=None):
        self.reverse = reverse
        self.column_family = column_family
        # TO DO
        # add is_required property using True by default
        # add default property using None by default
        # Handling above in HBaseModel and throw exceptions when needed

class IntegerField(HBaseField):
    field_type = 'int'

    def __init__(self, *args, **kwargs):
        super(IntegerField, self).__init__(*args, **kwargs)

class TimestampField(HBaseField):
    field_type = 'timestamp'

    def __init__(self, *args, auto_new_add=False, **kwargs):
        super(TimestampField, self).__init__(*args, **kwargs)


# column_family
# It can help you to split some column_keys and their values for data sharding
# So you can store the columns and their values into different HBase instances
# To fit your complicated query scenario:
# ABC columns are more likely used in case 1, DEF columns are more likely used in case 2...
# 
# In this project so far, we will set column_family as None by default or merge all into one
# Because we don't have complicated scenario currently


# reverse
# This is a important design to avoid hotspotting problem
# 
# for example
# row_key for Following/Follower (user_id, timestamp)
# since user_id is a increasing integer, newer use will have a larger number
# In most cases, newer ones are more active say following, tweeting...
# Since most of the newest data are in the newest HBase instance
# Then most of the request will goes to the newest HBase instance
# 
# Such high concentration to certain DB instances in data requsts led by the row key design is called hotspotting.
# 
# Since we will not send range queries to user_id but only use == for it
# So we can turn user_id from 000123 to 321000
# 
# Reverse user_id digit by digit will largely boost its performance
# DO NOT use reverse on row keys you need to make range query