import build2_orig
build2_orig.build()

import pytest

pytest.register_assert_rewrite("what2_utf_parse")
