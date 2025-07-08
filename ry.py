def handle_input(input_string, input_limits, parse=str, in_or_not=True):
    while True:
        try:
            handled_input = parse(input(input_string))
            if (handled_input in input_limits) == in_or_not:
                return handled_input
        except:
            continue

def dict_enum(input):
    return dict(enumerate(input))

def range_len(input):
    return range(len(input))