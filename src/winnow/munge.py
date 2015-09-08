

def remove_key_named(node, key_name, collecting_node=None):

    if isinstance(node, dict):
        if key_name in node.keys():
            if collecting_node is not None:
                collecting_node[key_name] = node[key_name]
            del node[key_name]
        for key in node.keys():
            child = node[key]
            remove_key_named(child, key_name, collecting_node)
            if isinstance(child, dict) and len(child) == 0:
                del node[key]

    if isinstance(node, list):
        for i, child in enumerate(node[:]):
            remove_key_named(child, key_name, collecting_node)
            if isinstance(child, dict) and len(child) == 0:
                del node[key]