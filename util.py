def do_nothing_decorator(*args, **kwargs):
    def wrapper(f):
        return f

    if len(args) > 0 and not callable(args[0]) or len(kwargs) > 0:
        return wrapper
    elif len(args) == 0:
        return wrapper
    else:
        return args[0]
