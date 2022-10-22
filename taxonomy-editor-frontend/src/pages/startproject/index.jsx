import { Typography, Box, Grid, TextField, Stack, Autocomplete, Snackbar, Alert } from "@mui/material";
import LoadingButton from '@mui/lab/LoadingButton';
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { TAXONOMY_NAMES } from "../../constants";
import { createBaseURL } from "../editentry/createURL";

const StartProject = () => {
    const [branchName, setBranchName] = useState("")
    const [taxonomyName, setTaxonomyName] = useState("additives")
    const [description, setDescription] = useState("");
    const [loading, setLoading] = useState(false); 
    const [open, setOpen] = useState(false);
    const [errorMessage, setErrorMessage] = useState("")
    const navigate = useNavigate();
    
    function handleSubmit() {
        const url = createBaseURL(taxonomyName, branchName)
        setLoading(true);
        const dataToBeSent = {'description' : description};
        fetch(url+'import', {
            method : 'POST',
            headers: {"Content-Type" : "application/json"},
            body: JSON.stringify(dataToBeSent)
        }).then((response) => {
            if (!response.ok) {
                return response.json();
            }
            navigate(`/${taxonomyName}/${branchName}/entry`)
        }).then((responseBody) => {
            setErrorMessage(responseBody.detail)
            setOpen(true); setLoading(false);
        })
    }
    function handleClose() {setOpen(false);}
    return (
        <Box>
            <Grid
            container
            direction="column"
            alignItems="center"
            justifyContent="center"
            >
                <Typography sx={{mt: 4}} variant="h3">Start a project</Typography>
                <Stack sx={{mt: 4, mb: 4}} direction="row" alignItems="center">
                    <Typography sx={{mr: 4}} variant="h5">Taxonomy Name</Typography>
                    <Autocomplete
                        sx={{width: 265}}
                        options={ TAXONOMY_NAMES }
                        onChange={(e, selectedTaxonomy) => {
                            if (selectedTaxonomy) setTaxonomyName(selectedTaxonomy.toLowerCase().replaceAll(/\s/g, '_'));
                            else setTaxonomyName(null);
                        }}
                        renderInput={(params) => <TextField {...params} />}
                    >
                    </Autocomplete>
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
                <Stack sx={{mt: 4}} direction="row" alignItems="center">
                    <Typography sx={{mr: 10}} variant="h5">Description</Typography>
                    <TextField
                        sx={{width: 265}}
                        minRows={4}
                        multiline
                        onChange = {event => {
                            setDescription(event.target.value)
                        }}
                        value={description} 
                        variant="outlined" />
                </Stack>
                {/* Button for submitting edits */}
                <LoadingButton
                    variant="contained"
                    loading={loading}
                    disabled={!branchName || !taxonomyName}
                    onClick={handleSubmit}
                    sx={{mt:4, width: 130}}>
                        Submit
                </LoadingButton>
            </Grid>
            <Snackbar anchorOrigin={{vertical: 'top', horizontal: 'right'}} open={open} autoHideDuration={3000} onClose={handleClose}>
                <Alert elevation={6} variant="filled" onClose={handleClose} severity="error">
                    {errorMessage}
                </Alert>
            </Snackbar>
        </Box>
    );
}
 
export default StartProject;