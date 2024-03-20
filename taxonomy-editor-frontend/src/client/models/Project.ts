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
  ownerName: string | null;
  isFromGithub: boolean;
  createdAt: string;
  errorsCount: number;
  githubCheckoutCommitSha: string | null;
  githubFileLatestSha: string | null;
  githubPrUrl: string | null;
};
