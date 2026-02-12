from django import template

register = template.Library()


@register.filter(name="get_item")
def get_item(dictionary, key):
    """
    Template filter to get an item from a dictionary
    Usage: {{ dictionary|get_item:key }}
    """
    return dictionary.get(key)


@register.filter(name="append")
def append_list(value, arg):
    """
    Template filter to append an item to a list
    Usage: {{ list|append:item }}
    """
    if value is None:
        value = []
    if isinstance(value, list):
        value.append(arg)
        return value
    return [value, arg]


@register.filter(name="filename")
def filename(value):
    """
    Template filter to extract just the filename from a path
    Usage: {{ file_path|filename }}
    """
    if value:
        return value.split("/")[-1]
    return value


@register.simple_tag(name="empty_list")
def empty_list():
    """
    Template tag to create an empty list
    Usage: {% empty_list as list_name %}
    """
    return []
