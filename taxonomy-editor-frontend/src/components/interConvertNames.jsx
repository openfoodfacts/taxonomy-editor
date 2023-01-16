/**
 * Changes taxonomy name to title case
 */
export function toTitleCase(taxonomyName) {
  return taxonomyName
    .toLowerCase()
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

/**
 * Changes taxonomy name to snake case
 */
export function toSnakeCase(taxonomyName) {
  return taxonomyName.toLowerCase().split(" ").join("_");
}
