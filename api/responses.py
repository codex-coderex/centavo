"""
Shared response helpers for api/ functions.

Every api/ function returns one of these shapes so the frontend
always gets a consistent, JSON-safe object back from pywebview:

    ok(data)   -> {"ok": True, "data": data}
    fail(e)    -> {"ok": False, "error": str(e)}
"""


def ok(data=None):
    return {"ok": True, "data": data}


def fail(error):
    return {"ok": False, "error": str(error)}
