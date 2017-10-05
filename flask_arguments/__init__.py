from flask import abort, request

LOCATIONS = ('args', 'json', 'headers', 'cookies')
DEFAULT_LOCATIONS = ('args', 'json')


def __get_all_args():
    return {
        'args': request.args.to_dict() if request.args else None,
        'json': request.get_json() if request.get_json() else None,
        # 'headers': request.headers.copy() if request.headers else None,
        # 'cookies': request.cookies.copy() if request.cookies else None
    }


def __get_arg(input_args, resolved_arg):
    arg = None
    locations = resolved_arg.get('locations', DEFAULT_LOCATIONS)
    for l in locations:
        arg = arg or input_args[l].get(resolved_arg['name'])
    if not arg and resolved_arg.get('is_required'):
        return abort(
            400,
            'Missing required argument: \'{}\' in {}.'.format(
                resolved_arg['name'], ', '.join(locations))
        )
    return arg or resolved_arg.get('default')


def __check_type(input_arg, resolved_arg):
    resolved_type = resolved_arg.get('type')
    if resolved_type:
        try:
            return resolved_type(input_arg)
        except (ValueError, TypeError):
            return abort(
                400,
                'Invalid argument type: \'{}\' must be \'{}\', not \'{}\'.'.format(
                    resolved_arg['name'],
                    resolved_type.__name__,
                    input_arg.__class__.__name__
                )
            )
    return input_arg


def __validate(input_arg, resolved_arg):
    validators = resolved_arg.get('validators', [])
    validation_res = input_arg
    for v in validators:
        validation_res = v(input_arg)
        if isinstance(validation_res, tuple) and validation_res[0] is None:
            return abort(
                400,
                'Invalid \'{arg_name}\' arg: \'{input_arg}\': {msg}.'.format(
                    arg_name=resolved_arg['name'],
                    input_arg=input_arg,
                    msg=validation_res[1]
                )
            )
    return validation_res


def parse_args(resolved_args):
    args = __get_all_args()
    result = {}

    for resolved_arg in resolved_args:
        input_arg = __get_arg(args, resolved_arg)  # required and default
        input_arg = __check_type(input_arg, resolved_arg)
        input_arg = __validate(input_arg, resolved_arg)
        result[resolved_arg['name']] = input_arg

    return result

