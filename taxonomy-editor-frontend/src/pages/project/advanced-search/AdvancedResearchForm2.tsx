import { useParams, useSearchParams } from "react-router-dom";
import { useState, useEffect, useCallback } from "react";
import ISO6391 from "iso-639-1";
import {
    Typography,
    FormControl,
    OutlinedInput,
    InputAdornment,
    Box,
    FormControlLabel,
    Checkbox,
  } from "@mui/material";
import SearchIcon from '@mui/icons-material/Search';
import { MultipleSelectFilter } from "./MultipleSelectFilter";
import { DefaultService, EntryNode } from "@/client";

import type { EntryNodeSearchResult } from "../../../client/models/EntryNodeSearchResult";
import { useQuery } from "@tanstack/react-query";

const checkboxTheme = {
    color: "#201a17",
    '&.Mui-checked': {
      color: "#341100",
    },
}

type AdvancedResearchFormType = {
    taxonomyName: string, 
    branchName: string,
}
type FiltersType = EntryNodeSearchResult["filters"];

const AdvancedResearchForm2 = ({taxonomyName, branchName}: AdvancedResearchFormType) => {

    const [searchParams, setSearchParams] = useSearchParams();

    const [q,setQ] = useState(searchParams.get("q") ?? "is:root")
    const pageParam = searchParams.get("page");
    const page = (pageParam !== null ? +pageParam : 1);

    const [searchExpression,setSearchExpression] = useState<string>(q);
    // const [currentPage,setCurrentPage] = useState<number>(page);
    
    const [isRootNodesChecked,setIsRootNodesChecked] = useState<boolean>(true);
    const [isModifiedChecked,setIsModifiedChecked] = useState<boolean>(false);
    const [chosenLanguagesCodes, setChosenLanguagesCodes] = useState<string[]>([]);
    const [withoutChosenLanguagesCodes,setWithoutChosenLanguagesCodes] =useState<string[]>([]);

    const [filters,setFilters] = useState<FiltersType>([{filterType: "is", filterValue:"root"}]);//by default we display root nodes only
    const [, setNodes] = useState<EntryNode[]>([]);
    const [,setNodeCount] = useState(0);
    const [, setPageCount] = useState(1);

    const initializeFilters  = () : {
        isRootNodesChecked: boolean;
        isModifiedChecked: boolean;
        chosenLanguagesCodes: string[];
        withoutChosenLanguagesCodes: string[];
    } => {
        return {
            isRootNodesChecked: false,
            isModifiedChecked: false,
            chosenLanguagesCodes: [],
            withoutChosenLanguagesCodes: [],
        }
    }

    const updateFiltersStates = useCallback((updatedFilters) => {
        const filtersStates = initializeFilters();
        for (const filter of updatedFilters) {
            switch (filter.filterType) {
                case "is":
                    if (filter.filterValue === "root") {
                        filtersStates.isRootNodesChecked = true;
                    } else if (filter.filterValue === "modified") {
                        filtersStates.isModifiedChecked = true;
                    }
                    break;
                case "language":
                    if (filter.negated) {
                        filtersStates.withoutChosenLanguagesCodes.push(filter.filterValue);
                    } else {
                        filtersStates.chosenLanguagesCodes.push(filter.filterValue);
                    }
                    break;
                default:
                    break;
            }
        }
        setIsRootNodesChecked(filtersStates.isRootNodesChecked);
        setIsModifiedChecked(filtersStates.isModifiedChecked);
        setChosenLanguagesCodes(filtersStates.chosenLanguagesCodes);
        setWithoutChosenLanguagesCodes(filtersStates.withoutChosenLanguagesCodes);
    },[])

    useEffect(() => {
        updateFiltersStates(filters);
        setSearchParams((prevSearchParams) => ({...prevSearchParams, q: q}))
    }, [filters, q, setSearchParams, updateFiltersStates]);


    const {data : entryNodeSearchResult, refetch} = useQuery({
        queryKey: [
            "searchEntryNodesTaxonomyNameBranchNodesEntryGet",
            taxonomyName,
            branchName,
            q,
            page,
        ],
        queryFn: async () => {
            return await DefaultService.searchEntryNodesTaxonomyNameBranchNodesEntryGet(
                taxonomyName,
                branchName,
                q,
                page,  
            );
        },
    });

    useEffect(() => {
        refetch();
    }, [q, refetch]);

    if (entryNodeSearchResult && entryNodeSearchResult.filters !== filters) {
        setNodeCount(entryNodeSearchResult.nodeCount);
        setPageCount(entryNodeSearchResult.pageCount);
        setNodes(entryNodeSearchResult.nodes);
        setFilters(entryNodeSearchResult.filters);
    }

    const handleCheckbox = (
        event: React.ChangeEvent<HTMLInputElement>,
        filterKey: string,
        setChecked: React.Dispatch<React.SetStateAction<boolean>>,
    ) => {
        setQ((prevQ) => prevQ+` ${filterKey}`);
        setChecked(event.target.checked);
    }

    const handleSearchInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setSearchExpression(event.target.value);
    };

    const handleEnterKeyPress = (event: React.KeyboardEvent<HTMLInputElement>) => {
        if (event.key === 'Enter') {
            setQ(searchExpression);
            event.preventDefault();
        }
    };

    return (
        <Box sx={{ display: 'flex', flexWrap: 'wrap' }}>
            <FormControl fullWidth sx={{ m: 1 }} variant="outlined">
                <OutlinedInput
                    id="search-expression"
                    sx={{backgroundColor:"#f2e9e4"}}
                    startAdornment={<InputAdornment position="start"><SearchIcon/></InputAdornment>}
                    value={searchExpression}
                    onChange={handleSearchInputChange}
                    onKeyDown={handleEnterKeyPress}
                />
            </FormControl>

            <Box
                sx={{
                width: "100%",
                m: 1,
                borderRadius: 1,
                bgcolor: "#f2e9e4",
                p:1,
                pl:2,
                pr:2,
                }}
            >
                <FormControlLabel id="root-nodes-checkbox" control={<Checkbox sx={checkboxTheme} onChange={(e) => handleCheckbox(e,"is:root",setIsRootNodesChecked)} checked={isRootNodesChecked} />} label="Root nodes" />
                <FormControlLabel id="modified-checkbox" control={<Checkbox sx={checkboxTheme} onChange={(e) => handleCheckbox(e,"is:modified",setIsModifiedChecked)} checked={isModifiedChecked} />} label="Modified" />
                <MultipleSelectFilter label="Translated into" filterValue={chosenLanguagesCodes} setFilterValue={setChosenLanguagesCodes} listOfChoices={ISO6391.getAllNames()} mapCodeToValue={ISO6391.getName} mapValueToCode={ISO6391.getCode} />
                <MultipleSelectFilter label="Not translated into" filterValue={withoutChosenLanguagesCodes} setFilterValue={setWithoutChosenLanguagesCodes} listOfChoices={ISO6391.getAllNames()} mapCodeToValue={ISO6391.getName} mapValueToCode={ISO6391.getCode} />

            </Box>
        </Box>
    )
}

export const AdvancedResearchFormWrapper2 = () => {
    const { taxonomyName, branchName } = useParams();
  
    if (!taxonomyName || !branchName)
      return (
        <Typography variant="h3">
          Oops, something went wrong! Please try again later.
        </Typography>
      );
  
    return <AdvancedResearchForm2 taxonomyName={taxonomyName} branchName={branchName} />;
  };