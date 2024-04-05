import json
import ast
from django.core.exceptions import ValidationError
from django.utils.dateparse import parse_datetime

from .utils import get_payload

'''
Instructions for usage

1.add schema decorator for every function views
e.g.
@schema(method='GET', schema=schemata.user_get_schema)
@schema(method='POST', schema=schemata.user_post_schema)
@schema(method='PUT', schema=schemata.user_put_schema)
@schema(method='DELETE', schema=schemata.user_delete_schema)
def user(request):
    pass


2.define schemata structure
user_get_schema = {
    'properties': {
        'user_id': '',
        'name': '',
        'group_name': 'group__name'
    },
    'required': ['user_id', 'name'],
    'data_field': ['username'],
    'int_field': ['year_born'],
    'float_field': ['age'],
    'bool_field': ['is_staff'],
}

3.find the schemas in the ./schema_type.py file or create your own schemas

'''
pagination_chema = {
    'sort': '',
    'search': '',
    'per_page': '',
    'page': '',
    'fields': '',
    'data_field': '',
}

filter_schema = {
    'filtered': ''
}

empty_schemas = {
    'properties': {}, 'required': [], 'bool_args': [], 'int_args': [], 'float_args': [],
}


def get_value(d, k, allow_null=False):
    if '.' not in k:
        value = d[k]
    else:
        v = d
        for _ in k.split('.'):
            v = v.get(_, {})
        value = v if v else ''
    return value if allow_null or value is not None else ''


def schema(method=None, schema=None, add_postdata=False, allow_null=False):
    def decorator(func):
        def wrapped_view(request, **kwargs):
            query_args = schema.get('properties', {})
            mandatory_args = schema.get('required', {})

            # if filtered:
            #     schema.get('properties', {}).update(filter_schema)
            # if pagination:
            #     schema.get('properties', {}).update(pagination_chema)

            if 'params' in kwargs:
                params = kwargs.pop('params', None)
            elif request.method == "GET":
                params = get_payload(request.GET, query_args)
            elif request.method == 'POST' and request.META.get('CONTENT_TYPE', '').startswith('multipart/form-data'):
                params = request.POST.dict()
                params = {query_args[f]: f'{get_value(params, f, allow_null)}' for f in query_args if
                          f.split('.')[0] in params}
            # else:  # elif request.method == "POST":
            elif request.body.startswith(b'{') and request.body.endswith(b'}'):
                post_data = json.loads(request.body)
                params = {query_args[f]: f'{get_value(post_data, f, allow_null)}' for f in query_args if
                          f.split('.')[0] in post_data}
                if add_postdata:
                    params['post_data'] = post_data
                # params = {query_args[f]: f'{params[f]}' if isinstance(params[f], dict)
                # else params[f] for f in query_args if f in params}
            else:
                params = {}
            if method is None or request.method == method:
                if any(f not in params for f in mandatory_args):
                    raise ValidationError(message='LACK_OF_ARGS')
            else:
                raise ValidationError(message='WRONG_METHOD_ARGS')

            for key in schema.get('bool_args', []):
                if key not in params:
                    continue
                params[key] = f'{params[key]}'.lower() == 'true'
            for key in schema.get('int_args', []):
                if key not in params:
                    continue
                params[key] = int(f'{params[key]}') if params[key] else params[key]
            for key in schema.get('float_args', []):
                if key not in params:
                    continue
                params[key] = float(f'{params[key]}') if params[key] else params[key]
            for key in schema.get('datetime_args', []):
                if key not in params:
                    continue
                params[key] = parse_datetime(params.get(key)),
            for key in schema.get('list_args', []):
                if key not in params:
                    continue
                if not isinstance(params[key], list):
                    if params[key].startswith('['):
                        params[key] = ast.literal_eval(params[key])
                    else:
                        params[key] = f'{params[key]}'.split(',')
                params[key] = [f'{_}' for _ in params[key]]

            return func(request, params=params, **kwargs)

        return wrapped_view

    return decorator
