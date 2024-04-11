import { useParams, useSearchParams } from "react-router-dom";
import { useEffect, useState } from "react";
import { Box } from "@mui/material";
import { DefaultService } from "@/client";

import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { SearchResults } from "./SearchResults";
import { SearchExpressionInput } from "./SearchExpressionInput";
import { FiltersArea } from "./FiltersArea";

export const AdvancedSearchForm = () => {
  const { taxonomyName, branchName } = useParams() as unknown as {
    taxonomyName: string;
    branchName: string;
  };

  const [searchParams, setSearchParams] = useSearchParams();

  const [q, setQ] = useState(searchParams.get("q") ?? "");
  const pageParam = searchParams.get("page");

  const [searchExpression, setSearchExpression] = useState<string>(q);
  const [currentPage, setCurrentPage] = useState<number>(
    parseInt(pageParam ?? "1")
  );

  const {
    data: entryNodeSearchResult,
    isError,
    isPending,
    error,
  } = useQuery({
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
          branchName,
          taxonomyName,
          q,
          currentPage
        );
      return nodesResult;
    },
    placeholderData: keepPreviousData,
  });

  useEffect(() => {
    if (entryNodeSearchResult?.q !== undefined) {
      setSearchExpression(entryNodeSearchResult.q);
      setSearchParams((prevSearchParams) => ({
        ...prevSearchParams,
        q: entryNodeSearchResult.q,
      }));
    }
  }, [entryNodeSearchResult?.q, setSearchParams]);

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
      <SearchResults
        entryNodes={entryNodeSearchResult?.nodes ?? []}
        nodeCount={entryNodeSearchResult?.nodeCount}
        currentPage={currentPage}
        setCurrentPage={setCurrentPage}
        isError={isError}
        errorMessage={error?.message ?? ""}
        isPending={isPending}
      />
    </Box>
  );
};
