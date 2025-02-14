from .schema_generator import ResponseSchemaGenerator

class CurrencyRefModel(ResponseSchemaGenerator):
    def __init__(
        self,
        name: str,
        value: str
    ):
        self.name = name
        self.value = value

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'value': self.value
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            name=data.get('name', ''),
            value=data.get('value', '')
        )

class MetaDataModel(ResponseSchemaGenerator):
    def __init__(
        self,
        CreateTime: str,
        LastUpdatedTime: str
    ):
        self.CreateTime = CreateTime
        self.LastUpdatedTime = LastUpdatedTime

    def to_dict(self) -> dict:
        return {
            'CreateTime': self.CreateTime,
            'LastUpdatedTime': self.LastUpdatedTime
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            CreateTime=data.get('CreateTime', ''),
            LastUpdatedTime=data.get('LastUpdatedTime', '')
        )


ERROR_RESPONSE = {
    'type': 'object',
    'properties': {
        'success': {'type': 'boolean'},
        'error': {'type': 'string'},
        'details': {'type': 'string'}
    }
}
