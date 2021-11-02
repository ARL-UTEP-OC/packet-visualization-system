import os

import pytest

from packetvisualization.backend_components.table_backend import TableBackend


def test_gen_frame_string():
    list = []
    assert TableBackend.gen_frame_string(None, list) == [""]
    list = [1]
    assert TableBackend.gen_frame_string(None, list) == ['frame.number==1']
    list.clear()

    for i in range(252):
        list.append(i)
    assert TableBackend.gen_frame_string(None, list)[1] == 'frame.number==251'
    assert len(TableBackend.gen_frame_string(None, list)) == 2
    list.clear()

    for i in range(502):
        list.append(i)
    assert TableBackend.gen_frame_string(None, list)[2] == 'frame.number==501'
    assert len(TableBackend.gen_frame_string(None, list)) == 3

def test_convert_to_raw():
    assert TableBackend.convert_to_raw(None, "") == ""
    assert TableBackend.convert_to_raw(None, "A") == "41"
    assert TableBackend.convert_to_raw(None, "1") == "31"
    assert TableBackend.convert_to_raw(None, "Hello") == "48:65:6c:6c:6f"
    assert TableBackend.convert_to_raw(None, "123456AA") == "31:32:33:34:35:36:41:41"

def test_convert_to_ascii():
    assert TableBackend.convert_to_ascii(None, "") == ""
    assert TableBackend.convert_to_ascii(None, "A") == "65 "
    assert TableBackend.convert_to_ascii(None, "1") == "49 "
    assert TableBackend.convert_to_ascii(None, "Hello") == "72 101 108 108 111 "
    assert TableBackend.convert_to_ascii(None, "12345AA") == "49 50 51 52 53 65 65 "
