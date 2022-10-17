import { Typography, Box, Grid, TextField, Stack, FormControl, InputLabel, Select } from "@mui/material";
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
                throw new Error("Project already exists!");
            }
            navigate(`/${taxonomyName}/${branchName}/entry`)
        }).catch((errorMessage) => {
            console.log(errorMessage)
        })
    }
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
        </Box>
    );
}
 
export default StartProject;