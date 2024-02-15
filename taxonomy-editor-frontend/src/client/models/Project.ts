/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ProjectStatus } from "./ProjectStatus";
export type Project = {
  id: string;
  status: ProjectStatus;
  taxonomy_name: string;
  branch_name: string;
  description: string;
  is_from_github: boolean;
  created_at: string;
  github_checkout_commit_sha?: string | null;
  github_file_latest_sha?: string | null;
  github_pr_url?: string | null;
};
