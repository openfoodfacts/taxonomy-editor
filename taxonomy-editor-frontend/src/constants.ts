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

// Mapping from URL-friendly taxonomy slugs (used in deep links)
// to the display names used in TAXONOMY_NAMES above.
// Deep links from external tools (e.g. Hunger Games) use short slugs like
// "ingredients" which need to map to "Food Ingredients" in the dropdown.
export const TAXONOMY_URL_SLUG_MAP: Record<string, string> = {
  additives: "Additives",
  allergens: "Allergens",
  amino_acids: "Amino Acids",
  brands: "Brands",
  categories: "Food Categories",
  data_quality: "Data Quality",
  food_groups: "Food Groups",
  improvements: "Improvements",
  ingredients: "Food Ingredients",
  ingredients_analysis: "Ingredients Analysis",
  ingredients_processing: "Ingredients Processing",
  labels: "Labels",
  minerals: "Minerals",
  misc: "Misc",
  nova_groups: "Nova Groups",
  nucleotides: "Nucleotides",
  nutrients: "Nutrients",
  other_nutritional_substances: "Other Nutritional Substances",
  packaging_materials: "Packaging Materials",
  packaging_recycling: "Packaging Recycling",
  packaging_shapes: "Packaging Shapes",
  periods_after_opening: "Periods After Opening",
  preservation: "Preservation",
  states: "States",
  test: "Test",
  vitamins: "Vitamins",
};

