import json
from typing import Any, Dict


def canonical_json(data: Dict[str, Any]) -> bytes:
    """
    Produces deterministic canonical JSON byte representation (Section 7):
    - Keys sorted lexicographically
    - Compact separators (',', ':')
    - UTF-8 encoded
    - Non-ASCII characters preserved
    """
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
