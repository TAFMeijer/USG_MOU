"""Fail readably when a page is running against a stale `mou_lib`.

Streamlit re-executes a page's script on every rerun but does not always reload
an imported local module. A commit that adds something to `mou_lib.py` AND uses
it from a page in the same commit can therefore run the new page against the old
module - and on Streamlit Cloud that surfaces as a redacted AttributeError or
KeyError with no hint of what to do about it. It has happened twice:
`palette()['country_order']` and `lib.rate_note`, both correct in the repo, both
missing from the module the running process had in memory.

Checking the names a page needs up front turns an opaque stack trace into an
instruction. Kept in its own module, and deliberately dependency-free, so the
check can never itself be the stale thing.
"""
import streamlit as st


def require(lib, *names: str) -> None:
    """Stop the page with a plain-language message if `lib` is missing `names`."""
    missing = sorted(n for n in names if not hasattr(lib, n))
    if not missing:
        return
    st.error(
        "**This page is running against an older version of `mou_lib` than it "
        "was built for.** Missing: "
        + ", ".join(f"`{n}`" for n in missing)
        + ".\n\nNothing is wrong with the data or with the deployed code - "
        "Streamlit re-executed the page without reloading the module. "
        "**Reboot the app** (*Manage app -> Reboot app* on Streamlit Cloud, or "
        "restart `streamlit run` locally) and it will come back."
    )
    st.stop()
