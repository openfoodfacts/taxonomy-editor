import { Typography, Box, Grid, TextField, Stack, FormControl, InputLabel, Select, Button } from "@mui/material";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { TAXONOMY_NAMES } from "../../constants";

const StartProject = () => {
    const [branchName, setBranchName] = useState("")
    const [taxonomyName, setTaxonomyName] = useState("additives")
    const [description, setDescription] = useState("");
    const navigate = useNavigate();
    
    function handleSubmit() {
        // Work in progress..
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
                                        <option value={element.toLowerCase()}>{element}</option>
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
                <Button
                    variant="contained"
                    onClick={handleSubmit}
                    sx={{mt:4, width: 130}}>
                        Submit
                </Button>
            </Grid>
        </Box>
    );
}
 
export default StartProject;