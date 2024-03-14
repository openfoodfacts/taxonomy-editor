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
  } from "@mui/material";
import SearchIcon from '@mui/icons-material/Search';
import { parseFilterSearchTerm, splitQueryIntoSearchTerms } from "./queryParser";
import { MultipleSelectFilter } from "./MultipleSelectFilter";

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
                let isNegative=false;
                switch (filter) {
                    case "with_languages":
                        filter_expression="language";
                        break;
                    case "without_languages":
                        filter_expression="language";
                        isNegative=true;
                        break;
                    default:
                        break;
                }
                for (const element of value) {
                    if (isNegative) {
                        newExpression += ` not(${filter_expression}:${element})`;
                    } else {
                        newExpression += ` ${filter_expression}:${element}`;
                    }
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
    const [withoutChosenLanguagesCodes,setWithoutChosenLanguagesCodes] =useState(initFilters.without_languages);

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
            without_languages: withoutChosenLanguagesCodes,
        }
        setFilters(updatedFilters);
        updateSearchExpression(updatedFilters);
        updateURL(updatedFilters);
      }, [chosenLanguagesCodes, withoutChosenLanguagesCodes, isModifiedChecked, isRootNodesChecked, updateSearchExpression, updateURL]);

    const handleCheckbox = (
        event: React.ChangeEvent<HTMLInputElement>,
        filterKey: keyof FiltersType,
        setChecked: React.Dispatch<React.SetStateAction<boolean>>,
    ) => {
        setChecked(event.target.checked);
    }

    const handleSearchInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setSearchExpression(event.target.value);
    };

    const handleEnterKeyPress = (event: React.KeyboardEvent<HTMLInputElement>) => {
        if (event.key === 'Enter') {
            // Update URL when Enter key is pressed
            const searchTerms = splitQueryIntoSearchTerms(searchExpression);
            let updatedIsRootNodes = false;
            let updatedIsModified = false;
            const updatedChosenLanguagesCodes:string[] = [];
            const updatedWithoutChosenLanguagesCodes:string[] = [];
            for (const searchTerm of searchTerms) {
                const filterToUpdate = parseFilterSearchTerm(searchTerm);
                if (filterToUpdate!==null) {
                    const filterName = Object.keys(filterToUpdate)[0]; // Récupérer la seule clé de l'objet
                    const filterValue = filterToUpdate[filterName];
                    switch(filterName) {
                        case "is_root":
                            updatedIsRootNodes = filterValue;
                            break;
                        case "is_modified":
                            updatedIsModified = filterValue;
                            break;
                        case "with_languages":
                            // console.log("filterValue = ",filterValue);
                            // console.log("current languages = ", chosenLanguagesCodes);
                            // console.log("new languages without filter = ",[...chosenLanguagesCodes,filterValue[0]]);
                            // console.log("new languages with filter = ",[...chosenLanguagesCodes,filterValue[0]].filter((item,
                            //     index) => chosenLanguagesCodes.indexOf(item) === index));
                            updatedChosenLanguagesCodes.push(filterValue[0]);
                            break;
                        case "without_languages":
                            updatedWithoutChosenLanguagesCodes.push(filterValue[0]);
                            break;
                    }
                }
            }
            setIsRootNodesChecked(updatedIsRootNodes);
            setIsModifiedChecked(updatedIsModified);
            setChosenLanguagesCodes(updatedChosenLanguagesCodes);
            setWithoutChosenLanguagesCodes(updatedWithoutChosenLanguagesCodes);
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
                <FormControlLabel id="root-nodes-checkbox" control={<Checkbox sx={checkboxTheme} onChange={(e) => handleCheckbox(e,"is_root",setIsRootNodesChecked)} checked={isRootNodesChecked} />} label="Root nodes" />
                <FormControlLabel id="modified-checkbox" control={<Checkbox sx={checkboxTheme} onChange={(e) => handleCheckbox(e,"is_modified",setIsModifiedChecked)} checked={isModifiedChecked} />} label="Modified" />
                <MultipleSelectFilter label="Translated into" filterValue={chosenLanguagesCodes} setFilterValue={setChosenLanguagesCodes} listOfChoices={ISO6391.getAllNames()} mapCodeToValue={ISO6391.getName} mapValueToCode={ISO6391.getCode} />
                <MultipleSelectFilter label="Not translated into" filterValue={withoutChosenLanguagesCodes} setFilterValue={setWithoutChosenLanguagesCodes} listOfChoices={ISO6391.getAllNames()} mapCodeToValue={ISO6391.getName} mapValueToCode={ISO6391.getCode} />

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