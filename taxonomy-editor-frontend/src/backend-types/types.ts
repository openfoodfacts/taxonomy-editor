type ProjectType = {
  branch_name: string;
  created_at: {
    _DateTime__date: {
      _Date__ordinal: number;
      _Date__year: number;
      _Date__month: number;
      _Date__day: number;
    };
    _DateTime__time: {
      _Time__ticks: number;
      _Time__hour: number;
      _Time__minute: number;
      _Time__second: number;
      _Time__nanosecond: number;
      _Time__tzinfo: any;
    };
  };
  description: string;
  id: string;
  taxonomy_name: string;
  owner_name: string;
  errors_count: number;
  status: string;
};

export type ProjectsAPIResponse = ProjectType[];

export type NodeInfo = {
  id: string;
  is_external: boolean;
};

export type RootEntriesAPIResponse = Array<NodeInfo[]>;

export type SearchAPIResponse = NodeInfo[];

export type ParentsAPIResponse = string[];

export type ProjectInfoAPIResponse = ProjectType;

export enum ProjectStatus {
  FAILED = "FAILED",
  OPEN = "OPEN",
  LOADING = "LOADING",
  EXPORTED = "EXPORTED",
  CLOSED = "CLOSED",
}
