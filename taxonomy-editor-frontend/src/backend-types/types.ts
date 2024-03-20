type NodeType = {
  id: string;
  string: string | Array<string>;
};

export type RootEntriesAPIResponse = Array<NodeType[]>;

export type SearchAPIResponse = string[];

export type ParentsAPIResponse = string[];
