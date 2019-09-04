hook_subscribers = {}
HOOK_BEFORE_LOAD = 'before_load'
HOOK_AFTER_LOAD = 'after_load'


def add_subscriber(subscriber, *hooks):
    for hook in hooks:
        if hook not in hook_subscribers:
            hook_subscribers[hook] = []
        hook_subscribers[hook].append(subscriber)


def emit_hook(hook, *payload):
    initial_payload = payload[0]
    try:
        for subscriber in hook_subscribers[hook]:
            initial_payload = getattr(subscriber, hook)(initial_payload)
        return initial_payload
    except KeyError:
        pass
