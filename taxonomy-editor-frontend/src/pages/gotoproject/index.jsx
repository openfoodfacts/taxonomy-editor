import { Typography, Box, Grid, TextField, Stack, FormControl, InputLabel, Select, Button, Alert, Snackbar } from "@mui/material";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { TAXONOMY_NAMES } from "../../constants";
import { createBaseURL } from "../editentry/createURL";

const GotoProject = () => {
    const [openSnackbar, setOpenSnackbar] = useState(false);
    const [branchName, setBranchName] = useState("");
    const [taxonomyName, setTaxonomyName] = useState("additives");
    const navigate = useNavigate();

    // Helper functions for Dialog component 
    const handleClose = () => {setOpenSnackbar(false)};

    function handleSubmit() {
        const url = createBaseURL(taxonomyName, branchName);
        fetch(url+'rootnodes', {
            method: 'GET',
        }).then(res => { 
            if (!res.ok) {
                throw Error("Could not fetch the data for resource!")
            }
            return res.json();
        }).then((data) => {
            if (data.length === 0) {
                setOpenSnackbar(true);
            } 
            else {
                navigate(`/${taxonomyName}/${branchName}/entry`);
            }
        }).catch(() => {})
    }
    return (
        <Box>
            <Grid
            container
            direction="column"
            alignItems="center"
            justifyContent="center"
            >
                <Typography sx={{mt: 4}} variant="h3">Existing project?</Typography>
                <Stack sx={{mt: 6, mb: 4}} direction="row" alignItems="center">
                    <Typography sx={{mr: 4}} variant="h5">Taxonomy Name</Typography>
                    <FormControl>
                        <InputLabel>Type</InputLabel>
                        <Select
                            native
                            label="Type"
                            value={taxonomyName}
                            onChange={(e) => {
                                setTaxonomyName(e.target.value);
                            }}
                        >
                            {
                                TAXONOMY_NAMES.map((element) => {
                                    return (
                                        <option key={element} value={element.toLowerCase().replaceAll(/\s/g, '_')}>{element}</option>
                                    )
                                })
                            }
                        </Select>
                    </FormControl>
                </Stack>
                <Stack direction="row" alignItems="center">
                    <Typography sx={{mr: 8}} variant="h5">Branch Name</Typography>
                    <TextField
                        size="small"
                        sx={{width: 265}}
                        onChange = {event => {
                            setBranchName(event.target.value)
                        }}
                        value={branchName}
                        variant="outlined" />
                </Stack>
                {/* Button for submitting edits */}
                <Button
                    variant="contained"
                    disabled={!branchName || !taxonomyName}
                    onClick={handleSubmit}
                    sx={{mt:4, width: 130}}>
                        Submit
                </Button>
            </Grid>
            {/* Snackbar for acknowledgment of update */}
            <Snackbar anchorOrigin={{vertical: 'top', horizontal: 'right'}} open={openSnackbar} autoHideDuration={3000} onClose={handleClose}>
                <Alert elevation={6} variant="filled" onClose={handleClose} severity="error">
                    Your project is not found!
                </Alert>
            </Snackbar>
        </Box>
        
    );
}
 
export default GotoProject;