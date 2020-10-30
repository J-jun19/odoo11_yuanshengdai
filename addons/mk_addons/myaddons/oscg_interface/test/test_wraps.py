from functools import wraps

def my_decorator(f):
    @wraps(f)
    def wrapper(*args,**kwds):
        print "Calling decorated function"
        f.env={
            "name":'lwt'
        }
        return f(*args,**kwds)
    return wrapper

@my_decorator
def example():
    """DocString"""
    print "Called example function"

example()
print example.__name__
print example.__doc__