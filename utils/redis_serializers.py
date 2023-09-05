from django.core import serializers
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
