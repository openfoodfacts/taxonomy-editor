import { Typography, Snackbar, Alert, Box, TextField, Grid, Stack, Button, IconButton, Paper, FormControl, InputLabel, Autocomplete } from "@mui/material";
import useFetch from "../../components/useFetch";
import { Link } from "react-router-dom";
import { useState } from "react";
import Container from '@mui/material/Container';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import EditIcon from '@mui/icons-material/Edit';
import AddBoxIcon from '@mui/icons-material/AddBox';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import Select from '@mui/material/Select';
import ISO6391 from 'iso-639-1';
import { createBaseURL } from "../editentry/createURL";
import { greyHexCode } from "../../constants";

const SearchResults = ({query, taxonomyName, branchName}) => {
    const baseUrl = createBaseURL(taxonomyName, branchName);
    const urlPrefix = `/${taxonomyName}/${branchName}`
    /* eslint no-unused-vars: ["error", { varsIgnorePattern: "__" }] */
    const { data: nodeIds, isPending, isError, __isSuccess, errorMessage } = useFetch(`${baseUrl}search?query=${encodeURI(query)}`);

    const [nodeType, setNodeType] = useState('entry'); // Used for storing node type
    const [newLanguageCode, setNewLanguageCode] = useState(''); // Used for storing new Language Code
    const isValidLanguageCode = ISO6391.validate(newLanguageCode) // Used for validating a new LC
    const [newNode, setnewNode] = useState(null); // Used for storing canonical tag
    const [openAddDialog, setOpenAddDialog] = useState(false);
    const [openSuccessSnackbar, setOpenSuccessSnackbar] = useState(false);

    // Helper functions for Dialog component
    const handleCloseAddDialog = () => { setOpenAddDialog(false); }
    const handleOpenAddDialog = () => { setOpenAddDialog(true); }
    const handleOpenSuccessSnackbar = () => { setOpenSuccessSnackbar(true); }
    const handleCloseSuccessSnackbar = () => { setOpenSuccessSnackbar(false); }
    
    function handleAddNode() {
        const newNodeID = newLanguageCode + ':' + newNode // Reconstructing node ID
        const data = {"id": newNodeID, "main_language": newLanguageCode};
        fetch(baseUrl+'nodes', {
            method : 'POST',
            headers: {"Content-Type" : "application/json"},
            body: JSON.stringify(data)
        }).then(() => {
            handleCloseAddDialog();
            handleOpenSuccessSnackbar();
        }).catch(() => {})
    }

    // Displaying errorMessages if any
    if (isError) {
        return (
            <Container component="main" maxWidth="xs">
            <Grid
            container
            direction="column"
            alignItems="center"
            justifyContent="center"
            >
                <Typography sx={{mt: 2}} variant='h5'>{errorMessage}</Typography>
                </Grid>   
            </Container>
        )
    }

    // Loading...
    if (isPending) {
        return (
            <Grid
            container
            direction="column"
            alignItems="center"
            justifyContent="center"
            >
                <Typography sx={{mt: 2}} variant='h5'>Loading..</Typography>
            </Grid>   
        )
    }

    return (
        <Box>
            <Grid
            container
            direction="column"
            alignItems="center"
            justifyContent="center"
            >
                <Grid item xs={3} sx={{mt: 4}}>
                     <Typography variant="h4">Search Results</Typography>
                </Grid>
                <Typography variant="h6" sx={{mt: 2, mb: 1}}>
                Number of nodes found: {nodeIds.length}
                </Typography>
                {/* Table for listing all nodes in taxonomy */}
                <TableContainer sx={{width: 375}} component={Paper}>
                    <Table>
                        <TableHead>
                        <TableRow>
                            <Stack direction="row" alignItems="center">
                                <TableCell align="left">
                                <Typography variant="h6">
                                    Nodes
                                </Typography>
                                </TableCell>
                                <IconButton sx={{ml: 1, color: greyHexCode}} onClick={handleOpenAddDialog}>
                                    <AddBoxIcon />
                                </IconButton>
                            </Stack>
                            <TableCell align="left">
                            <Typography variant="h6">
                                Action
                            </Typography>
                            </TableCell>
                        </TableRow>
                        </TableHead>
                        <TableBody>
                            {nodeIds.map((nodeId) => (
                                <TableRow
                                key={nodeId}
                                >
                                    <TableCell align="left" component="td" scope="row">
                                        <Typography variant="subtitle1">
                                            {nodeId}
                                        </Typography>
                                    </TableCell>
                                    <TableCell align="left" component="td" scope="row">
                                        <IconButton 
                                            component={Link}
                                            to={`${urlPrefix}/entry/${nodeId}`}
                                            aria-label="edit">
                                            <EditIcon color="primary"/>
                                        </IconButton>
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </TableContainer>
                {/* Dialog box for adding nodes */}
                <Dialog open={openAddDialog} onClose={handleCloseAddDialog}>
                    <DialogTitle>Add a node</DialogTitle>
                    <DialogContent>
                    <Stack direction="row" alignItems="center" sx={{mt: 1, ml: 2, mr: 2, mb: 2}}>
                        <Typography>Type of node</Typography>
                        <FormControl sx={{ml: 7}}>
                            <InputLabel>Type</InputLabel>
                            <Select
                                native
                                label="Type"
                                value={nodeType}
                                onChange={(e) => {
                                    setNodeType(e.target.value);
                                }}
                            >
                                {/* TODO: Add support for synonyms and stopwords */}
                                {/* https://github.com/openfoodfacts/taxonomy-editor/issues/108 */}
                                <option value={'entry'}>Entry</option>
                            </Select>
                        </FormControl>
                    </Stack>
                    <Stack direction="row" alignItems="center" sx={{m: 2}}>
                        <Typography>Main Language</Typography>
                        <Autocomplete
                            options={ISO6391.getAllNames()}
                            onChange={(e,language) => {
                                if (!language) language = '';
                                setNewLanguageCode(ISO6391.getCode(language));
                            }}
                            renderInput={(params) => <TextField error={!isValidLanguageCode} {...params} label="Languages" />}
                            sx={{width : 150, ml: 5}}
                        />
                    </Stack>
                    {
                        nodeType === 'entry' &&
                        <Stack direction="row" alignItems="center" sx={{mt: 2, ml: 2, mr: 2}}>
                        <Typography>Node ID</Typography>
                        <TextField
                            onChange={(e) => { 
                                setnewNode(e.target.value);
                            }}
                            label="Node ID"
                            sx={{width : 150, ml: 11.5}}
                            size="small"
                            variant="outlined"
                        />
                        </Stack>
                    }
                    </DialogContent>
                    <DialogActions>
                    <Button onClick={handleCloseAddDialog}>Cancel</Button>
                    <Button 
                        disabled={!isValidLanguageCode}
                        onClick={(e) => {handleAddNode(e)}}>
                            Add
                    </Button>
                    </DialogActions>
                </Dialog>
                {/* Snackbar for acknowledgment of addition of node */}
                <Snackbar 
                    anchorOrigin={{vertical: 'top', horizontal: 'right'}} 
                    open={openSuccessSnackbar} 
                    autoHideDuration={3000} 
                    onClose={handleCloseSuccessSnackbar}
                >
                    <Alert elevation={6} variant="filled" onClose={handleCloseSuccessSnackbar} severity="success">
                        The node has been successfully added!
                    </Alert>
                </Snackbar>
            </Grid>
        </Box>
    );
}
 
export default SearchResults;