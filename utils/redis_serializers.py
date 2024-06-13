import json

from django.core import serializers
from django_hbase.models import HBaseModel
from utils.json_encoder import JSONEncoder


class DjangoModelSerializer():
    
    @classmethod
    def serialize(cls, instance):
        return serializers.serialize('json', [instance], cls=JSONEncoder)
        # serialize(format, querytset or list, cls: encoder class)
        # After execute this function, it will return a string
    
    @classmethod
    def deserialize(cls, serialized_data):
        return list(serializers.deserialize('json', serialized_data))[0].object
        # list(deserialize(format, string)[0]) is to obtain the "[instance]" above
        # This will return a DeserializedObject object
        # DeserializedObject object has two attributes: "object" and "m2m_data"
        # "object" is the instance of the object, thus, we need to ".object"


class HBaseModelSerializer:

    @classmethod
    def get_model_class(cls, model_class_name):
        for subclass in HBaseModel.__subclasses__():
            # Find all the HBase models, since not too many
            if subclass.__name__ == model_class_name:
                # If the model_class_name is same as the model name, then return
                return subclass
        raise Exception('HBaseModel {} not found'.format(model_class_name))
    
    @classmethod
    def serialize(cls, instance):
        json_data = {'model_class_name': instance.__class__.__name__}
        # model_class_name: find which model
        for key in instance.get_field_hash():
            # get_field_hash: get all the fields in the HBase model
            value = getattr(instance, key) # get key-value
            json_data[key] = value  # add the key-value into the json data
        return json.dumps(json_data) # Turn dict to string-formatted json
    
    @classmethod
    def deserialize(cls, serialized_data):
        json_data = json.loads(serialized_data)
        model_class = cls.get_model_class(json_data['model_class_name'])
        del json_data['model_class_name']
        # model_class is already a class created by the previous function:
        # model_class = HBaseModel # means
        # model_class(...) == HBaseModel(...)
        return model_class(**json_data)