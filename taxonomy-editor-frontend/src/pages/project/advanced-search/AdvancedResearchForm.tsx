import { useParams, useNavigate, useLocation } from "react-router-dom";
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
    Select,
    MenuItem,
    InputLabel,
    ListItemText,
  } from "@mui/material";
import SearchIcon from '@mui/icons-material/Search';
import { parseFilterSearchTerm, splitQueryIntoSearchTerms } from "./queryParser";

const checkboxTheme = {
    color: "#201a17",
    '&.Mui-checked': {
      color: "#341100",
    },
}

export type FiltersType = {
    is_root: boolean;
    is_modified: boolean;
    with_languages: string[];
    without_languages: string[];
};

const emptyFilters: FiltersType = {
    is_root: false,
    is_modified: false,
    with_languages: [],
    without_languages: [],
}; 

const AdvancedResearchForm = () => {

    const navigate = useNavigate();
    const location = useLocation();

    const queryParams = new URLSearchParams(location.search);

    const initializeFilters = () :FiltersType => {
        const isRootString = queryParams.get("is_root");
        const isRoot = isRootString === null ? false : true;

        const isModifiedString = queryParams.get("is_modified");
        const isModified = isModifiedString === null ? false : true;

        const withLanguagesString = queryParams.get("with_languages");
        const withLanguages = withLanguagesString === null ? [] : withLanguagesString.split("+");

        const withoutLanguagesString = queryParams.get("without_languages");
        const withoutLanguages = withoutLanguagesString === null ? [] : withoutLanguagesString.split("+");

        return {
            is_root: isRoot,
            is_modified: isModified,
            with_languages: withLanguages, 
            without_languages: withoutLanguages,
        }
    }

    const findExpressionFromFilters = (filters:FiltersType) => {
        let newExpression = "";
        for (const filter in filters) {
            const value = filters[filter]
            if (typeof value === "boolean" && value === true) {
                newExpression += " " + filter.replace("_",":")
            } else if (Array.isArray(value) && value.length>0) {
                let filter_expression="";
                switch (filter) {
                    case "with_languages":
                        filter_expression="language";
                        break;
                    default:
                        break;
                }
                for (const element of value) {
                    newExpression+= " " + filter_expression + ":" + element;
                }
            }
        }
        return newExpression;
    }

    // Fetch URL parameters to retrieve previously selected filters
    // Build search expression from these filters
    const initFilters = initializeFilters();
    const initExpression = findExpressionFromFilters(initFilters);

    const [_,setFilters] = useState<FiltersType>(initFilters);
    const [searchExpression,setSearchExpression] = useState<string>(initExpression);
    const [isRootNodesChecked,setIsRootNodesChecked] = useState<boolean>(initFilters.is_root);
    const [isModifiedChecked,setIsModifiedChecked] = useState<boolean>(initFilters.is_modified);
    const [chosenLanguagesCodes, setChosenLanguagesCodes] = useState(initFilters.with_languages);

    const updateSearchExpression = useCallback((updatedFilters:FiltersType) => {
        const newExpression = findExpressionFromFilters(updatedFilters);
        setSearchExpression(newExpression);
    },[])

    //Update the page url on the expression in the searchbar
    const updateURL = useCallback((filters: FiltersType) => {
        const queryParams = new URLSearchParams();

        for (const filter in filters) {
            const value = filters[filter];
            if (Array.isArray(value)) {
                if (value.length===0) {
                    queryParams.delete(filter);
                } else {
                    queryParams.set(filter, value.join("+"));
                }
            } else {
                // value is a boolean
                if (value) {
                    queryParams.set(filter, value.toString());
                } else {
                    queryParams.delete(filter);
                }
            }
        }

        const newUrl = `?${queryParams.toString()}`;
        navigate(newUrl);
    },[navigate]);

    useEffect(() => {
        const updatedFilters = {
            is_root: isRootNodesChecked,
            is_modified: isModifiedChecked,
            with_languages: chosenLanguagesCodes, 
            without_languages: [],
        }
        setFilters(updatedFilters);
        updateSearchExpression(updatedFilters);
        updateURL(updatedFilters);
      }, [chosenLanguagesCodes, isModifiedChecked, isRootNodesChecked, updateSearchExpression, updateURL]);

    const handleCheckbox = (
        event: React.ChangeEvent<HTMLInputElement>,
        filterKey: keyof FiltersType,
        setChecked: React.Dispatch<React.SetStateAction<boolean>>,
    ) => {
        setChecked(event.target.checked);
    }

    const updateFiltersStates = (filters: FiltersType) => {
        setIsRootNodesChecked(filters.is_root);
        setIsModifiedChecked(filters.is_modified);
    }

    const handleSearchInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setSearchExpression(event.target.value);
    };

    const handleEnterKeyPress = (event: React.KeyboardEvent<HTMLInputElement>) => {
        if (event.key === 'Enter') {
            // Update URL when Enter key is pressed
            const searchTerms = splitQueryIntoSearchTerms(searchExpression);
            // let updatedFilters = emptyFilters;
            let updatedIsRootNodes = false;
            let updatedIsModified = false;
            const updatedChosenLanguagesCodes:string[] = [];
            for (const searchTerm of searchTerms) {
                const filterToUpdate = parseFilterSearchTerm(searchTerm);
                if (filterToUpdate!==null) {
                    const filterName = Object.keys(filterToUpdate)[0]; // Récupérer la seule clé de l'objet
                    const filterValue = filterToUpdate[filterName];
                    switch(filterName) {
                        case "is_root":
                            updatedIsRootNodes = filterValue;
                            // setIsRootNodesChecked(filterValue);
                            break;
                        case "is_modified":
                            updatedIsModified = filterValue;
                            // setIsModifiedChecked(filterValue);
                            break;
                        case "with_languages":
                            console.log("filterValue = ",filterValue);
                            console.log("current languages = ", chosenLanguagesCodes);
                            console.log("new languages without filter = ",[...chosenLanguagesCodes,filterValue[0]]);
                            console.log("new languages with filter = ",[...chosenLanguagesCodes,filterValue[0]].filter((item,
                                index) => chosenLanguagesCodes.indexOf(item) === index));
                            updatedChosenLanguagesCodes.push(filterValue[0]);
                            // setChosenLanguagesCodes([...chosenLanguagesCodes,filterValue[0]]);
                    }
                    // if (typeof filterValue === "boolean") {
                    //     updatedFilters = {...updatedFilters,...filterToUpdate};
                    // } else if (Array.isArray(filterValue)) {
                    //     updatedFilters[filterName].push(filterValue[0]);
                    // }
                }
            }
            // setFilters(updatedFilters);
            setIsRootNodesChecked(updatedIsRootNodes);
            setIsModifiedChecked(updatedIsModified);
            setChosenLanguagesCodes(updatedChosenLanguagesCodes);
            event.preventDefault();
            // updateURL(updatedFilters);
            // updateFiltersStates(updatedFilters);
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
                <FormControlLabel id="root-nodes-checkbox" control={<Checkbox sx={checkboxTheme} onChange={(e) => handleCheckbox(e,"is_root",setIsRootNodesChecked)} checked={isRootNodesChecked} />} label="Root nodes" />
                <FormControlLabel id="modified-checkbox" control={<Checkbox sx={checkboxTheme} onChange={(e) => handleCheckbox(e,"is_modified",setIsModifiedChecked)} checked={isModifiedChecked} />} label="Modified" />
                <FormControl sx={{ m: 1, minWidth: 120 }}>
                    <InputLabel id="demo-multiple-name-label">With languages</InputLabel>
                    <Select
                        id="languages-filter"
                        multiple
                        value={chosenLanguagesCodes}
                        onChange={
                            (event) =>{
                                console.log("chosen languages = ",event.target.value as string[])
                              setChosenLanguagesCodes(event.target.value as string[]) // type casting to string[] due to the `multiple` prop
                          }}
                        input={<OutlinedInput label="Languages" />}
                        renderValue={(selected) =>
                            selected
                              .map((langCode) => ISO6391.getName(langCode))
                              .filter(Boolean) //to ignore "xx" language
                              .join(", ")
                          }
                        >
                        {ISO6391.getAllNames()
                        .sort()
                        .map((languageNameItem) => {
                            const languageCodeItem = ISO6391.getCode(languageNameItem);
                            return (
                            <MenuItem key={languageCodeItem} value={languageCodeItem}>
                                <Checkbox
                                checked={chosenLanguagesCodes.includes(languageCodeItem)}
                                />
                                <ListItemText primary={languageNameItem} />
                            </MenuItem>
                            );
                        })}
                    </Select>
                </FormControl> 
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