CLASS_NAME_SEPARATOR = 'ǁ'

def build_trampoline(*, orig_name, mutants, class_name, is_generator):
    mangled_name = mangle_function_name(name=orig_name, class_name=class_name)

    mutants_dict = f'{mangled_name}__mutmut_mutants : ClassVar[MutantDict] = {{\n' + ', \n    '.join(f'{repr(m)}: {m}' for m in mutants) + '\n}'
    access_prefix = ''
    access_suffix = ''
    self_arg = ''
    if class_name is not None:
        access_prefix = f'object.__getattribute__(self, "'
        access_suffix = '")'
        self_arg = ', self'

    if is_generator:
        yield_statement = 'yield from '  # note the space at the end!
        trampoline_name = '_mutmut_yield_from_trampoline'
    else:
        yield_statement = ''
        trampoline_name = '_mutmut_trampoline'

    return f"""
{mutants_dict}

def {orig_name}({'self, ' if class_name is not None else ''}*args, **kwargs):
    result = {yield_statement}{trampoline_name}({access_prefix}{mangled_name}__mutmut_orig{access_suffix}, {access_prefix}{mangled_name}__mutmut_mutants{access_suffix}, args, kwargs{self_arg})
    return result 

{orig_name}.__signature__ = _mutmut_signature({mangled_name}__mutmut_orig)
{mangled_name}__mutmut_orig.__name__ = '{mangled_name}'
"""

def mangle_function_name(*, name, class_name):
    assert CLASS_NAME_SEPARATOR not in name
    if class_name:
        assert CLASS_NAME_SEPARATOR not in class_name
        prefix = f'x{CLASS_NAME_SEPARATOR}{class_name}{CLASS_NAME_SEPARATOR}'
    else:
        prefix = 'x_'
    return f'{prefix}{name}'

# noinspection PyUnresolvedReferences
# language=python
trampoline_impl = """
from inspect import signature as _mutmut_signature
try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated
from typing import Callable, ClassVar, Dict

MutantDict = Annotated[Dict[str, Callable], "Mutant"]

def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    \"""Forward call to original or mutated function, depending on the environment\"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result  # for the yield case
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result  # for the yield case
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result

"""
yield_from_trampoline_impl = trampoline_impl.replace('result = ', 'result = yield from ').replace('_mutmut_trampoline', '_mutmut_yield_from_trampoline')