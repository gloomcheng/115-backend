"""The harness track: units 10 through 17, and the final project.

The package grows every unit from 10 to 17. Each unit adds one module and
one rule. The rule is the point; the module is where it lives.

    unit 10  validation.py, events.py   a result that fails the check never reaches the log
    unit 11  authz.py                   a request carries a role, and the role is checked
    unit 12  host.py, state.py          every call goes through the same chain
    unit 13  tests/test_state.py        the replay rules, written as assertions
    unit 14  tools.py                   adding a tool is adding an entry
    unit 15  trace.py                   one id follows a request into the log
    unit 16  Dockerfile                 the harness as one image
    unit 17  deploy/                    the harness as a service that stays up
    final    checkpoint.py, appendix.py the task list exists exactly once
"""
