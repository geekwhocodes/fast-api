import functools
from time import perf_counter, strftime


def timeit(func):
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        tic = perf_counter()
        value = func(*args, **kwargs)
        toc = perf_counter()
        elapsed_time = toc - tic
        print(
            f"\n{func.__name__!r} finished at {strftime('%l:%M%p %Z on %b %d, %Y') } in {elapsed_time:0.4f} seconds\n"
        )
        return value

    return wrapper_timer
