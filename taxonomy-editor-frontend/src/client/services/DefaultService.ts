/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Body_upload_taxonomy__taxonomy_name___branch__upload_post } from "../models/Body_upload_taxonomy__taxonomy_name___branch__upload_post";
import type { EntryNodeCreate } from "../models/EntryNodeCreate";
import type { EntryNodeSearchResult } from "../models/EntryNodeSearchResult";
import type { ErrorNode } from "../models/ErrorNode";
import type { Footer } from "../models/Footer";
import type { Header } from "../models/Header";
import type { Project } from "../models/Project";
import type { ProjectStatus } from "../models/ProjectStatus";
import type { CancelablePromise } from "../core/CancelablePromise";
import { OpenAPI } from "../core/OpenAPI";
import { request as __request } from "../core/request";
export class DefaultService {
  /**
   * Hello
   * @returns any Successful Response
   * @throws ApiError
   */
  public static helloGet(): CancelablePromise<any> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/",
    });
  }
  /**
   * Pong
   * Check server health
   * @returns any Successful Response
   * @throws ApiError
   */
  public static pongPingGet(): CancelablePromise<any> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/ping",
    });
  }
  /**
   * Get All Projects
   * List projects created in the Taxonomy Editor
   * @returns Project Successful Response
   * @throws ApiError
   */
  public static getAllProjectsProjectsGet(): CancelablePromise<Array<Project>> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/projects",
    });
  }
  /**
   * Get Project Info
   * Get information about a Taxonomy Editor project
   * @param branch
   * @param taxonomyName
   * @returns Project Successful Response
   * @throws ApiError
   */
  public static getProjectInfoTaxonomyNameBranchProjectGet(
    branch: string,
    taxonomyName: string
  ): CancelablePromise<Project> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/{taxonomy_name}/{branch}/project",
      path: {
        branch: branch,
        taxonomy_name: taxonomyName,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Set Project Status
   * Set the status of a Taxonomy Editor project
   * @param branch
   * @param taxonomyName
   * @param status
   * @returns any Successful Response
   * @throws ApiError
   */
  public static setProjectStatusTaxonomyNameBranchSetProjectStatusGet(
    branch: string,
    taxonomyName: string,
    status?: ProjectStatus | null
  ): CancelablePromise<any> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/{taxonomy_name}/{branch}/set-project-status",
      path: {
        branch: branch,
        taxonomy_name: taxonomyName,
      },
      query: {
        status: status,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Find All Nodes
   * Get all nodes within taxonomy
   * @param branch
   * @param taxonomyName
   * @returns any Successful Response
   * @throws ApiError
   */
  public static findAllNodesTaxonomyNameBranchNodesGet(
    branch: string,
    taxonomyName: string
  ): CancelablePromise<any> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/{taxonomy_name}/{branch}/nodes",
      path: {
        branch: branch,
        taxonomy_name: taxonomyName,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Delete Node
   * Deleting given node from a taxonomy
   * @param branch
   * @param taxonomyName
   * @returns any Successful Response
   * @throws ApiError
   */
  public static deleteNodeTaxonomyNameBranchNodesDelete(
    branch: string,
    taxonomyName: string
  ): CancelablePromise<any> {
    return __request(OpenAPI, {
      method: "DELETE",
      url: "/{taxonomy_name}/{branch}/nodes",
      path: {
        branch: branch,
        taxonomy_name: taxonomyName,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Find All Root Nodes
   * Get all root nodes within taxonomy
   * @param branch
   * @param taxonomyName
   * @returns any Successful Response
   * @throws ApiError
   */
  public static findAllRootNodesTaxonomyNameBranchRootentriesGet(
    branch: string,
    taxonomyName: string
  ): CancelablePromise<any> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/{taxonomy_name}/{branch}/rootentries",
      path: {
        branch: branch,
        taxonomy_name: taxonomyName,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Find One Entry
   * Get entry corresponding to id within taxonomy
   * @param branch
   * @param taxonomyName
   * @param entry
   * @returns any Successful Response
   * @throws ApiError
   */
  public static findOneEntryTaxonomyNameBranchEntryEntryGet(
    branch: string,
    taxonomyName: string,
    entry: string
  ): CancelablePromise<any> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/{taxonomy_name}/{branch}/entry/{entry}",
      path: {
        branch: branch,
        taxonomy_name: taxonomyName,
        entry: entry,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Edit Entry
   * Editing an entry in a taxonomy.
   * New key-value pairs can be added, old key-value pairs can be updated.
   * URL will be of format '/entry/<id>'
   * @param branch
   * @param taxonomyName
   * @param entry
   * @returns any Successful Response
   * @throws ApiError
   */
  public static editEntryTaxonomyNameBranchEntryEntryPost(
    branch: string,
    taxonomyName: string,
    entry: string
  ): CancelablePromise<any> {
    return __request(OpenAPI, {
      method: "POST",
      url: "/{taxonomy_name}/{branch}/entry/{entry}",
      path: {
        branch: branch,
        taxonomy_name: taxonomyName,
        entry: entry,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Find One Entry Parents
   * Get parents for a entry corresponding to id within taxonomy
   * @param branch
   * @param taxonomyName
   * @param entry
   * @returns any Successful Response
   * @throws ApiError
   */
  public static findOneEntryParentsTaxonomyNameBranchEntryEntryParentsGet(
    branch: string,
    taxonomyName: string,
    entry: string
  ): CancelablePromise<any> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/{taxonomy_name}/{branch}/entry/{entry}/parents",
      path: {
        branch: branch,
        taxonomy_name: taxonomyName,
        entry: entry,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Find One Entry Children
   * Get children for a entry corresponding to id within taxonomy
   * @param branch
   * @param taxonomyName
   * @param entry
   * @returns any Successful Response
   * @throws ApiError
   */
  public static findOneEntryChildrenTaxonomyNameBranchEntryEntryChildrenGet(
    branch: string,
    taxonomyName: string,
    entry: string
  ): CancelablePromise<any> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/{taxonomy_name}/{branch}/entry/{entry}/children",
      path: {
        branch: branch,
        taxonomy_name: taxonomyName,
        entry: entry,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Edit Entry Children
   * Editing an entry's children in a taxonomy.
   * New children can be added, old children can be removed.
   * URL will be of format '/entry/<id>/children'
   * @param branch
   * @param taxonomyName
   * @param entry
   * @returns any Successful Response
   * @throws ApiError
   */
  public static editEntryChildrenTaxonomyNameBranchEntryEntryChildrenPost(
    branch: string,
    taxonomyName: string,
    entry: string
  ): CancelablePromise<any> {
    return __request(OpenAPI, {
      method: "POST",
      url: "/{taxonomy_name}/{branch}/entry/{entry}/children",
      path: {
        branch: branch,
        taxonomy_name: taxonomyName,
        entry: entry,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Find One Synonym
   * Get synonym corresponding to id within taxonomy
   * @param branch
   * @param taxonomyName
   * @param synonym
   * @returns any Successful Response
   * @throws ApiError
   */
  public static findOneSynonymTaxonomyNameBranchSynonymSynonymGet(
    branch: string,
    taxonomyName: string,
    synonym: string
  ): CancelablePromise<any> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/{taxonomy_name}/{branch}/synonym/{synonym}",
      path: {
        branch: branch,
        taxonomy_name: taxonomyName,
        synonym: synonym,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Edit Synonyms
   * Editing a synonym in a taxonomy.
   * New key-value pairs can be added, old key-value pairs can be updated.
   * URL will be of format '/synonym/<id>'
   * @param branch
   * @param taxonomyName
   * @param synonym
   * @returns any Successful Response
   * @throws ApiError
   */
  public static editSynonymsTaxonomyNameBranchSynonymSynonymPost(
    branch: string,
    taxonomyName: string,
    synonym: string
  ): CancelablePromise<any> {
    return __request(OpenAPI, {
      method: "POST",
      url: "/{taxonomy_name}/{branch}/synonym/{synonym}",
      path: {
        branch: branch,
        taxonomy_name: taxonomyName,
        synonym: synonym,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Find All Synonyms
   * Get all synonyms within taxonomy
   * @param branch
   * @param taxonomyName
   * @returns any Successful Response
   * @throws ApiError
   */
  public static findAllSynonymsTaxonomyNameBranchSynonymGet(
    branch: string,
    taxonomyName: string
  ): CancelablePromise<any> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/{taxonomy_name}/{branch}/synonym",
      path: {
        branch: branch,
        taxonomy_name: taxonomyName,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Find One Stopword
   * Get stopword corresponding to id within taxonomy
   * @param branch
   * @param taxonomyName
   * @param stopword
   * @returns any Successful Response
   * @throws ApiError
   */
  public static findOneStopwordTaxonomyNameBranchStopwordStopwordGet(
    branch: string,
    taxonomyName: string,
    stopword: string
  ): CancelablePromise<any> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/{taxonomy_name}/{branch}/stopword/{stopword}",
      path: {
        branch: branch,
        taxonomy_name: taxonomyName,
        stopword: stopword,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Edit Stopwords
   * Editing a stopword in a taxonomy.
   * New key-value pairs can be added, old key-value pairs can be updated.
   * URL will be of format '/stopword/<id>'
   * @param branch
   * @param taxonomyName
   * @param stopword
   * @returns any Successful Response
   * @throws ApiError
   */
  public static editStopwordsTaxonomyNameBranchStopwordStopwordPost(
    branch: string,
    taxonomyName: string,
    stopword: string
  ): CancelablePromise<any> {
    return __request(OpenAPI, {
      method: "POST",
      url: "/{taxonomy_name}/{branch}/stopword/{stopword}",
      path: {
        branch: branch,
        taxonomy_name: taxonomyName,
        stopword: stopword,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Find All Stopwords
   * Get all stopwords within taxonomy
   * @param branch
   * @param taxonomyName
   * @returns any Successful Response
   * @throws ApiError
   */
  public static findAllStopwordsTaxonomyNameBranchStopwordGet(
    branch: string,
    taxonomyName: string
  ): CancelablePromise<any> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/{taxonomy_name}/{branch}/stopword",
      path: {
        branch: branch,
        taxonomy_name: taxonomyName,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Find Header
   * Get __header__ within taxonomy
   * @param branch
   * @param taxonomyName
   * @returns any Successful Response
   * @throws ApiError
   */
  public static findHeaderTaxonomyNameBranchHeaderGet(
    branch: string,
    taxonomyName: string
  ): CancelablePromise<any> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/{taxonomy_name}/{branch}/header",
      path: {
        branch: branch,
        taxonomy_name: taxonomyName,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Edit Header
   * Editing the __header__ in a taxonomy.
   * @param branch
   * @param taxonomyName
   * @param requestBody
   * @returns any Successful Response
   * @throws ApiError
   */
  public static editHeaderTaxonomyNameBranchHeaderPost(
    branch: string,
    taxonomyName: string,
    requestBody: Header
  ): CancelablePromise<any> {
    return __request(OpenAPI, {
      method: "POST",
      url: "/{taxonomy_name}/{branch}/header",
      path: {
        branch: branch,
        taxonomy_name: taxonomyName,
      },
      body: requestBody,
      mediaType: "application/json",
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Find Footer
   * Get __footer__ within taxonomy
   * @param branch
   * @param taxonomyName
   * @returns any Successful Response
   * @throws ApiError
   */
  public static findFooterTaxonomyNameBranchFooterGet(
    branch: string,
    taxonomyName: string
  ): CancelablePromise<any> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/{taxonomy_name}/{branch}/footer",
      path: {
        branch: branch,
        taxonomy_name: taxonomyName,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Edit Footer
   * Editing the __footer__ in a taxonomy.
   * @param branch
   * @param taxonomyName
   * @param requestBody
   * @returns any Successful Response
   * @throws ApiError
   */
  public static editFooterTaxonomyNameBranchFooterPost(
    branch: string,
    taxonomyName: string,
    requestBody: Footer
  ): CancelablePromise<any> {
    return __request(OpenAPI, {
      method: "POST",
      url: "/{taxonomy_name}/{branch}/footer",
      path: {
        branch: branch,
        taxonomy_name: taxonomyName,
      },
      body: requestBody,
      mediaType: "application/json",
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Find All Errors
   * Get all errors within taxonomy
   * @param branch
   * @param taxonomyName
   * @returns ErrorNode Successful Response
   * @throws ApiError
   */
  public static findAllErrorsTaxonomyNameBranchParsingErrorsGet(
    branch: string,
    taxonomyName: string
  ): CancelablePromise<ErrorNode> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/{taxonomy_name}/{branch}/parsing_errors",
      path: {
        branch: branch,
        taxonomy_name: taxonomyName,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Search Entry Nodes
   * @param branch
   * @param taxonomyName
   * @param q The search query string to filter down the returned entry nodes.            Example: is:root language:en not(language):fr
   * @param page
   * @returns EntryNodeSearchResult Successful Response
   * @throws ApiError
   */
  public static searchEntryNodesTaxonomyNameBranchNodesEntryGet(
    branch: string,
    taxonomyName: string,
    q: string = "",
    page: number = 1
  ): CancelablePromise<EntryNodeSearchResult> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/{taxonomy_name}/{branch}/nodes/entry",
      path: {
        branch: branch,
        taxonomy_name: taxonomyName,
      },
      query: {
        q: q,
        page: page,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Export To Text File
   * @param branch
   * @param taxonomyName
   * @returns any Successful Response
   * @throws ApiError
   */
  public static exportToTextFileTaxonomyNameBranchDownloadexportGet(
    branch: string,
    taxonomyName: string
  ): CancelablePromise<any> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/{taxonomy_name}/{branch}/downloadexport",
      path: {
        branch: branch,
        taxonomy_name: taxonomyName,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Export To Github
   * @param branch
   * @param taxonomyName
   * @returns any Successful Response
   * @throws ApiError
   */
  public static exportToGithubTaxonomyNameBranchGithubexportGet(
    branch: string,
    taxonomyName: string
  ): CancelablePromise<any> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/{taxonomy_name}/{branch}/githubexport",
      path: {
        branch: branch,
        taxonomy_name: taxonomyName,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Import From Github
   * Get taxonomy from Product Opener GitHub repository
   * @param branch
   * @param taxonomyName
   * @returns any Successful Response
   * @throws ApiError
   */
  public static importFromGithubTaxonomyNameBranchImportPost(
    branch: string,
    taxonomyName: string
  ): CancelablePromise<any> {
    return __request(OpenAPI, {
      method: "POST",
      url: "/{taxonomy_name}/{branch}/import",
      path: {
        branch: branch,
        taxonomy_name: taxonomyName,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Upload Taxonomy
   * Upload taxonomy file to be parsed
   * @param branch
   * @param taxonomyName
   * @param formData
   * @returns any Successful Response
   * @throws ApiError
   */
  public static uploadTaxonomyTaxonomyNameBranchUploadPost(
    branch: string,
    taxonomyName: string,
    formData: Body_upload_taxonomy__taxonomy_name___branch__upload_post
  ): CancelablePromise<any> {
    return __request(OpenAPI, {
      method: "POST",
      url: "/{taxonomy_name}/{branch}/upload",
      path: {
        branch: branch,
        taxonomy_name: taxonomyName,
      },
      formData: formData,
      mediaType: "multipart/form-data",
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Create Entry Node
   * Creating a new entry node in a taxonomy
   * @param branch
   * @param taxonomyName
   * @param requestBody
   * @returns any Successful Response
   * @throws ApiError
   */
  public static createEntryNodeTaxonomyNameBranchEntryPost(
    branch: string,
    taxonomyName: string,
    requestBody: EntryNodeCreate
  ): CancelablePromise<any> {
    return __request(OpenAPI, {
      method: "POST",
      url: "/{taxonomy_name}/{branch}/entry",
      path: {
        branch: branch,
        taxonomy_name: taxonomyName,
      },
      body: requestBody,
      mediaType: "application/json",
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Delete Project
   * Delete a project
   * @param branch
   * @param taxonomyName
   * @returns void
   * @throws ApiError
   */
  public static deleteProjectTaxonomyNameBranchDelete(
    branch: string,
    taxonomyName: string
  ): CancelablePromise<void> {
    return __request(OpenAPI, {
      method: "DELETE",
      url: "/{taxonomy_name}/{branch}",
      path: {
        branch: branch,
        taxonomy_name: taxonomyName,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
}
