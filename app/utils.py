import ast
from django.db.models import Q

emoji_mapping = {
    # Add your emoji mappings here
}

def parse_boolean_query(query, fields):
    terms = query.split()
    q_objects = Q()
    for term in terms:
        for field in fields:
            q_objects |= Q(**{f"{field}__icontains": term})
    return q_objects

def parse_emoji_reactions(raw_reactions):
    try:
        return ast.literal_eval(raw_reactions)
    except (ValueError, SyntaxError):
        return {}
