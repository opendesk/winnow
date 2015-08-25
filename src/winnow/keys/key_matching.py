import re
from winnow.exceptions import OptionsExceptionKeyError

class KeyMatcher():

    def __init__(self):
        self.options = {}
        pattern = "^[\*]$|^(([a-z0-9_-]+\/)*[a-z0-9_-]+)$|^([\*]\/[a-z0-9_-]+)$"
        self.prog = re.compile(pattern)

    @classmethod
    def from_dict(cls, d):
        m = cls()
        for k, v in d.iteritems():
            m.add_options(v, k)
        return m


    def add_options(self, option, key):
        self._add_options_paths(option, key)


    def _add_options_paths(self, option, key_path):
        self.set(key_path, option)

        def _add_it(v):
            if isinstance(v, dict):
                if "options" in v.keys():
                    for option_key, new_option in v["options"].iteritems():
                        new_key_path = "%s/%s" % (key_path, option_key)
                        self._add_options_paths(new_option, new_key_path)

        # the option is an object
        if isinstance(option, dict):
            # with values
            if "values" in option.keys():
                values = option["values"]
                if isinstance(values, dict):
                     _add_it(values)
                if isinstance(values, list):
                    for v in values:
                        _add_it(v)


    def _get_last(self, kp):
        return kp.split("/")[-1]


    def validate(self, kp):
        result = self.prog.match(kp)
        return result is not None


    def set(self, key_path, options):
        if not self.validate(key_path):
            raise OptionsExceptionKeyError("invalid key %s" % key_path)
        self.options[key_path] = options

    def get_matching_paths(self, key_path):
        if not self.validate(key_path):
            raise OptionsExceptionKeyError("invalid key %s" % key_path)
        matching = []
        for k in self.options.keys():
            if key_path == k:
                matching.append(k)
            if "*" in key_path or "*" in k:
                if self._get_last(key_path) == self._get_last(k):
                    matching.append(k)
        return matching


    def get(self, key_path):
        if not self.validate(key_path):
            raise OptionsExceptionKeyError("invalid key %s" % key_path)
        for k in self.options.keys():
            if key_path == k:
                return self.options[k]
            if "*" in key_path or "*" in k:
                if self._get_last(key_path) == self._get_last(k):
                    return self.options[k]
        return None

