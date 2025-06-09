import inspect


def strict(func):    
    """Декоратор для строгой проверки типов аргументов"""
    annotations = func.__annotations__
    signature = inspect.signature(func)
    
    def wrapper(*args, **kwargs):
        bound_args = signature.bind(*args, **kwargs)
        arguments = bound_args.arguments
        
        for param_name, value in arguments.items():
            if param_name == 'return':
                continue
                
            expected_type = annotations.get(param_name)
            if expected_type is not None:
                actual_type = type(value)
                if actual_type is not expected_type:
                    raise TypeError(
                        f"Argument '{param_name}' must be "
                        f"{expected_type.__name__}, "
                        f"not {actual_type.__name__}"
                    )
        
        return func(*args, **kwargs)
    
    return wrapper