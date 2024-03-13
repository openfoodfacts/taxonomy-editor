import { useParams, useNavigate, useLocation } from "react-router-dom";
import { useState } from "react";
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
import { parseFilterSearchTerm, splitQueryIntoSearchTerms } from "./queryParser";

// type AdvancedResearchFormProps = {
//     taxonomyName: string;
//     branchName: string;
//   };
//   { taxonomyName, branchName }: AdvancedResearchFormProps

const checkboxTheme = {
    color: "#201a17",
    '&.Mui-checked': {
      color: "#341100",
    },
}

export type FiltersType = {
    is_root: boolean;
    is_modified: boolean;
};

const emptyFilters = {
    is_root: false,
    is_modified: false
}; 

const AdvancedResearchForm = () => {

    const navigate = useNavigate();
    const location = useLocation();

    const queryParams = new URLSearchParams(location.search);

    const initializeFilters = () => {
        const isRootString = queryParams.get("is_root");
        const isRoot = isRootString === null ? false : true;

        const isModifiedString = queryParams.get("is_modified");
        const isModified = isModifiedString === null ? false : true;

        return {
            is_root: isRoot,
            is_modified: isModified,
        }
    }

    const findExpressionFromFilters = (filters:FiltersType) => {
        let newExpression = "";
        for (const filter in filters) {
            const value = filters[filter]
            if (typeof value === "boolean" && value === true) {
                newExpression += " " + filter.replace("_",":")
            }
        }
        return newExpression;
    }

    const initFilters = initializeFilters();
    const initExpression = findExpressionFromFilters(initFilters);



    console.log("initFilters() = ",initFilters);
    const [filters,setFilters] = useState<FiltersType>(initFilters);
    const [searchExpression,setSearchExpression] = useState<string>(initExpression);
    const [isRootNodesChecked,setIsRootNodesChecked] = useState<boolean>(initFilters.is_root);
    const [isModifiedChecked,setIsModifiedChecked] = useState<boolean>(initFilters.is_modified);

    const updateSearchExpression = (updatedFilters:FiltersType) => {
        const newExpression = findExpressionFromFilters(updatedFilters);
        setSearchExpression(newExpression);
    }

    const handleRootNodesCheckbox = (event: React.ChangeEvent<HTMLInputElement>) => {
        const updatedFilters = {...filters, is_root: event.target.checked};
        setIsRootNodesChecked(!isRootNodesChecked);
        setFilters(updatedFilters);
        updateSearchExpression(updatedFilters);
        updateURL(updatedFilters);
      };

    const handleModifiedCheckbox = (event: React.ChangeEvent<HTMLInputElement>) => {
        const updatedFilters = {...filters, is_modified: event.target.checked};
        setIsModifiedChecked(!isModifiedChecked);
        setFilters(updatedFilters);
        updateSearchExpression(updatedFilters);
        updateURL(updatedFilters);
    };

    const handleSearchInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setSearchExpression(event.target.value);
    };

    const handleEnterKeyPress = (event: React.KeyboardEvent<HTMLInputElement>) => {
        if (event.key === 'Enter') {
            // Update URL when Enter key is pressed
            const searchTerms = splitQueryIntoSearchTerms(searchExpression);
            let updatedFilters = emptyFilters;
            console.log("searchTerms = ",searchTerms);
            for (const searchTerm of searchTerms) {
                const filterToUpdate = parseFilterSearchTerm(searchTerm);
                console.log("filterToUpdate : ",filterToUpdate);
                if (filterToUpdate!==null) {
                    updatedFilters = {...updatedFilters,...filterToUpdate};
                }
            }
            setFilters(updatedFilters);
            console.log("enter was pressed");
            console.log("filters = ", updatedFilters);
            event.preventDefault();
            updateURL(updatedFilters);
        }
    };

    const updateURL = (filters: FiltersType) => {
        const queryParams = new URLSearchParams();

        for (const filter in filters) {
            const value = filters[filter];
            if (value) {
                queryParams.set(filter, value.toString());
            } else {
                queryParams.delete(filter);
            }
        }

        const newUrl = `?${queryParams.toString()}`;
        console.log("newUrl = ",newUrl);
        navigate(newUrl);
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
                <FormControlLabel id="root-nodes-checkbox" control={<Checkbox sx={checkboxTheme} onChange={handleRootNodesCheckbox} checked={isRootNodesChecked} />} label="Root nodes" />
                <FormControlLabel id="modified-checkbox" control={<Checkbox sx={checkboxTheme} onChange={handleModifiedCheckbox} checked={isModifiedChecked} />} label="Modified" /> 
            </Box>
        </Box>
    )
}

export const AdvancedResearchFormWrapper = () => {
    const { taxonomyName, branchName } = useParams();
  
    if (!taxonomyName || !branchName)
      return (
        <Typography variant="h3">
          Oops, something went wrong! Please try again later.
        </Typography>
      );
  
    // return <AdvancedResearchForm taxonomyName={taxonomyName} branchName={branchName} />;
    return <AdvancedResearchForm />;
  };