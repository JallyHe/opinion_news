#-*-coding=utf-8-*-
# User: linhaobuaa
# Date: 2015-01-02 12:00:00
# Version: 0.1.0
"""处理演化过程中出错的话题
"""

from Database import EventManager, Event
from run import one_topic_calculation


def handle_error(eventid):
    """
    """
    event = Event(eventid)
    last_modify = event.getLastmodify()

    event.setLastmodify(last_modify - 3600)
    event.setModifysuccess(True)

    # one_topic_calculation((eventid, False))


if __name__ == '__main__':
    em = EventManager()
    # event_ids_list = em.getFalseEventIDs()
    event_ids_list = em.getAllEventIDs()
    map(handle_error, event_ids_list)

