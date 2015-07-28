# General functions used by all apps
import json
import random
import string

def random_string(N=8):
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(N))

def random_digits(N=5):
    return ''.join(random.choice(string.digits) for _ in range(N))

def getattr_str(obj, p):
    """ Returns value of p from obj following path split by . or __ """
    if p == 'self':
        return obj

    path = p.split('.' if '.' in p else '__', 1)
    attr = getattr(obj, path[0])
    return getattr_str(attr, path[1]) if len(path) > 1 else attr



