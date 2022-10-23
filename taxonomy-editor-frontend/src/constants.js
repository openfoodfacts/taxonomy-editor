/**
 * Build the taxonomy api url from ui url
 * @param URL location
 * @returns string
 */
function taxonomyApiUrlFromUi(location) {
    let components = location.host.split(".");
    if (components[0] === "ui") {
        // we build api url by just replacing ui by api
        components[0] = "api";
        return location.protocol + "//" + components.join(".") + "/"
    }
    else {
        // this is a default for simple dev setup
        return "http://localhost:80/"
    }
}
export const API_URL = taxonomyApiUrlFromUi(window.location);
export const ENTER_KEYCODE = 13;

// List of all taxonomies in Open Food Facts
// https://wiki.openfoodfacts.org/Global_taxonomies#Overview
export const TAXONOMY_NAMES = [
    "Additives",
    "Allergens",
    "Amino Acids",
    "Categories",
    "Countries",
    "Data Quality",
    "Food Groups",
    "Improvements",
    "Ingredients",
    "Ingredients Analysis",
    "Ingredients Processing",
    "Labels",
    "Languages",
    "Minerals",
    "Misc",
    "Nova Groups",
    "Nucleotides",
    "Nutrients",
    "Origins",
    "Other Nutritional Substances",
    "Packaging Materials",
    "Packaging Recycling",
    "Packaging Shapes",
    "Periods After Opening",
    "Preservation",
    "States",
    "Test",
    "Vitamins"
];
