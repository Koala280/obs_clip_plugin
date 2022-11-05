import helpers as h

subscribers = dict()

def subscribe(event_type: str, fn):
    if not event_type in subscribers:
        subscribers[event_type] = []
    subscribers[event_type].append(fn)

def post(event_type: str):
    if not event_type in subscribers:
        h.err(f"Event Type {event_type} not existing!")
        return
    for fn in subscribers[event_type]:
        fn()