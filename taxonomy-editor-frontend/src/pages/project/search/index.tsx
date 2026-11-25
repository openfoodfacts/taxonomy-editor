import { useParams, useSearchParams } from "react-router-dom";
import { SetStateAction, useEffect, useState } from "react";
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

  const q = searchParams.get("q") ?? "";
  const page = Number(searchParams.get("page"));
  const currentPage = Number.isSafeInteger(page) && page > 0 ? page : 1;
  const [searchExpression, setSearchExpression] = useState(q);

  const setQ = (update: SetStateAction<string>) => {
    const nextQuery = typeof update === "function" ? update(q) : update;
    if (nextQuery === q && currentPage === 1) return;

    const nextParams = new URLSearchParams(searchParams);
    nextParams.set("q", nextQuery);
    nextParams.delete("page");
    setSearchParams(nextParams);
  };

  const setCurrentPage = (nextPage: number) => {
    const nextParams = new URLSearchParams(searchParams);
    if (nextPage === 1) {
      nextParams.delete("page");
    } else {
      nextParams.set("page", String(nextPage));
    }
    setSearchParams(nextParams);
  };

  const {
    data: entryNodeSearchResult,
    isError,
    isPending,
    isPlaceholderData,
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
          currentPage,
        );
      return nodesResult;
    },
    placeholderData: keepPreviousData,
  });

  useEffect(() => {
    setSearchExpression(q);
  }, [q]);

  const normalizedQuery = entryNodeSearchResult?.q;
  useEffect(() => {
    if (
      isPlaceholderData ||
      normalizedQuery === undefined ||
      normalizedQuery === q
    ) {
      return;
    }

    const nextParams = new URLSearchParams(searchParams);
    nextParams.set("q", normalizedQuery);
    setSearchParams(nextParams, { replace: true });
  }, [isPlaceholderData, normalizedQuery, q, searchParams, setSearchParams]);

  return (
    <Box sx={{ display: "flex", flexWrap: "wrap" }}>
      <SearchExpressionInput
        searchExpression={searchExpression}
        setSearchExpression={setSearchExpression}
        setQ={setQ}
      />
      <FiltersArea setQ={setQ} filters={entryNodeSearchResult?.filters ?? []} />
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
