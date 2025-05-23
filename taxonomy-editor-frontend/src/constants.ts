/**
 * Build the taxonomy api url from ui url
 * @param URL location
 * @returns string
 */
const taxonomyApiUrlFromUi = (location: Location): string => {
  const components = location.host.split(".");
  if (components[0] === "ui") {
    // we build api url by just replacing ui by api
    components[0] = "api";
    return location.protocol + "//" + components.join(".") + "/";
  } else {
    // this is a default for simple dev setup
    return import.meta.env.VITE_APP_API_URL;
  }
};

export const API_URL = taxonomyApiUrlFromUi(window.location);

export const ENTER_KEYCODE = 13;
export const greyHexCode = "#808080";

// List of all editable taxonomies in Open Food Facts
// Countries and Languages taxonomies are not editable
// Origins is also not editable as it depends on the Countries taxonomy
// https://wiki.openfoodfacts.org/Global_taxonomies#Overview
export const TAXONOMY_NAMES = [
  "Additives",
  "Allergens",
  "Amino Acids",
  "Brands",
  "Food Categories",
  "Data Quality",
  "Food Groups",
  "Improvements",
  "Food Ingredients",
  "Ingredients Analysis",
  "Ingredients Processing",
  "Labels",
  "Minerals",
  "Misc",
  "Nova Groups",
  "Nucleotides",
  "Nutrients",
  "Other Nutritional Substances",
  "Packaging Materials",
  "Packaging Recycling",
  "Packaging Shapes",
  "Periods After Opening",
  "Preservation",
  "States",
  "Test",
  "Vitamins",
  "Beauty Ingredients",
  "Beauty Abbreviations",
  "Beauty Allergens",
  "Beauty Brands",
  "Beauty EU lists",
  "Beauty INCI Functions",
  "Beauty Safety",
  "Beauty Special Ingredients",
  "Beauty Warnings",
  "Beauty Categories",
  "Beauty Labels",
  "Product Categories",
  "Product Labels",
  "Pet Food Categories",
  "Pet Food Ingredients",
];
