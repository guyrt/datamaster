from .cache import cache
from .settings import settings


def set_branch(branch_name):
    b = cache.get_or_create_branch(branch_name)
    settings.active_branch = b.name
    settings.save()
    return b
