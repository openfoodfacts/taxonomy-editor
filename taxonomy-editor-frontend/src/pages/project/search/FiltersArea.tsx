import { Box, FormControlLabel, Checkbox } from "@mui/material";
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
import { ThreeOptionsSwitch } from "./ThreeOptionsSwitch";

const checkboxTheme = {
  color: "#201a17",
  "&.Mui-checked": {
    color: "#341100",
  },
};

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
  const [isRootNodesChecked, setIsRootNodesChecked] = useState<boolean>(true);
  const [taxonomyScope, setTaxonomyScope] = useState<string>("");
  const [chosenLanguagesCodes, setChosenLanguagesCodes] = useState<string[]>(
    []
  );
  const [withoutChosenLanguagesCodes, setWithoutChosenLanguagesCodes] =
    useState<string[]>([]);
  const [parentId, setParentId] = useState<string>("");
  const [childId, setChildId] = useState<string>("");
  const [ancestorId, setAncestorId] = useState<string>("");
  const [descendantId, setDescendantId] = useState<string>("");

  const initializeFilters = (): {
    isRootNodesChecked: boolean;
    taxonomyScopeMode: string; //"in" -> in taxonomy, "out" -> outside taxonomy, "" -> filter not selected
    chosenLanguagesCodes: string[];
    withoutChosenLanguagesCodes: string[];
  } => {
    return {
      isRootNodesChecked: false,
      taxonomyScopeMode: "",
      chosenLanguagesCodes: [],
      withoutChosenLanguagesCodes: [],
    };
  };

  const updateFiltersStates = useCallback((updatedFilters) => {
    const filtersStates = initializeFilters();
    for (const filter of updatedFilters) {
      switch (filter.filterType) {
        case "is":
          switch (filter.filterValue) {
            case "root":
              filtersStates.isRootNodesChecked = true;
              break;
            case "external":
              filtersStates.taxonomyScopeMode = "out";
              break;
            case "not:external":
              filtersStates.taxonomyScopeMode = "in";
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
    setIsRootNodesChecked(filtersStates.isRootNodesChecked);
    setTaxonomyScope(filtersStates.taxonomyScopeMode);
    setChosenLanguagesCodes(filtersStates.chosenLanguagesCodes);
    setWithoutChosenLanguagesCodes(filtersStates.withoutChosenLanguagesCodes);
  }, []);

  useEffect(() => {
    updateFiltersStates(filters);
  }, [filters, updateFiltersStates]);

  const handleCheckbox = (
    event: React.ChangeEvent<HTMLInputElement>,
    filterKey: string,
    isChecked: boolean,
    setChecked: React.Dispatch<React.SetStateAction<boolean>>
  ) => {
    setCurrentPage(1);
    if (!isChecked) {
      setQ((prevQ) => prevQ + ` ${filterKey}`);
    } else {
      setQ((prevQ) => prevQ.replace(`${filterKey}`, ""));
    }
    setChecked(event.target.checked);
  };

  return (
    <Box
      sx={{
        width: "100%",
        m: 1,
        borderRadius: 1,
        bgcolor: "#f2e9e4",
        p: 1,
        pl: 2,
        pr: 2,
        display: "flex",
        flexWrap: "wrap",
        alignItems: "center",
      }}
    >
      <FormControlLabel
        id="root-nodes-checkbox"
        control={
          <Checkbox
            sx={checkboxTheme}
            onChange={(e) =>
              handleCheckbox(
                e,
                "is:root",
                isRootNodesChecked,
                setIsRootNodesChecked
              )
            }
            checked={isRootNodesChecked}
          />
        }
        label="Root nodes"
      />
      <ThreeOptionsSwitch
        filterValue={taxonomyScope}
        setFilterValue={setTaxonomyScope}
        options={{
          in: { text: "IN", isNegated: true },
          out: { text: "OUT", isNegated: false },
        }}
        setQ={setQ}
        keySearchTerm="external"
        setCurrentPage={setCurrentPage}
      />
      <MultipleSelectFilter
        label="Translated into"
        filterValue={chosenLanguagesCodes}
        listOfChoices={ISO6391.getAllNames()}
        mapCodeToValue={ISO6391.getName}
        mapValueToCode={ISO6391.getCode}
        setQ={setQ}
        keySearchTerm="language"
        setCurrentPage={setCurrentPage}
      />
      <MultipleSelectFilter
        label="Not translated into"
        filterValue={withoutChosenLanguagesCodes}
        listOfChoices={ISO6391.getAllNames()}
        mapCodeToValue={ISO6391.getName}
        mapValueToCode={ISO6391.getCode}
        setQ={setQ}
        keySearchTerm="language:not"
        setCurrentPage={setCurrentPage}
      />
      <FilterInput
        label="Is parent of (id)"
        filterValue={parentId}
        setFilterValue={setParentId}
        setQ={setQ}
        keySearchTerm="parent"
        setCurrentPage={setCurrentPage}
      />
      <FilterInput
        label="Is child of (id)"
        filterValue={childId}
        setFilterValue={setChildId}
        setQ={setQ}
        keySearchTerm="child"
        setCurrentPage={setCurrentPage}
      />
      <FilterInput
        label="Is ancestor of (id)"
        filterValue={ancestorId}
        setFilterValue={setAncestorId}
        setQ={setQ}
        keySearchTerm="ancestor"
        setCurrentPage={setCurrentPage}
      />
      <FilterInput
        label="Is descendant of (id)"
        filterValue={descendantId}
        setFilterValue={setDescendantId}
        setQ={setQ}
        keySearchTerm="descendant"
        setCurrentPage={setCurrentPage}
      />
    </Box>
  );
};
