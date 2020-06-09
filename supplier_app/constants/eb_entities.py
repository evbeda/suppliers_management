from collections import namedtuple

DBTuple = namedtuple('DBTuple', 'value verbose_name')

EB_ENTITIES = {
    "1": DBTuple("1", "Eventbrite Argentina S.A."),
    "2": DBTuple("2", "Eventbrite Inc."),
}


def get_eb_entities():
    return [(eb_entity.value, eb_entity.verbose_name) for eb_entity in EB_ENTITIES.values()]
