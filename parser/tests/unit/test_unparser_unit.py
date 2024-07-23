import inspect
import pathlib

import pytest
from openfoodfacts_taxonomy_parser import unparser


@pytest.mark.parametrize(
    "properties_txt, expected",
    [
        (
            """
            vegan:en: yes
            ciqual_food_name:fr: Lécithine de soja
            ciqual_food_code:en: 42200
            vegetarian:en: yes
            ciqual_food_name:en: Soy lecithin
            """,
            [
                "ciqual_food_code:en",
                "ciqual_food_name:en",
                "ciqual_food_name:fr",
                "vegan:en",
                "vegetarian:en",
            ],
        ),
    ],
)
def test_list_property_and_lc(properties_txt, expected):
    # construct a node with the given properties
    properties = [
        prop for prop in inspect.cleandoc(properties_txt).split("\n") if prop.strip()
    ]
    name_lc_values = [prop.split(":", 2) for prop in properties]
    node = {f"prop_{name}_{lc}": value for name, lc, value in name_lc_values}
    # node = {f"prop_{name}_{lc}": value for prop in properties for name, lc, value in prop.split(":", 2)}
    result = unparser.WriteTaxonomy(None).list_property_and_lc(node)
    assert result, expected
