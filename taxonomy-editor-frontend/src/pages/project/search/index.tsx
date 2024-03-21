import { useParams, useSearchParams } from "react-router-dom";
import { useState, useCallback } from "react";
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
import { DefaultService} from "@/client";

import { useQuery } from "@tanstack/react-query";
import { FilterInput } from "./FilterInput";
import { AdvancedResearchResults } from "./SearchResults";

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

const AdvancedResearchForm = ({taxonomyName, branchName}: AdvancedResearchFormType) => {

    const [searchParams, setSearchParams] = useSearchParams();

    const [q,setQ] = useState(searchParams.get("q")??"is:root")
    const pageParam = searchParams.get("page");

    const [searchExpression,setSearchExpression] = useState<string>(q);
    const [currentPage,setCurrentPage] = useState<number>(parseInt(pageParam??"1"));
    
    const [isRootNodesChecked,setIsRootNodesChecked] = useState<boolean>(true);
    const [chosenLanguagesCodes, setChosenLanguagesCodes] = useState<string[]>([]);
    const [withoutChosenLanguagesCodes,setWithoutChosenLanguagesCodes] =useState<string[]>([]);
    const [parentId, setParentId] = useState<string>("");
    const [childId, setChildId] = useState<string>("");
    const [ancestorId, setAncestorId] = useState<string>("");
    const [descendantId, setDescendantId] = useState<string>("");

    
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
                        filtersStates.withoutChosenLanguagesCodes.push(filter.filterValue.replace("not:",""));
                    } else {
                        filtersStates.chosenLanguagesCodes.push(filter.filterValue);
                    }
                    break;
                default:
                    break;
            }
        }
        setIsRootNodesChecked(filtersStates.isRootNodesChecked);
        setChosenLanguagesCodes(filtersStates.chosenLanguagesCodes);
        setWithoutChosenLanguagesCodes(filtersStates.withoutChosenLanguagesCodes);
    },[])

      const {data : entryNodeSearchResult} = useQuery({
        queryKey: [
            "searchEntryNodesTaxonomyNameBranchNodesEntryGet",
            branchName,
            taxonomyName,
            q,
            currentPage,
        ],
        queryFn: async () => {
            const nodesResult = await DefaultService.searchEntryNodesTaxonomyNameBranchNodesEntryGet(
                branchName,
                taxonomyName,
                q,
                currentPage,  
            );
            setSearchExpression(nodesResult.q);
            updateFiltersStates(nodesResult.filters);
            setSearchParams((prevSearchParams) => ({...prevSearchParams, q: nodesResult.q}))
            return nodesResult;
        },
    });

    const handleCheckbox = (
        event: React.ChangeEvent<HTMLInputElement>,
        filterKey: string,
        isChecked: boolean,
        setChecked: React.Dispatch<React.SetStateAction<boolean>>,
    ) => {
        setCurrentPage(1);
        if (! isChecked) {
            setQ((prevQ) => prevQ+` ${filterKey}`);
        } else {
            setQ((prevQ) => prevQ.replace(`${filterKey}`,""));
        }
        setChecked(event.target.checked);
        
    }

    const handleSearchInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setSearchExpression(event.target.value);
    };

    const handleEnterKeyPress = (event: React.KeyboardEvent<HTMLInputElement>) => {
        setCurrentPage(1);
        if (event.key === 'Enter') {
            setQ(searchExpression);
            event.preventDefault();
        }
    };

    return (
        <Box sx={{ display: 'flex', flexWrap: 'wrap'}}>
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
                display: 'flex', flexWrap: 'wrap', alignItems: 'center'
                }}
            >
                <FormControlLabel id="root-nodes-checkbox" control={<Checkbox sx={checkboxTheme} onChange={(e) => handleCheckbox(e,"is:root", isRootNodesChecked,setIsRootNodesChecked)} checked={isRootNodesChecked} />} label="Root nodes" />
                <MultipleSelectFilter label="Translated into" filterValue={chosenLanguagesCodes} listOfChoices={ISO6391.getAllNames()} mapCodeToValue={ISO6391.getName} mapValueToCode={ISO6391.getCode} setQ={setQ} keySearchTerm="language" setCurrentPage={setCurrentPage}/>
                <MultipleSelectFilter label="Not translated into" filterValue={withoutChosenLanguagesCodes} listOfChoices={ISO6391.getAllNames()} mapCodeToValue={ISO6391.getName} mapValueToCode={ISO6391.getCode} setQ={setQ} keySearchTerm="language:not" setCurrentPage={setCurrentPage}/>
                <FilterInput label="Is parent of (id)" filterValue={parentId} setFilterValue={setParentId} setQ={setQ} keySearchTerm="parent" setCurrentPage={setCurrentPage}/>
                <FilterInput label="Is child of (id)" filterValue={childId} setFilterValue={setChildId} setQ={setQ} keySearchTerm="child" setCurrentPage={setCurrentPage}/>
                <FilterInput label="Is ancestor of (id)" filterValue={ancestorId} setFilterValue={setAncestorId} setQ={setQ} keySearchTerm="ancestor" setCurrentPage={setCurrentPage}/>
                <FilterInput label="Is descendant of (id)" filterValue={descendantId} setFilterValue={setDescendantId} setQ={setQ} keySearchTerm="descendant" setCurrentPage={setCurrentPage}/>
            </Box>
            <AdvancedResearchResults taxonomyName={taxonomyName} branchName={branchName} nodeIds={entryNodeSearchResult?.nodes.map((node) => node.id)??[]} nodeCount={entryNodeSearchResult?.nodeCount} currentPage={currentPage} setCurrentPage={setCurrentPage}/>
        </Box>
    )
}

export const SearchNodeWrapper = () => {
    const { taxonomyName, branchName } = useParams();
  
    if (!taxonomyName || !branchName)
      return (
        <Typography variant="h3">
          Oops, something went wrong! Please try again later.
        </Typography>
      );
  
    return <AdvancedResearchForm taxonomyName={taxonomyName} branchName={branchName} />;
  };