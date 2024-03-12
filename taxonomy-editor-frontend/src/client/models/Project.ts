/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ProjectStatus } from "./ProjectStatus";
export type Project = {
  id: string;
  status: ProjectStatus;
  taxonomyName: string;
  branchName: string;
  description: string;
  ownerName: string;
  isFromGithub: boolean;
  createdAt: string;
  githubCheckoutCommitSha?: string | null;
  githubFileLatestSha?: string | null;
  githubPrUrl?: string | null;
};
