import useFetch from "../../components/useFetch";
import { API_URL } from "../../constants";
import { Typography, Box, TextField, Stack, Button, IconButton, Paper, FormControl, InputLabel } from "@mui/material";
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import EditIcon from '@mui/icons-material/Edit';
import { useNavigate } from "react-router-dom";
import AddBoxIcon from '@mui/icons-material/AddBox';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import Select from '@mui/material/Select';
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline';
import * as uuid from "uuid";
import ISO6391 from 'iso-639-1';
import { useState } from "react";

const Entry = () => {
    const url = API_URL+'nodes';
    const title = "Test";
    const {data: nodes, isPending, errorMessage} = useFetch(url);
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
        const data = {"main_language": newLanguageCode};
        fetch(url+`/${newNodeID}`, {
            method : 'POST',
            headers: {"Content-Type" : "application/json"},
            body: JSON.stringify(data)
        }).then(() => {
            handleCloseAddDialog();
            nodes.push([{"id" : newNodeID, ...data}]) // Not required after "all nodes" table removal
            handleOpenSuccessDialog();
        }).catch((errorMessage) => {
            console.log(errorMessage);
        })
    }
    
    if (errorMessage) {
        return (
            <div className="all-entries">
                {errorMessage}
            </div>
        )
    }
    if (isPending) {
        return (
            <div className="all-entries">
                Loading...
            </div>
        )
    }
    return (
        <div className="all-entries">
            <Box>
                <Typography sx={{mb: 1, mt:2, ml: 2}} variant="h4">
                    List of nodes in {title} Taxonomy:
                </Typography>
                <Typography variant="h6" sx={{mt: 2, ml: 2, mb: 1}}>
                    Number of nodes in taxonomy: {nodes.length}
                </Typography>
                {/* Table for listing all nodes in taxonomy */}
                <TableContainer sx={{ml: 2}} component={Paper}>
                    <Table sx={{ width: 400 }}>
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
                                        <IconButton onClick={event => handleClick(event, node[0].id) } aria-label="edit">
                                            <EditIcon color="primary"/>
                                        </IconButton>
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </TableContainer>
                {/* Dialog box for adding translations */}
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
                    <Button sx={{fontFamily: 'Roboto, Helvetica, Arial, sans-serif'}} onClick={handleCloseSuccessDialog} autoFocus>
                        Continue
                    </Button>
                    </DialogActions>
                </Dialog>
            </Box>
        </div>
    );
}
 
export default Entry;