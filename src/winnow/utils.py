import hashlib
import ujson as json
import decimal
import uuid
import cPickle
import copy


def get_doc_hash(data):
    s = hashlib.sha1()
    s.update(data)
    return unicode(s.hexdigest())

def get_uuid():
    return unicode(uuid.uuid4())

def json_loads(as_json):
    return json.loads(as_json)

def json_dumps(an_obj):
    return json.dumps(an_obj,  indent=4, sort_keys=True)

def to_decimal(float_or_int):
    return decimal.Decimal(str(float_or_int))

def from_decimal(as_decimal):
    if as_decimal.to_integral_value() == as_decimal:
        return int(as_decimal)
    else:
        return float(as_decimal)

def deep_copy_dict(as_dict):
    # return copy.deepcopy(as_dict)
    return cPickle.loads(cPickle.dumps(as_dict, -1))