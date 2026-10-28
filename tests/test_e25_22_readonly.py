import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from e25_22_readonly import decode_shadows


def test_ids_required_before_using_shadow_bytes():
    assert decode_shadows([bytes([n, 0, n + 10, 0]) for n in range(3, 9)]) == [13, 14, 15, 16, 17, 18]
    with pytest.raises(ValueError):
        decode_shadows([b'\0\0\1\0'] * 6)
