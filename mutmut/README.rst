mutmut - python mutation tester (Customized)

Requirements
------------

Mutmut must be run on a system with `fork` support. This means that if you want
to run on windows, you must run inside WSL.

------------

- **New Options for Mutmut Run:**  
    - Selective Line Mutation (--lines): You can now specify a comma-separated list of line numbers to mutate using the --lines option (e.g., --lines=10,12,15). Only mutations on these lines will be generated and tested, allowing for targeted mutation testing and faster feedback when working on specific code sections.
    - Test File Selection (--test-file): The --test-file option allows you to specify a single test file to copy and use during mutation testing, instead of copying all test files. This is helpful for focused testing or when working with large test suites.

- **Mutation Description Tracking:**  
  Each generated mutant now includes a detailed mutation description, including the line number and a unified diff showing the exact code change. This information is used to help users understand what each mutant does and is also exported for further analysis.

- **Survived Mutants Export:**  
  After running mutation testing, information about surviving mutants—including their mutation description, source file, and related tests—is saved to `mutants/survived_mutants.json`.


Install and run
---------------

You can get started with a simple:

.. code-block:: console

    pip install -e .
    mutmut run

This will by run pytest on tests in the "tests" or "test" folder and
it will try to figure out where the code to mutate is.


You can stop the mutation run at any time and mutmut will restart where you
left off. It will continue where it left off, and re-test functions that were
modified since last run.

To work with the results, use `mutmut browse` where you can see the mutants,
retest them when you've updated your tests.

You can also write a mutant to disk from the `browse` interface, or via
`mutmut apply <mutant>`. You should **REALLY** have the file you mutate under
source code control and committed before you apply a mutant!

Configuration
-------------

In `setup.cfg` in the root of your project you can configure mutmut if you need to:

.. code-block:: ini

    [mutmut]
    paths_to_mutate=src/
    tests_dir=tests/

If you use `pyproject.toml`, you must specify the paths as array in a `tool.mutmut` section:

.. code-block:: toml

    [tool.mutmut]
    paths_to_mutate = [ "src/" ]
    tests_dir = [ "tests/" ]

See below for more options for configuring mutmut.


Wildcards for testing mutants
-----------------------------

Unix filename pattern matching style on mutants is supported. Example:

.. code-block:: console

    mutmut run "my_module*"
    mutmut run "my_module.my_function*"

In the `browse` TUI you can press `f` to retest a function, and `m` to retest
an entire module.


"also copy" files
-----------------

To run the full test suite some files are often needed above the tests and the
source. You can configure to copy extra files that you need by adding
directories and files to `also_copy` in your `setup.cfg`:

.. code-block:: ini

    also_copy=
        iommi/snapshots/
        conftest.py


Limit stack depth
-----------------

In big code bases some functions are called incidentally by huge swaths of the
codebase, but you really don't want tests that hit those executions to count
for mutation testing purposes. Incidentally tested functions lead to slow
mutation testing as hundreds of tests can be checked for things that should
have clean and fast unit tests, and it leads to bad test suites as any
introduced bug in those base functions will lead to many tests that fail which
are hard to understand how they relate to the function with the change.

You can configure mutmut to only count a test as being relevant for a function
if the stack depth from the test to the function is below some limit. In your
`setup.cfg` add:

.. code-block:: ini

    max_stack_depth=8

A lower value will increase mutation speed and lead to more localized tests,
but will also lead to more surviving mutants that would otherwise have been
caught.


Exclude files from mutation
---------------------------

You can exclude files from mutation in `setup.cfg`:

.. code-block::

    do_not_mutate=
        *__tests.py


Whitelisting
------------

You can mark lines like this:

.. code-block:: python

    some_code_here()  # pragma: no mutate

to stop mutation on those lines. Some cases we've found where you need to
whitelist lines are:

- The version string on your library. You really shouldn't have a test for this :P
- Optimizing break instead of continue. The code runs fine when mutating break
  to continue, but it's slower.

If you wish to contribute to Mutmut, please see our `contributing guide <CONTRIBUTING.rst>`_.
