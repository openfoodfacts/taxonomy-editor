import useFetch from "../../components/useFetch";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useState } from "react";
import { API_URL } from "../../constants";
import { Typography, Box, TextField, Stack, Button, IconButton, Paper, FormControl, InputLabel } from "@mui/material";
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
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import Select from '@mui/material/Select';
import ISO6391 from 'iso-639-1';

const SearchResults = () => {
    const [searchParams] = useSearchParams();
    let query = searchParams.get('query');
    if (query === "") query = "\"\""
    const url = API_URL+`search?query=${query}`
    const { data: nodes, isPending, isError, isSuccess, errorMessage } = useFetch(url);
    const [nodeType, setNodeType] = useState('entry'); // Used for storing node type
    const [newLanguageCode, setNewLanguageCode] = useState(null); // Used for storing new Language Code
    const [newNode, setnewNode] = useState(null); // Used for storing canonical tag
    const [isValidLC, setisValidLC] = useState(false); // Used for validating a new LC
    const [openAddDialog, setOpenAddDialog] = useState(false);
    const [openSuccessDialog, setOpenSuccessDialog] = useState(false);
    const [btnDisabled, setBtnDisabled] = useState(true);
    const navigate = useNavigate();

    // Handler function for button clicks
    const handleClick = (event, id) => {
        event.preventDefault();
        navigate('/entry/'+id);
    }
    // Helper functions for Dialog component
    function handleCloseAddDialog() { setOpenAddDialog(false); }
    function handleOpenAddDialog() { setOpenAddDialog(true); }
    function handleCloseSuccessDialog() { setOpenSuccessDialog(false); }
    function handleOpenSuccessDialog() { setOpenSuccessDialog(true); }
    
    function handleAddNode() {
        const newNodeID = newLanguageCode + ':' + newNode // Reconstructing node ID
        const data = {"id": newNodeID, "main_language": newLanguageCode};
        fetch(url, {
            method : 'POST',
            headers: {"Content-Type" : "application/json"},
            body: JSON.stringify(data)
        }).then(() => {
            handleCloseAddDialog();
            handleOpenSuccessDialog();
        }).catch((errorMessage) => {
            console.log(errorMessage);
        })
    }

    // Displaying errorMessages if any
    if (isError) {
        return (<Typography variant='h5'>{errorMessage}</Typography>)
    }

    // Loading...
    if (isPending) {
        return (<Typography variant='h5'>Loading..</Typography>)
    }

    return (
        <Box>
            <Typography sx={{mb: 1, mt:2, ml: 2}} variant="h4">
                Search Results
            </Typography>
            <Typography variant="h6" sx={{mt: 2, ml: 2, mb: 1}}>
                Number of nodes found: {nodes.length}
            </Typography>
            {/* Table for listing all nodes in taxonomy */}
            <TableContainer sx={{ml: 2, width: 400}} component={Paper}>
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
                            key={node}
                            >
                                <TableCell align="left" component="td" scope="row">
                                    <Typography variant="subtitle1">
                                        {node}
                                    </Typography>
                                </TableCell>
                                <TableCell align="left" component="td" scope="row">
                                    <IconButton onClick={event => handleClick(event, node) } aria-label="edit">
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
                    <FormControl sx={{ml: 6.5}}>
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
                            const validateBool = ISO6391.validate(e.target.value);
                            validateBool ? setisValidLC(true) : setisValidLC(false);
                            validateBool ? setBtnDisabled(false) : setBtnDisabled(true);
                        }}
                        label="Language Code"
                        error={!isValidLC}
                        sx={{width : 150, ml: 4.5}}
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
                        sx={{width : 150, ml: 11}}
                        size="small"
                        variant="outlined"
                    />
                    </Stack>
                }
                </DialogContent>
                <DialogActions>
                <Button onClick={handleCloseAddDialog}>Cancel</Button>
                <Button 
                    disabled={btnDisabled}
                    onClick={(e) => {handleAddNode(e)}}>
                        Add
                </Button>
                </DialogActions>
            </Dialog>
            {/* Dialog box for acknowledgement of addition of node */}
            <Dialog
                open={openSuccessDialog}
                aria-labelledby="alert-dialog-title"
                aria-describedby="alert-dialog-description"
            >
                <DialogTitle id="alert-dialog-title">
                {"Your edits have been saved!"}
                </DialogTitle>
                <DialogContent>
                <DialogContentText id="alert-dialog-description">
                    The node {newNode} has been successfully added.
                </DialogContentText>
                </DialogContent>
                <DialogActions>
                <Button onClick={handleCloseSuccessDialog} autoFocus>
                    Continue
                </Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
}
 
export default SearchResults;