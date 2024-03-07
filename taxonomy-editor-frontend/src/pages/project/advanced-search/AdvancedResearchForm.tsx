import { useParams } from "react-router-dom";
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

type FiltersType = {
    is_root: boolean;
    is_modified: boolean;
};

const AdvancedResearchForm = () => {

    const [searchExpression,setSearchExpression] = useState(""); //à initialiser selon les params de l'url
    const [filters,setFilters] = useState<FiltersType>({
        is_root: false,
        is_modified: false
    });

    const updateSearchExpression = (updatedFilters:FiltersType) => {
        let newExpression = "";
        for (const filter in updatedFilters) {
            const value = updatedFilters[filter]
            if (typeof value === "boolean" && value === true) {
                newExpression += " " + filter.replace("_",":")
            }
        }
        setSearchExpression(newExpression);
    }

    const handleRootNodesCheckbox = (event: React.ChangeEvent<HTMLInputElement>) => {
        const updatedFilters = {...filters, is_root: event.target.checked};
        setFilters(updatedFilters);
        updateSearchExpression(updatedFilters);
      };

    const handleModifiedCheckbox = (event: React.ChangeEvent<HTMLInputElement>) => {
        const updatedFilters = {...filters, is_modified: event.target.checked};
        setFilters(updatedFilters);
        updateSearchExpression(updatedFilters);
    };

    return (
        <Box sx={{ display: 'flex', flexWrap: 'wrap' }}>
            <FormControl fullWidth sx={{ m: 1 }} variant="outlined">
                <OutlinedInput
                    id="search-expression"
                    sx={{backgroundColor:"#f2e9e4"}}
                    startAdornment={<InputAdornment position="start"><SearchIcon/></InputAdornment>}
                    value={searchExpression}
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
                <FormControlLabel id="root-nodes-checkbox" control={<Checkbox sx={checkboxTheme} onChange={handleRootNodesCheckbox}/>} label="Root nodes" />
                <FormControlLabel id="modified-checkbox" control={<Checkbox sx={checkboxTheme} onChange={handleModifiedCheckbox}/>} label="Modified" /> 
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