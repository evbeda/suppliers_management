from django.contrib.auth.models import Group, Permission


def create_groups_and_apply_permisssions(group_permissions):

    for group_name, permissions in group_permissions.items():
        group, created = Group.objects.get_or_create(name=group_name)
        if not created:
            continue
        for permission in permissions:
            codename, name, content_type = permission
            perm, _ = Permission.objects.get_or_create(codename=codename, name=name, content_type=content_type)
            group.permissions.add(perm)
