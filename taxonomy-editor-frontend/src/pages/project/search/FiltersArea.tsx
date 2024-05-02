import { Box } from "@mui/material";
import { FilterInput } from "./FilterInput";
import { MultipleSelectFilter } from "./MultipleSelectFilter";
import {
  Dispatch,
  SetStateAction,
  useCallback,
  useEffect,
  useState,
} from "react";
import ISO6391 from "iso-639-1";
import { EntryNodeSearchResult } from "@/client";
import { SingleSelectFilter } from "./SingleSelectFilter";

type FiltersAreaProps = {
  setCurrentPage: Dispatch<SetStateAction<number>>;
  setQ: Dispatch<SetStateAction<string>>;
  filters: EntryNodeSearchResult["filters"];
};

export const FiltersArea = ({
  setCurrentPage,
  setQ,
  filters,
}: FiltersAreaProps) => {
  const [nodesLevel, setNodesLevel] = useState<string>("root");
  const [taxonomyScope, setTaxonomyScope] = useState<string>("both");
  const [chosenLanguagesCodes, setChosenLanguagesCodes] = useState<string[]>(
    []
  );
  const [withoutChosenLanguagesCodes, setWithoutChosenLanguagesCodes] =
    useState<string[]>([]);

  const initializeFilters = (): {
    nodesLevel: string;
    taxonomyScopeMode: string; //"in" -> in taxonomy, "out" -> outside taxonomy, "" -> filter not selected
    chosenLanguagesCodes: string[];
    withoutChosenLanguagesCodes: string[];
  } => {
    return {
      nodesLevel: "root",
      taxonomyScopeMode: "",
      chosenLanguagesCodes: [],
      withoutChosenLanguagesCodes: [],
    };
  };

  const updateFiltersStates = useCallback((updatedFilters) => {
    const filtersStates = initializeFilters();
    let hasScopeFilterInQ = false;
    let hasLevelFilterInQ = false;
    for (const filter of updatedFilters) {
      switch (filter.filterType) {
        case "is":
          switch (filter.filterValue) {
            case "root":
              filtersStates.nodesLevel = "root";
              hasLevelFilterInQ = true;
              break;
            case "external":
              filtersStates.taxonomyScopeMode = "external";
              hasScopeFilterInQ = true;
              break;
            case "not:external":
              filtersStates.taxonomyScopeMode = "not:external";
              hasScopeFilterInQ = true;
              break;
          }
          break;
        case "language":
          if (filter.negated) {
            filtersStates.withoutChosenLanguagesCodes.push(
              filter.filterValue.replace("not:", "")
            );
          } else {
            filtersStates.chosenLanguagesCodes.push(filter.filterValue);
          }
          break;
        default:
          break;
      }
    }
    setNodesLevel(hasLevelFilterInQ ? filtersStates.nodesLevel : "both");
    setTaxonomyScope(
      hasScopeFilterInQ ? filtersStates.taxonomyScopeMode : "both"
    );
    setChosenLanguagesCodes(filtersStates.chosenLanguagesCodes);
    setWithoutChosenLanguagesCodes(filtersStates.withoutChosenLanguagesCodes);
  }, []);

  useEffect(() => {
    updateFiltersStates(filters);
  }, [filters, updateFiltersStates]);

  const scopeOptions = {
    "Only Outside Current Taxonomy": "external",
    "Only In Current Taxonomy": "not:external",
    "Both In and Outside Current Taxonomy": "both",
  };

  const levelOptions = {
    "Top level entries": "root",
    "All levels": "both",
  };

  return (
    <Box
      sx={{
        width: "100%",
        m: 1,
        borderRadius: 1,
        bgcolor: "#f2e9e4",
        p: 1,
        px: 2,
        display: "flex",
        flexWrap: "wrap",
        alignItems: "center",
      }}
    >
      <SingleSelectFilter
        label="Hierarchy Level"
        filterValue={nodesLevel}
        listOfChoices={Object.keys(levelOptions)}
        mapValueToCode={(value: string) => levelOptions[value]}
        setQ={setQ}
        keySearchTerm="is"
        setCurrentPage={setCurrentPage}
      />
      <SingleSelectFilter
        label="Scope"
        filterValue={taxonomyScope}
        listOfChoices={Object.keys(scopeOptions)}
        mapValueToCode={(value: string) => scopeOptions[value]}
        setQ={setQ}
        keySearchTerm="is"
        setCurrentPage={setCurrentPage}
      />
      <MultipleSelectFilter
        label="Translated into"
        filterValue={chosenLanguagesCodes}
        listOfChoices={ISO6391.getAllNames().sort()}
        mapCodeToValue={ISO6391.getName}
        mapValueToCode={ISO6391.getCode}
        setQ={setQ}
        keySearchTerm="language"
        setCurrentPage={setCurrentPage}
      />
      <MultipleSelectFilter
        label="Not translated into"
        filterValue={withoutChosenLanguagesCodes}
        listOfChoices={ISO6391.getAllNames().sort()}
        mapCodeToValue={ISO6391.getName}
        mapValueToCode={ISO6391.getCode}
        setQ={setQ}
        keySearchTerm="language:not"
        setCurrentPage={setCurrentPage}
      />
      <FilterInput
        label="Is parent of (id)"
        setQ={setQ}
        keySearchTerm="parent"
        setCurrentPage={setCurrentPage}
      />
      <FilterInput
        label="Is child of (id)"
        setQ={setQ}
        keySearchTerm="child"
        setCurrentPage={setCurrentPage}
      />
      <FilterInput
        label="Is ancestor of (id)"
        setQ={setQ}
        keySearchTerm="ancestor"
        setCurrentPage={setCurrentPage}
      />
      <FilterInput
        label="Is descendant of (id)"
        setQ={setQ}
        keySearchTerm="descendant"
        setCurrentPage={setCurrentPage}
      />
    </Box>
  );
};
