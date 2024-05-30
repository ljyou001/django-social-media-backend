from django.conf import settings
from django_hbase.client import HBaseClient

from .exceptions import BadRowKeyError, EmptyColumnError
from .fields import HBaseField, IntegerField, TimestampField


class HBaseModel:

    class Meta:
        table_name = None
        row_key = ()

    @classmethod
    def get_table(cls):
        connection = HBaseClient().get_connection()
        if not cls.Meta.table_name:
            raise NotImplementedError('Missing table_name in HBaseModel meta class')
        return connection.table(cls.Meta.table_name)
    
    def __init__(self, **kwargs):
        for key, field in self.get_field_hash().items():
            value = kwargs.get(key)
            setattr(self, key, value) 
            # set key-values to __dict__ of this instance
            # Then you can access the value by self.key, say self.from_user_id

    @classmethod
    def get_field_hash(cls):
        """
        get field_hash
        :return: dict
        """
        field_hash = {}
        for field in cls.__dict__:
            field_obj = getattr(cls, field) # this equals to `cls.__dict__['field']`
            if isinstance(field_obj, HBaseField):
                field_hash[field] = field_obj
        return field_hash
    
    @classmethod
    def serialized_field(cls, field, value):
        """
        serialize value according to HBase design format
        mainly check whether it is need to reverse or fill-up 0s
        :param field: HBaseField
        :param value: any
        :return: bytes
        """
        value = str(value)
        if isinstance(field, IntegerField):
            value = str(value)
            while len(value) < 16:
                # This is to apply the fill-up 0s as we mentioned in study note
                # len(value) < 16: 8x digits more space efficiency
                value = '0' + value
        if field.reverse:
            # This is to apply the reverse as we mentioned in study note
            value = value[::-1]
        return value
    
    @classmethod
    def deserialize_field(cls, key, value):
        """
        deserialize value according to HBase design format
        :param key: HBaseField
        :param value: bytes
        :return: any
        """
        field = cls.get_field_hash()[key]
        if field.reverse:
            value = value[::-1]
        if field.field_type in [IntegerField.field_type, TimestampField.field_type]:
            return int(value)
        return value

    @classmethod
    def serialize_row_key(cls, data):
        """
        serialize dict of values to bytes (not str) in order to generate row keys
        {key1: val1} => b"val1"
        {key1: val1, key2: val2} => b"val1:val2"
        {key1: val1, key2: val2, key3: val3} => b"val1:val2:val3"
        REMEMBER: row key is storing the values

        NOTE: define in this way, it means that the values should not contain ":"

        classmethod?
        Yes, because we need to ensure this function is available even there is no instance
        Say, create or filter data

        :param data: dict
        :return: bytes

        What is field_hash?
        It it a hash table takes all the attributes(keys) and values of a model
        Take Friendship.HBaseFollowing as exameple: one of the field hash is
        {
            'from_user_id': 001, field_type = 'int', reverse = True
            'created_at': 1716511825, field_type = 'timestamp'
            'to_user_id': 002, field_type = 'int', column_family='cf'
        }
        """
        field_hash = cls.get_field_hash()
        values = []
        for key, field in field_hash.items():
            if field.column_family:
                continue
            value = data.get(key)
            if value is None:
                raise BadRowKeyError('Missing row key: {}'.format(key))
            # if there is no problem in row key
            value = cls.serialized_field(field, value)
            if ':' in value:
                raise BadRowKeyError(f'{key} should not contain ":" in value: {value}')
            values.append(value)
        return bytes(':'.join(values), encoding='utf-8')
    
    @classmethod
    def deserialize_row_key(cls, row_key):
        """
        deserialize row key to dict
        :param row_key: bytes
        :return: dict
        """
        data = {}
        if isinstance(row_key, bytes):
            # isinstance? in case you passed a instance manually created, rather than loaded from DB
            # bytes -> str
            row_key = row_key.decode('utf-8')

        row_key = row_key + ':' # val1:val2 -> val1:val2: for the convenience of finding
        for key in cls.Meta.row_key:
            index = row_key.find(':')
            if index == -1:
                # If you cannot find even one ':', .find() will return -1
                break
            data[key] = cls.deserialize_field(key, row_key[:index]) # get the value from start to the index
            row_key = row_key[index + 1:] # throw away the part of value we have already gotten
        return data

    @classmethod
    def serialize_row_data(cls, data):
        row_data = {}
        field_hash = cls.get_field_hash()
        for key, field in field_hash.items():
            if not field.column_family:
                # Skip the fields that are not in column family, which means in row key
                continue
            column_key = '{}:{}'.format(field.column_family, key)
            column_value = data.get(key)
            if column_value is None:
                continue
            row_data[column_key] = cls.serialized_field(field, column_value)
        return row_data
    
    @classmethod
    def init_from_row(cls, row_key, row_data):
        if not row_data:
            return None
        data = cls.deserialize_row_key(row_key)
        for column_key, column_value in row_data.items():
            column_key = column_key.decode('utf-8')
            key = column_key[column_key.find(':') + 1:]
            data[key] = cls.deserialize_field(key, column_value)
        return cls(**data)

    @property # <- used as a var in save()
    def row_key(self):
        return self.serialize_row_key(self.__dict__)
        # What is __dict__?
        # __dict__ is a special attribute of class, it is a dict that contains all the attributes of class
        # For example:
        # intance = HBaseFollowing()
        # instance.from_user_id = 1
        # instance.to_user_id = 2
        # instance.created_at = 123
        # print(instance.__dict__)
        # {'from_user_id': 1, 'to_user_id': 2, 'created_at': 123}

    def save(self):
        row_data = self.serialize_row_data(self.__dict__)
        if len(row_data) == 0:
            # If row_data is empty, it means no column key values need to be stored in HBase
            # In this case, HBase will not store anything and **ignore** the operation 
            # Here is a notice for user to avoid store empty value
            raise EmptyColumnError('Empty column data')
        table = self.get_table()
        table.put(self.row_key, row_data)

    # HBaseModel.create()
    # 1. Friendship.create(from_user_id=1, to_user_id=2, created_at=123)
    # 2. instance = HBaseModel(from_user_id=1, to_user_id=2, created_at=123)
    #     instance.save()
    # 3. instance.from_user_id = 2  # <- modify
    #     instance.save()
    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs) # <- pass to def __init__() of this class
        # instance = cls(kwargs) is wrong, since kwargs is a dict, it means only 1 parm was delivered
        instance.save()
        return instance
    
    # HBaseModel.get()
    # 1. Friendship.get(from_user_id=1, to_user_id=2,...)
    @classmethod
    def get(cls, **kwargs):
        row_key = cls.serialize_row_key(kwargs)
        table = cls.get_table()
        row = table.row(row_key)
        return cls.init_from_row(row_key, row)