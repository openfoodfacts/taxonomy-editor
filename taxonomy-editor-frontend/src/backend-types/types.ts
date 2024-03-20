export type NodeInfo = {
  id: string;
  is_external: boolean;
};

export type RootEntriesAPIResponse = Array<NodeInfo[]>;

export type SearchAPIResponse = NodeInfo[];

export type ParentsAPIResponse = string[];
