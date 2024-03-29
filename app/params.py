import jsonschema
from jsonschema.exceptions import ValidationError


class PropertiesError(Exception):
    ...


def _parse_json(data: dict, schema: dict) -> dict:
    try:
        jsonschema.validate(data, schema)
        return data
    except ValidationError as error:
        message = error.message
        path_strs = map(lambda elem: f'"{elem}"' if isinstance(elem, str) else str(elem), error.path)
        path = f'[{"][".join(path_strs)}]'
        raise PropertiesError(f'{message} (path: {path})') from error


class Properties:
    __props_schema = {
        'type': 'object',
        'properties': {
            'rows': {
                'type': 'object',
                'properties': {
                    'height': {
                        'type': 'integer',
                        'minimum': 1
                    },
                    'spacing': {
                        'type': 'integer',
                        'minimum': 1
                    },
                    'critical_value_size': {
                        'type': 'integer',
                        'minimum': 1
                    }
                },
                'required': ['height', 'spacing'],
                'additionalProperties': False
            },
            'font': {
                'type': 'object',
                'properties': {
                    'size': {
                        'type': 'integer',
                        'minimum': 1
                    }
                },
                'required': ['size'],
                'additionalProperties': False
            },
            'mode': {
                'type': 'string',
                'enum': ['columns', 'rows']
            }
        },
        'required': ['rows', 'font', 'mode'],
        'additionalProperties': False
    }

    def __init__(self, data: dict):
        self.__props_data = _parse_json(data, self.__props_schema)

    @property
    def row_height(self) -> int:
        return self.__props_data['rows']['height']

    @property
    def rows_spacing(self) -> int:
        return self.__props_data['rows']['spacing']

    @property
    def critical_value_size(self) -> int:
        return self.__props_data['rows']['critical_value_size']

    @property
    def font_size(self) -> int:
        return self.__props_data['font']['size']

    @property
    def mode(self) -> str:
        return self.__props_data['mode']


class Messages:
    __msgs_schema = {
        'type': 'object',
        'properties': {
            'main_window_caption': {
                'type': 'string'
            }
        },
        'required': ['main_window_caption'],
        'additionalProperties': False
    }

    def __init__(self, data: dict):
        self.__msgs_data = _parse_json(data, self.__msgs_schema)

    def __getitem__(self, key: str) -> str:
        return self.__msgs_data[key]

    @property
    def main_window_caption(self) -> str:
        return self['main_window_caption']


class DataItem:

    def __init__(self, data: dict):
        self.__data = data

    @property
    def name(self) -> str:
        return self.__data['name']

    @property
    def value(self) -> str:
        return self.__data['value']


class DataGroup:

    def __init__(self, data: dict):
        self.__data = data

    @property
    def name(self) -> str:
        return self.__data['name']

    def __getitem__(self, index: int) -> DataItem:
        return DataItem(self.__data['data'][index])

    def __iter__(self):
        return map(lambda item: DataItem(item), self.__data['data'])

    def __len__(self):
        return len(self.__data)


class Data:
    __data_schema = {
        'type': 'array',
        'items': {
            'type': 'object',
            'properties': {
                'name': {
                    'type': 'string'
                },
                'data': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'name': {
                                'type': 'string'
                            },
                            'value': {
                                'type': 'string'
                            }
                        },
                        'required': ['name', 'value'],
                        'additionalProperties': False
                    },
                    'minItems': 1
                }
            },
            'required': ['name', 'data'],
            'additionalProperties': False
        },
        'minItems': 1
    }

    def __init__(self, data: dict):
        self.__data = _parse_json(data, self.__data_schema)

    def __getitem__(self, index: int) -> DataGroup:
        return DataGroup(self.__data[index])

    def __iter__(self):
        return map(lambda item: DataGroup(item), self.__data)

    def __len__(self):
        return len(self.__data)
