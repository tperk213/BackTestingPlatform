import inspect


def params_to_attr(func):
    def wrapper(*args, **kwargs):
        self_var = args[0]
        argSpec = inspect.getargspec(func)
        argNames = argSpec[0][1:]
        for key, _ in kwargs.items():
            if key in argNames:
                argNames.remove(key)
        argDict = zip(argNames, args[1:])
        self_var.__dict__.update(argDict)
        self_var.__dict__.update(kwargs)
        return func(*args, **kwargs)

    return wrapper


class my_test:
    @params_to_attr
    def __init__(self, first_arg, first_key_word_arg=24):
        self.fish = "salmon"


if __name__ == "__main__":

    my_obj = my_test(55, first_key_word_arg=39)
    print(my_obj.first_arg)
    print(my_obj.first_key_word_arg)

