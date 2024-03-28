export type NodeInfo = {
  id: string;
  is_external: boolean;
};

// TODO: Migrate to @/client/models/EntryNode
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

export type RootEntriesAPIResponse = Array<NodeInfo[]>;

export type ParentsAPIResponse = string[];
