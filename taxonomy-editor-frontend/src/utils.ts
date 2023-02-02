import { API_URL } from "./constants.js";

/**
 * @returns snake cased string converted into title case. Example: 'hello_friend' to 'Hello Friend'
 */
export const toTitleCase = (taxonomyName: string) => {
  return taxonomyName
    .toLowerCase()
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
};

/**
 * @returns string to lower caps and snake case. Example: 'Hello Friend' to 'hello_friend'
 */
export const toSnakeCase = (taxonomyName: string) => {
  return taxonomyName.toLowerCase().split(" ").join("_");
};

/**
 * Finds type of ID
 * Eg: Stopword, Synonym, Entry, Header or Footer
 *   ID's can look like: __header__, __footer__, synomym:0, stopword:0
 *  For an entry, id looks like en:yogurts
 */
type NodeType = "header" | "footer" | "synonyms" | "stopwords" | "entry";
export const getNodeType = (id: string): NodeType => {
  let idType: NodeType = "entry";

  if (id.startsWith("__header__")) {
    idType = "header";
  } else if (id.startsWith("__footer__")) {
    idType = "footer";
  } else if (id.startsWith("synonym")) {
    idType = "synonyms";
  } else if (id.startsWith("stopword")) {
    idType = "stopwords";
  }

  return idType;
};

/**
 * Creating base URL for server requests
 * @returns API_URL/taxonomyName/branchName/
 */
export const createBaseURL = (taxonomyName: string, branchName: string) => {
  return `${API_URL}${taxonomyName}/${branchName}/`;
};

/**
 *  @returns front end url for each type of node
 */
export const createURL = (
  taxonomyName: string,
  branchName: string,
  id: string
) => {
  const baseUrl = createBaseURL(taxonomyName, branchName);
  const idType = getNodeType(id);

  switch (idType) {
    case "header":
      return `${baseUrl}header`;
    case "footer":
      return `${baseUrl}footer`;
    case "synonyms":
      return `${baseUrl}synonym/${id}`;
    case "stopwords":
      return `${baseUrl}stopword/${id}`;
    case "entry":
      return `${baseUrl}entry/${id}`;
    default:
      throw new Error(`Unhandled id type, id: ${id}`);
  }
};
