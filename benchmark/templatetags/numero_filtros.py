from django import template

register = template.Library()


@register.filter
def ms_para_s(valor_ms):
    try:
        return float(valor_ms) / 1000.0
    except (TypeError, ValueError):
        return 0.0


@register.filter
def ms_para_min(valor_ms):
    try:
        return float(valor_ms) / 60000.0
    except (TypeError, ValueError):
        return 0.0
