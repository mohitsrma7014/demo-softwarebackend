from django.db.models import Aggregate

class GroupConcat(Aggregate):
    function = 'GROUP_CONCAT'
    template = '%(function)s(DISTINCT %(expressions)s)'
