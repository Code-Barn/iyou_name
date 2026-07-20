from django import template

from apps.generator.utils.prototype.date_utils import format_date, DateFormat

register = template.Library()


@register.filter(name="get_item")
def get_item(dictionary, key):
    """
    Template filter to get an item from a dictionary
    Usage: {{ dictionary|get_item:key }}
    """
    return dictionary.get(key)


@register.filter(name="get_name")
def get_name(ind_id, individuals_dict):
    """
    Template filter to get an individual's full name from their ID
    Usage: {{ ind_id|get_name:individuals_dict }}
    """
    if ind_id and individuals_dict:
        individual = individuals_dict.get(ind_id)
        if individual:
            return individual.full_name
    return ""


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


@register.filter(name="format_date")
def format_date_filter(date_str):
    """
    Template filter to format a date string to "19 Oct 1990" format.
    Usage: {{ date_str|format_date }}
    """
    if not date_str:
        return ""
    return format_date(date_str, DateFormat.DA_MON_YEAR)


@register.simple_tag(name="count_spouse_children")
def count_spouse_children(spouse_id, spouse_children_ids, individuals_dict):
    """
    Template tag to count children excluding step/adopted/foster children of the spouse.
    Usage: {% count_spouse_children spouse.id children_list individuals_dict as count %}
    """
    if not spouse_id or not spouse_children_ids or not individuals_dict:
        return 0
    count = 0
    for child_id in spouse_children_ids:
        child = individuals_dict.get(child_id)
        if child:
            step_parents = getattr(child, "step_parents", None) or []
            adoptive_parents = getattr(child, "adoptive_parents", None) or []
            foster_parents = getattr(child, "foster_parents", None) or []
            if (
                spouse_id not in step_parents
                and spouse_id not in adoptive_parents
                and spouse_id not in foster_parents
            ):
                count += 1
    return count
