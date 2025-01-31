from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    return field.as_widget(attrs={'class': css_class})

@register.filter(name='percentage')
def percentage(value):
    """Convert float score to percentage string"""
    return f"{value * 100:.0f}%"

@register.filter(name='score_color')
def score_color(value):
    """Return Bootstrap color class based on score"""
    if value >= 0.8:
        return 'success'
    elif value >= 0.5:
        return 'info'
    elif value >= 0.3:
        return 'warning'
    return 'danger'
