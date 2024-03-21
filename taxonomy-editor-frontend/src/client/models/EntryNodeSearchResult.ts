/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AncestorFilterSearchTerm } from "./AncestorFilterSearchTerm";
import type { ChildFilterSearchTerm } from "./ChildFilterSearchTerm";
import type { DescendantFilterSearchTerm } from "./DescendantFilterSearchTerm";
import type { EntryNode } from "./EntryNode";
import type { IsFilterSearchTerm } from "./IsFilterSearchTerm";
import type { LanguageFilterSearchTerm } from "./LanguageFilterSearchTerm";
import type { ParentFilterSearchTerm } from "./ParentFilterSearchTerm";
export type EntryNodeSearchResult = {
  q: string;
  nodeCount: number;
  pageCount: number;
  filters: Array<
    | IsFilterSearchTerm
    | LanguageFilterSearchTerm
    | ParentFilterSearchTerm
    | ChildFilterSearchTerm
    | AncestorFilterSearchTerm
    | DescendantFilterSearchTerm
  >;
  nodes: Array<EntryNode>;
};
