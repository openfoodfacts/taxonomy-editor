import { useParams, useSearchParams } from "react-router-dom";
import { useState } from "react";
import { Box } from "@mui/material";
import { DefaultService } from "@/client";

import { useQuery } from "@tanstack/react-query";
import { AdvancedResearchResults } from "./SearchResults";
import { SearchExpressionInput } from "./SearchExpressionInput";
import { FiltersArea } from "./FiltersArea";

export const AdvancedResearchForm = () => {
  const { taxonomyName, branchName } = useParams<{
    taxonomyName: string;
    branchName: string;
  }>();
  const [searchParams, setSearchParams] = useSearchParams();

  const [q, setQ] = useState(searchParams.get("q") ?? "is:root");
  const pageParam = searchParams.get("page");

  const [searchExpression, setSearchExpression] = useState<string>(q);
  const [currentPage, setCurrentPage] = useState<number>(
    parseInt(pageParam ?? "1")
  );

  const { data: entryNodeSearchResult } = useQuery({
    queryKey: [
      "searchEntryNodesTaxonomyNameBranchNodesEntryGet",
      branchName,
      taxonomyName,
      q,
      currentPage,
    ],
    queryFn: async () => {
      const nodesResult =
        await DefaultService.searchEntryNodesTaxonomyNameBranchNodesEntryGet(
          branchName ?? "",
          taxonomyName ?? "",
          q,
          currentPage
        );
      setSearchExpression(nodesResult.q);
      setSearchParams((prevSearchParams) => ({
        ...prevSearchParams,
        q: nodesResult.q,
      }));
      return nodesResult;
    },
  });

  return (
    <Box sx={{ display: "flex", flexWrap: "wrap" }}>
      <SearchExpressionInput
        searchExpression={searchExpression}
        setSearchExpression={setSearchExpression}
        setCurrentPage={setCurrentPage}
        setQ={setQ}
      />
      <FiltersArea
        setCurrentPage={setCurrentPage}
        setQ={setQ}
        filters={entryNodeSearchResult?.filters ?? []}
      />
      <AdvancedResearchResults
        nodeIds={entryNodeSearchResult?.nodes.map((node) => node.id) ?? []}
        nodeCount={entryNodeSearchResult?.nodeCount}
        currentPage={currentPage}
        setCurrentPage={setCurrentPage}
      />
    </Box>
  );
};
