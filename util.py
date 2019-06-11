def do_nothing_decorator(*_args, **_kws):
    def wrapper(f):
        return f

    if len(_args) > 0 and not callable(_args[0]) or len(_kws) > 0:
        return wrapper
    elif len(_args) == 0:
        return wrapper
    else:
        return _args[0]
