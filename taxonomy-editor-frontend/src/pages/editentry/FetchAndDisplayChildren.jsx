import useFetch from "../../components/useFetch";
import { Typography, Paper, TextField, Stack, Button, IconButton, Box } from "@mui/material";
import { Link } from "react-router-dom";
import { useEffect, useState } from "react";
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import AddBoxIcon from '@mui/icons-material/AddBox';
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline';
import * as uuid from "uuid";

const FetchChildren = ({url, id, updateNodeChildren, setUpdateNodeChildren}) => {
    const [relations, setRelations] = useState(null);
    const [newChild, setNewChild] = useState(null);
    const [newLanguageCode, setNewLanguageCode] = useState(null);
    const [open, setOpen] = useState(false); // Used for Dialog component
    const { data: incomingData, errorMessage, isPending } = useFetch(url);
    
    useEffect(() => {
        setUpdateNodeChildren(incomingData.map(el => el?.[0]));
        const arrayData = [];
        incomingData.map((el) =>
            arrayData.push(
                {"index" : uuid.v4(), "child" : el?.[0]})
            );
        setRelations(arrayData);
    }, [incomingData])

    // Helper functions for Dialog component
    function handleClose() { setOpen(false); }
    function handleOpen() { setOpen(true); }

    function handleAddChild() {
        const newChildID = newLanguageCode + ':' + newChild; // Reconstructing node ID
        setRelations([...relations, {"index" : uuid.v4(), "child": newChildID}]);
        setUpdateNodeChildren(prevState => {
            const duplicateData = [...prevState];
            duplicateData.push(newChildID);
            return duplicateData
        });
        setOpen(false);
    }

    function handleDeleteChild(index) {
        const duplicateRelations = relations.filter(obj => !(index === obj.index))
        setRelations(duplicateRelations);
        // Updated tags assigned for later use
        const tagsToBeInserted = duplicateRelations.map(el => (el.child))
        setUpdateNodeChildren(tagsToBeInserted);
    }

    // Check error in fetch
    if (errorMessage) {
        return (<Typography sx={{ml: 4}} variant='h5'>{errorMessage}</Typography>)
    }
    if (isPending) {
        return (<Typography sx={{ml: 4}} variant='h5'>Loading..</Typography>)
    }
    return (
        <div className="relations">
            <Stack direction="row" alignItems="center">
                <Typography sx={{ml: 4}} variant='h5' component={'div'}>Children</Typography>
                <IconButton sx={{ml: 1, color: "#808080"}} onClick={handleOpen}>
                    <AddBoxIcon />
                </IconButton>
            </Stack>
            {/* Renders parents or children of the node */}
            {relations && relations.map(relationObject => (
                <Stack key={relationObject['index']} direction="row" alignItems="center">
                    <Link to={`/entry/${relationObject['child']}`} style={{color: '#0064c8', display: 'inline-block'}}>
                        <Typography sx={{ml: 8}} variant='h6'>
                            {relationObject['child']}
                        </Typography>
                    </Link>
                    <IconButton sx={{ml: 1, color: "#808080"}} onClick={(e) => handleDeleteChild(relationObject['index'], e)}>
                        <DeleteOutlineIcon />
                    </IconButton>
                </Stack>
            )) }

            {/* When no parents or children are present */}
            {relations && relations.length === 0 && <Typography sx={{ml: 8, mb: 1, mt: 1}} variant="h6"> None </Typography>}

            {/* Dialog box for adding translations */}
            <Dialog open={open} onClose={handleClose}>
                <DialogTitle>Add a child</DialogTitle>
                <DialogContent>
                <DialogContentText>
                    Enter the name of the child in the format "LC:child_tag"
                </DialogContentText>
                <DialogContentText>
                    Example - en:yogurts
                </DialogContentText>
                <Stack sx={{mt: 2}} direction="row" alignItems="center">
                    <TextField
                        onKeyPress={(e) => { (e.key === 'Enter') && handleAddChild(e) }} 
                        onChange={(e) => { 
                            setNewLanguageCode(e.target.value);
                        }}
                        label="Language Code"
                        sx={{width : 250, marginRight: 1}}
                        size="small"
                        variant="outlined"
                    />
                    <Typography component="h4">:</Typography>
                    <TextField
                        margin="dense"
                        onKeyPress={(e) => { (e.key === 'Enter') && handleAddChild(e) }} 
                        onChange={(e) => { 
                            setNewChild(e.target.value);
                        }}
                        label="Child"
                        sx={{marginLeft: 1}}
                        size="small"
                        fullWidth
                        variant="outlined"
                    />
                </Stack>
                </DialogContent>
                <DialogActions>
                <Button onClick={handleClose}>Cancel</Button>
                <Button 
                    onClick={(e) => {handleAddChild(newChild, e)}}>
                        Add
                </Button>
                </DialogActions>
            </Dialog>
        </div>
    );
}
 
export default FetchChildren;