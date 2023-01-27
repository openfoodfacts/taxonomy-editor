/**
 * @returns snake cased string converted into title case. Example: 'hello_friend' to 'Hello Friend'
 */
export function toTitleCase(taxonomyName: string) {
  return taxonomyName
    .toLowerCase()
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

/**
 * @returns string to lower caps and snake case. Example: 'Hello Friend' to 'hello_friend'
 */
export function toSnakeCase(taxonomyName: string) {
  return taxonomyName.toLowerCase().split(" ").join("_");
}
