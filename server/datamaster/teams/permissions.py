from .models import Membership, MembershipType


def grant_access(user, team, relationship_type=MembershipType.EDIT):
    m, created = Membership.objects.get_or_create(user=user, team=team, defaults={'relationship_type': relationship_type})
    if not created and m.relationship_type != relationship_type:
        m.relationship_type = relationship_type
        m.save()
    return m


def has_access(user, team):
    return Membership.objects.filter(user=user, team=team).exists()