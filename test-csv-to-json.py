from csvtojson import parse_number, parse_numbers_compound_list, make_related_list_key, transpose_compound_list, reformat_compound_list, change_file_extension, group_related_list_values, conditionally_add_quotes
import pytest

def test_parse_number():
    assert parse_number("5") == 5
    assert parse_number("one") == "one"
    assert parse_number("5.6") == 5.6

def test_parse_numbers_compound_list():
    assert parse_numbers_compound_list([["5", "6", "7.1"], ["one", "two"]]) == [[5, 6, 7.1], ["one", "two"]]
    assert parse_numbers_compound_list([["5", "2.15"], ["three", "hi"]]) == [[5, 2.15], ["three", "hi"]]

def test_make_related_list_key():
    assert make_related_list_key(["one", "two", "three", "", ""]) == {"one": 0, "two": 0, "three": 3}
    assert make_related_list_key(["two", "", "three", "", ""]) == {"two": 2, "three": 3}

def test_group_related_list_values():
    assert group_related_list_values([["one", 2, 3], ["four", 5, 6]], {"str": 0, "int": 2}) == [["one", [2, 3]], ["four", [5, 6]]]
    assert group_related_list_values([["one", 2, ""], ["four", 5, 6]], {"str": 0, "int": 2}, 1) == [["one", [2]], ["four", [5, 6]]]
    assert group_related_list_values([["one", 2, ""], ["four", "two", ""]], {"str": 0, "int": 2}, 0) == [["one", [2, ""]], ["four", ["two", ""]]]

def test_transpose_compound_list():
    assert transpose_compound_list([["one", "2", "3.2"], ["four", "5", "6.4"]], ["str", "int", "float"]) == [{"one": "2", "four": "5"}, {"one": "3.2", "four": "6.4"}]
    assert transpose_compound_list([["one", ["2", "3.2"]], ["four", [5, "6.4"]]], ["str", "num"], keep_inside_array=True, include_keys=True) == [["one", "four"], [["2", "3.2"], [5, "6.4"]]]
    assert transpose_compound_list([["one", ["2", "3.2"]], ["four", ["5", 6.4]]], ["str", "num"], keep_outside_object=True, keep_inside_array=True, include_keys=True) == {"str": ["one", "four"], "num": [["2", "3.2"], ["5", 6.4]]}
    assert transpose_compound_list([["one", ["2", "3.2"]], ["four", ["5", "6.4"]]], ["str", "num"], keep_outside_object=True, include_keys=True) == {'str': {'one': 'one', 'four': 'four'}, 'num': {'one': ['2', '3.2'], 'four': ['5', '6.4']}}
    

def test_reformat_compound_list():
    assert reformat_compound_list([["one", "2", "3.2"], ["four", "5", "6.4"]], ["str", "int", "float"]) == [{"int": "2", "float": "3.2"}, {"int": "5", "float": "6.4"}]
    assert reformat_compound_list([["one", "2", "3.2"], ["four", "5", "6.4"]], ["str", "int", "float"], include_keys=True) == [{"str": "one", "int": "2", "float": "3.2"}, {"str": "four", "int": "5", "float": "6.4"}]
    assert reformat_compound_list([["one", "2", "3.2"], ["four", "5", "6.4"]], ["str", "int", "float"], include_keys=True, keep_inside_array=True) == [["one", "2", "3.2"], ["four", "5", "6.4"]]
    assert reformat_compound_list([["one", "2", "3.2"], ["four", "5", "6.4"]], ["str", "int", "float"], keep_outside_object=True) == {"one": {"int": "2", "float": "3.2"}, "four": {"int": "5", "float": "6.4"}}

def test_change_file_extension():
    assert change_file_extension("cool_picture.png", "txt") == "cool_picture.txt"
    assert change_file_extension("numbers.csv", "json") == "numbers.json"
    assert change_file_extension("reformatted_image.jpg", "webp") == "reformatted_image.webp"

def test_conditionally_add_quotes():
    assert conditionally_add_quotes("5", 1) == '"5"'
    assert conditionally_add_quotes("five", 1) == '"five"'
    assert conditionally_add_quotes(5, 1) == '"5"'
    assert conditionally_add_quotes(5, 0) == 5
    assert conditionally_add_quotes(5.2, 0) == 5.2
    assert conditionally_add_quotes([3, 5.1], 0) == "[3, 5.1]"
    assert conditionally_add_quotes(["one", 5.1], 0) == '["one", 5.1]'
    assert conditionally_add_quotes(["one", "5.1"], 1) == '["one", "5.1"]'

pytest.main(["-v", "--tb=line", "-rN", __file__])