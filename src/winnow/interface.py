from winnow.exceptions import OptionsExceptionMissingInterfaceMethod

class OptionsInterface(object):


    def set_is_expanded(self):
        raise OptionsExceptionMissingInterfaceMethod("set_is_expanded")

    def set_doc_hash(self, hash):
        raise OptionsExceptionMissingInterfaceMethod("set_doc_hash")

    def get_doc_hash(self):
        raise OptionsExceptionMissingInterfaceMethod("get_doc_hash")

    def get_uuid(self):
        raise OptionsExceptionMissingInterfaceMethod("get_uuid")

    def add_history_action(self, action, output_type, input=None, scopes=None):
        raise OptionsExceptionMissingInterfaceMethod("add_history_action")

    def get_options_dict(self):
        raise OptionsExceptionMissingInterfaceMethod("get_options_dict")

    def set_doc(self, doc):
        raise OptionsExceptionMissingInterfaceMethod("set_doc")

    def get_doc(self):
        raise OptionsExceptionMissingInterfaceMethod("get_doc")

    def lookup(self, path):
        raise OptionsExceptionMissingInterfaceMethod("lookup")

    def clone_history_from(self, options_delegate):
        raise OptionsExceptionMissingInterfaceMethod("clone_history_from")

    def get_upstream(self):
        raise OptionsExceptionMissingInterfaceMethod("get_upstream")

    def history_is_empty(self):
        raise OptionsExceptionMissingInterfaceMethod("history_is_empty")





