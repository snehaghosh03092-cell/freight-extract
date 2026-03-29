from collections import defaultdict


def build_port_lookup(port_list):
    """
    name → code mapping (case-insensitive)
    """
    lookup = defaultdict(set)

    for item in port_list:
        name = item["name"].strip().lower()
        code = item["code"].strip()

        lookup[name].add(code)

    return lookup