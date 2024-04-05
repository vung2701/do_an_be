from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core import serializers
import json
import base64
import ipaddress
import socket
import random
import string
from django.db import models

def b64encode(s):
    return base64.b64encode(s.encode('ascii')).decode('ascii')


def get_ip(domain):
    try:
        return socket.gethostbyname(domain)
    except Exception as ex:
        return domain


def get_domain(url):
    return url.strip().replace('http://', '').replace('https://', '').split('/')[0].split(':')[0]


def get_page(data, per_page, page_num):
    try:
        per_page = int(per_page) if per_page else 25
        page_num = int(page_num) if page_num else 1
        if per_page <= 0:
            per_page = len(data) + 1
    except Exception:
        per_page, page_num = 25, 1
    paginator = Paginator(data, per_page)
    try:
        page = paginator.page(page_num)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        page = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        page = paginator.page(paginator.num_pages)
    return page


def get_payload(request_get, query_args, bool_args=None, int_args=None, float_args=None):
    payload = {}
    for query_arg in query_args:
        filter_value = request_get.get(query_arg)
        if filter_value:
            filter_arg = query_args[query_arg] or query_arg
            payload[filter_arg] = filter_value
    if request_get.get('filtered'):
        filtered = request_get.get('filtered')
        filtered = [_.split('|') for _ in filtered.split(',')]
        filtered = {_[0]: _[1] for _ in filtered if len(_) == 2}
        for f_contain in filtered:
            filter_contain = '{0}__icontains'.format(query_args.get(f_contain) or f_contain)
            if f_contain not in query_args and filter_contain not in query_args:
                continue
            payload[filter_contain] = filtered[f_contain]
    if bool_args:
        for arg in bool_args:
            if arg in payload:
                payload[arg] = payload[arg].lower() == 'true'
    if int_args:
        for arg in int_args:
            if arg in payload:
                payload[arg] = int(payload[arg])
    if float_args:
        for arg in float_args:
            if arg in payload:
                payload[arg] = float(payload[arg])
    return payload


def obj_to_dict(obj):
    if hasattr(obj, 'to_dict'):
        return obj.to_dict()
    else:
        json_obj = json.loads(serializers.serialize('json', [obj]))[0].get('fields')
        json_obj['id'] = obj.id
        return json_obj


def get_fields(data, fields, to_dict_func=None):
    data = [_ for _ in data]
    if to_dict_func:
        return_data = [to_dict_func(_) for _ in data]
    else:
        return_data = [obj_to_dict(_) for _ in data]
    if not fields:
        return return_data
    return [{field: _.get(field) for field in fields} for _ in return_data]


def get_data_in_page_and_fields(model, model_name, payload, request_get, data_field=False, to_dict_func=None,
                                distinct=None, select_related=None, prefetch_related=None, addition_filter=None):
    if isinstance(model, models.QuerySet):
        filter_data = model.filter(**payload)
    else:
        filter_data = model.objects.filter(**payload)
    if request_get.get('sort'):
        sort = request_get.get('sort')
        if sort.startswith('['):
            sort = json.loads(request_get.get('sort'))
        else:
            sort = sort.split(',')
        filter_data = filter_data.order_by(*sort) if isinstance(sort, list) else filter_data.order_by(sort)
    if addition_filter:
        filter_data = filter_data.filter(addition_filter)
    if select_related:
        for _ in select_related:
            filter_data = filter_data.select_related(_)
    if prefetch_related:
        for _ in prefetch_related:
            filter_data = filter_data.prefetch_related(_)
    if distinct:
        filter_data = filter_data.distinct()
    total = filter_data.count()
    per_page = request_get.get('per_page')
    per_page = 25 if not per_page or not per_page.isdigit() else int(per_page)
    per_page = per_page if per_page > 0 else total + 1
    current_page = request_get.get('page')
    last_page = int((total - 1) / per_page) + 1 if per_page > 0 else 1
    current_page = 1 if not current_page or not current_page.isdigit() else int(current_page)
    current_page = last_page if current_page > last_page else current_page
    data = get_page(filter_data, per_page, current_page)
    data = get_fields(data, request_get.getlist('fields'), to_dict_func=to_dict_func)
    data_field = request_get.get('data_field', data_field)
    res = {
        model_name: data if not data_field else [],
        'data': data if data_field else [],
        'total': total,
        'from': (current_page - 1) * per_page + 1,
        'to': (current_page - 1) * per_page + len(data),
        'per_page': per_page,
        'current_page': current_page,
        'last_page': last_page,
    }
    return res


def is_ipv4(ip):
    try:
        _ip = ipaddress.ip_address(ip)
        ipv4 = True
    except ValueError:
        ipv4 = False
    except:
        ipv4 = False
    return ipv4


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_client_ips(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ips = x_forwarded_for.split(',')
    else:
        ips = [request.META.get('REMOTE_ADDR')]
    return ips


def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_letters
    result_str = ''.join(random.choice(letters) for i in range(length))
    # print("Random string of length", length, "is:", result_str)
    return result_str


def get_filename(filename, request):
    return filename.upper()
