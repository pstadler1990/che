hook_subscribers = {}
HOOK_BEFORE_LOAD = 'before_load'


def add_subscriber(subscriber, *hooks):
    for hook in hooks:
        if hook not in hook_subscribers:
            hook_subscribers[hook] = []
        hook_subscribers[hook].append(subscriber)


def emit_hook(hook, *payload):
    for subscriber in hook_subscribers[hook]:
        getattr(subscriber, hook)(payload[0])
