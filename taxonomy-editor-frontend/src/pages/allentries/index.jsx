import { Typography, Snackbar, Alert, Box, TextField, Stack, Button, IconButton, Paper, FormControl, InputLabel } from "@mui/material";
import useFetch from "../../components/useFetch";
import { Link, useParams } from "react-router-dom";
import { useState } from "react";
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
import { useEffect } from "react";

const Entry = ({setDisplayedPages}) => {
    const { taxonomyName, branchName } = useParams();
    const title = taxonomyName.charAt(0).toUpperCase() + taxonomyName.slice(1);
    const baseURL = createBaseURL(taxonomyName, branchName);
    const urlPrefix = `${taxonomyName}/${branchName}/`;
    const { data: nodes, isPending, isError, isSuccess, errorMessage } = useFetch(`${baseURL}rootnodes`);

    const [nodeType, setNodeType] = useState('entry'); // Used for storing node type
    const [newLanguageCode, setNewLanguageCode] = useState(null); // Used for storing new Language Code
    const [newNode, setnewNode] = useState(null); // Used for storing canonical tag
    const [isValidLanguageCode, setIsValidLanguageCode] = useState(false); // Used for validating a new LC
    const [openAddDialog, setOpenAddDialog] = useState(false);
    const [openSuccessSnackbar, setOpenSuccessSnackbar] = useState(false);

    // Set url prefix for navbar component
    useEffect(() => {
        setDisplayedPages([
            { url: urlPrefix+"entry", translationKey: "Nodes" },
            { url: urlPrefix+"search", translationKey: "Search" }
        ])
    }, [urlPrefix, setDisplayedPages])

    // Helper functions for Dialog component
    function handleCloseAddDialog() { setOpenAddDialog(false); }
    function handleOpenAddDialog() { setOpenAddDialog(true); }
    function handleOpenSuccessSnackbar() { setOpenSuccessSnackbar(true); }
    function handleCloseSuccessSnackbar() { setOpenSuccessSnackbar(false); }
    
    function handleAddNode() {
        const newNodeID = newLanguageCode + ':' + newNode // Reconstructing node ID
        const data = {"id": newNodeID, "main_language": newLanguageCode};
        fetch(baseURL+'nodes', {
            method : 'POST',
            headers: {"Content-Type" : "application/json"},
            body: JSON.stringify(data)
        }).then(() => {
            handleCloseAddDialog();
            handleOpenSuccessSnackbar();
        }).catch((errorMessage) => {
            // Do nothing
        })
    }
    if (isError) {
        return (
            <Box>
                <Typography variant='h5'>{errorMessage}</Typography>
            </Box>
        )
    }
    if (isPending) {
        return (
            <Box>
                <Typography variant='h5'>Loading..</Typography>
            </Box>
        )
    }
    return (
        <Box>
            <Typography sx={{mb: 1, mt:2, ml: 2}} variant="h4">
                List of root nodes in {title} Taxonomy:
            </Typography>
            <Typography variant="h6" sx={{mt: 2, ml: 2, mb: 1}}>
                Number of root nodes in taxonomy: {nodes.length}
            </Typography>
            {/* Table for listing all nodes in taxonomy */}
            <TableContainer sx={{ml: 2, width: 375}} component={Paper}>
                <Table>
                    <TableHead>
                    <TableRow>
                        <Stack direction="row" alignItems="center">
                            <TableCell align="left">
                            <Typography variant="h6">
                                Nodes
                            </Typography>
                            </TableCell>
                            <IconButton sx={{ml: 1, color: "#808080"}} onClick={handleOpenAddDialog}>
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
                        {nodes.map((node) => (
                            <TableRow
                            key={node[0].id}
                            >
                                <TableCell align="left" component="td" scope="row">
                                    <Typography variant="subtitle1">
                                        {node[0].id}
                                    </Typography>
                                </TableCell>
                                <TableCell align="left" component="td" scope="row">
                                    <IconButton 
                                        component={Link}
                                        to={`${node[0].id}`}
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
                            <option value={'entry'}>Entry</option>
                        </Select>
                    </FormControl>
                </Stack>
                <Stack direction="row" alignItems="center" sx={{m: 2}}>
                    <Typography>Main Language</Typography>
                    <TextField
                        onChange={(e) => { 
                            setNewLanguageCode(e.target.value);
                            setIsValidLanguageCode(ISO6391.validate(e.target.value));
                        }}
                        label="Language Code"
                        error={!isValidLanguageCode}
                        sx={{width : 150, ml: 5}}
                        size="small"
                        variant="outlined"
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
        </Box>
    );
}
 
export default Entry;