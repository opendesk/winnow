import hashlib
import json
import decimal
import uuid


def get_doc_hash(data):
    s = hashlib.sha1()
    s.update(data)
    return unicode(s.hexdigest())

def get_uuid():
    return unicode(uuid.uuid4())

"""
 Json encoding and decoding conventions
"""

class DecimalEncoder(json.JSONEncoder):
    """
    Patching the builtin jason encode to do decimals the way we want
    ie ints as nt ad floats as floats
    internally all numbers are stored as Decimals
    """

    def encode(self, o):
        if isinstance(o, list):
            return super(DecimalEncoder, self).encode(sorted(o))
        return super(DecimalEncoder, self).encode(o)


    def default(self, o):
        if hasattr(o, "__json__"):
            return o.__json__()
        if isinstance(o, decimal.Decimal):
            if o.to_integral_value() == o:
                return int(o)
            else:
                return float(o)
        return super(DecimalEncoder, self).default(o)


def json_loads(as_json):
    return json.loads(as_json, parse_float=decimal.Decimal, parse_int=decimal.Decimal)


def json_dumps(an_obj):
    return json.dumps(an_obj, indent=4, sort_keys=True, cls=DecimalEncoder)





