import pytest
from Parser import Parser
import re

def test_filename():
    x = Parser("test")
    x.file_name()
    assert x.filename == "test.txt"
    x = Parser("test.txt")
    x.file_name()
    assert x.filename == "test.txt"
    x = Parser("t")
    x.file_name()
    assert x.filename == "t.txt"

def test_fileiter():
    x=Parser("test")
    x.file_name()
    file=x.file_iter()
    counter=0
    language_code_prefix = re.compile('[a-zA-Z][a-zA-Z]:')
    for line in file:
        counter+=1
        assert line == '' or line[0]=="#" or 'stopword' in line or 'synonym' in line or line[0]=="<" or language_code_prefix.match(line) or ":" in line
        if counter==27:
            assert line == "carbon_footprint_fr_foodges_value:fr:10"
    assert counter == 37+1

def test_normalizing():
    x=Parser("")
    text="Numéro #1, n°1 des ¾ des Français*"
    text=x.normalizing(text,"fr")
    assert text == "numero-1-n-1-des-des-francais"
    text="Randôm Languäge wìth àccénts"
    text=x.normalizing(text,"fr")
    assert text == "random-language-with-accent"

def test_harvest():
    x=Parser("test")
    x.file_name()
    data=x.harvest()
    test_data=["# test taxonomy",
    {"id":"stopwords:1","value":"fr:aux,au,de,le,du,la,a,et"},
    {"id":"synonyms:1","value":"en:passion-fruit,passionfruit","comment":[]},
    {"id":"synonyms:2","value":"fr:fruit-de-la-passion,fruits-de-la-passion,maracuja,passion"},
    {"id":"en:yogurts","parent_tag":[],"tags":{"en":["yogurts","yoghurts"],"fr":["yaourts", "yoghourts", "yogourts"]},"tagsid":["en:yogurts","en:yoghurts","fr:yaourts","fr:yoghourts","fr:yogourts"],"properties":[],"comment":[]},
    {"id":"en:banana-yogurts","parent_tag":["en:yogurts"],"tags":{"en":["banana-yogurts"],"fr":["yaourts-a-la-banane"]},"tagsid":["en:banana-yogurts","fr:yaourts-a-la-banane"]},
    {"id":"en:passion-fruit-yogurts","parent_tag":["en:yogurts"],"tags":{"en":["passion-fruit-yogurts"],"fr":["yaourts-au-fruit-de-la-passion"]},"tagsid":["en:passion-fruit-yogurts","fr:yaourts-au-fruit-de-la-passion"]},
    {"id":"fr:yaourts-au-fruit-de-la-passion-alleges","parent_tag":["fr:yaourts-au-fruit-de-la-passion"],"tags":{"fr":["yaourts-au-fruit-de-la-passion-alleges"]},"tagsid":["fr:yaourts-au-fruit-de-la-passion-alleges"],"properties":[],"comment":[]},
    {"id":"en:meat","parent_tag":[],"tags":{"en":["meat"]},"tagsid":["en:meat"],"properties":[str({'id':1,'name':'vegan','value':'en:no'}),str({'id':2,'name':'carbon-footprint-fr-foodges-value','value':'fr:10'})],"comment":["meat"]},
    {"id":"en:fake-meat","parent_tag":["en:meat"],"tags":{"en":["fake-meat"]},"tagsid":["en:fake-meat"],"properties":[str({'id':1,'name':'vegan','value':'en:yes'})],"comment":[]},
    {"id":"en:fake-stuff","parent_tag":[],"tags":{"en":["fake-stuff"]},"tagsid":["en:fake-stuff"],"properties":[],"comment":[]},
    {"id":"en:fake-duck-meat","parent_tag":["en:fake-stuff","en:fake-meat"],"tags":{"en":["fake-duck-meat"]},"tagsid":["en:fake-duck-meat"]}
    ]
    counter=0
    first=next(data)
    assert first == test_data[0]
    for entry in data:
        counter+=1
        for key in test_data[counter]:
            assert test_data[counter][key] == entry[key]
    assert counter == 11



if __name__ == "__main__":
    pytest.main()