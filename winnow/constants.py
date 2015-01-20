OPTIONS_KEY = u"options"

HISTORY_ACTION_CREATE = u"create"
HISTORY_ACTION_MERGE = u"merge"
HISTORY_ACTION_PATCH = u"patch"

# numbers
VALUE_TYPE_NUMERIC_NUMBER   = u"numeric::number"
VALUE_TYPE_NUMERIC_SET      = u"numeric::set"
VALUE_TYPE_NUMERIC_RANGE    = u"numeric::range"
VALUE_TYPE_NUMERIC_STEP     = u"numeric::step"

# choices
VALUE_TYPE_OPTION_STRING    = u"option::string"
VALUE_TYPE_OPTION_OBJECT    = u"option::object"
# really just objects but typed
VALUE_TYPE_OPTION_SIZE      = u"option::size"
VALUE_TYPE_OPTION_COLOUR    = u"option::colour"

# choices with members of a taxonomy
VALUE_TYPE_OPTION_MATERIAL  = u"option::material"
VALUE_TYPE_OPTION_FINISH    = u"option::finish"

MAX_VALUE_SET_SIZE = 1000000