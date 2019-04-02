from for_runners.gpx import cutted_hash


def test_cutted_hash():
    assert cutted_hash("foobar", length=20) == "BJICMHV5DI4Q73JL6MTP"
    assert cutted_hash("foobar", length=10) == "BJICMHV5DI"
    assert cutted_hash("foobar", length=4) == "BJIC"
