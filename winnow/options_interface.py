
from winnow.options_exceptions import OptionsExceptionMissingInterfaceMethod




class OptionsInterface(object):

    def set_is_snapshot(self):
        raise OptionsExceptionMissingInterfaceMethod("set_is_snapshot")

    def set_doc_hash(self, hash):
        raise OptionsExceptionMissingInterfaceMethod("set_doc_hash")

    def add_history_action(self, action_name, sieve_delegate):
        raise OptionsExceptionMissingInterfaceMethod("add_history_action")

    def get_options_dict(self):
        raise OptionsExceptionMissingInterfaceMethod("get_options_dict")

    def set_doc(self, doc):
        raise OptionsExceptionMissingInterfaceMethod("set_doc")

    def get_doc(self):
        raise OptionsExceptionMissingInterfaceMethod("get_doc")

    def clone_history_from(self, sieve_delegate):
        raise OptionsExceptionMissingInterfaceMethod("clone_history_from")

    def clone(self):
        """return a clone"""
        raise OptionsExceptionMissingInterfaceMethod("clone")

    def get_upstream(self):
        """
        returns the upstream delegate
        """
        raise OptionsExceptionMissingInterfaceMethod("get_upstream")







