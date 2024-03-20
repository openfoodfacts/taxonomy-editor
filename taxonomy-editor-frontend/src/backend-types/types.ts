type NodeType = {
  id: string;
  string: string | Array<string>;
};

export type RootEntriesAPIResponse = Array<NodeType[]>;

export type SearchAPIResponse = {
  pageCount: number;
  nodeCount: number;
  nodes: NodeType[];
};

export type ParentsAPIResponse = string[];
