/**
 * @deprecated Migrate to @/client/models/EntryNode when possible
 */
export type DestructuredEntryNode = {
  id: string;
  precedingLines: Array<string>;
  srcPosition: number;
  mainLanguage: string;
  isExternal: boolean;
  originalTaxonomy: string | null;
  // TODO: Use updated types from the API
  [key: string]: any;
  // tags: Record<string, Array<string>>;
  // properties: Record<string, string>;
  // comments: Record<string, Array<string>>;
};

export type ParentsAPIResponse = string[];
