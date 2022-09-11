import { Typography, Stack, IconButton, Button } from "@mui/material";
import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import AccumulateAllComponents from "./AccumulateAllComponents";
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline';
import { API_URL } from "../../constants";

const EditEntry = () => {
    const { id } = useParams();
    const url = API_URL+'nodes';
    const [openDeleteDialog, setOpenDeleteDialog] = useState(false);
    const [openSuccessDialog, setOpenSuccessDialog] = useState(false);
    const navigate = useNavigate();

    // Handler function for button clicks
    const handleClick = (event) => {
        event.preventDefault();
        navigate('/entry');
    }

    // Helper functions for Dialog component
    function handleCloseDeleteDialog() { setOpenDeleteDialog(false); }
    function handleOpenDeleteDialog() { setOpenDeleteDialog(true); }
    function handleOpenSuccessDialog() { setOpenSuccessDialog(true); }
    
    function handleDeleteNode() {
        const data = {"id" : id}
        fetch(url, {
            method : 'DELETE',
            headers: {"Content-Type" : "application/json"},
            body: JSON.stringify(data)
        }).then(() => {
            handleCloseDeleteDialog();
            handleOpenSuccessDialog();
        }).catch((errorMessage) => {
            console.log(errorMessage);
        })
    }

    return (
        <div className="main-content">
            {/* Renders id of current node */}
            <div className="node-title">
                <Stack direction="row" alignItems="center">
                    <Typography sx={{mb: 2, mt:2, ml: 2}} variant="h4">
                        You are now editing "{id}"
                    </Typography>
                    <IconButton sx={{ml: 1, color: "#808080"}} onClick={handleOpenDeleteDialog}>
                        <DeleteOutlineIcon />
                    </IconButton>
                </Stack>
            </div>
            {/* Renders node info based on id */}
            <AccumulateAllComponents id={id} />
            {/* Dialog box for confirmation of deletion of node */}
            <Dialog
                open={openDeleteDialog}
            >
                <DialogTitle>Delete a node</DialogTitle>
                <DialogContent>
                <DialogContentText>
                    Are you sure you want to delete this node?
                </DialogContentText>
                </DialogContent>
                <DialogActions>
                <Button sx={{fontFamily: 'Roboto, Helvetica, Arial, sans-serif'}} onClick={handleCloseDeleteDialog} autoFocus>
                    Cancel
                </Button>
                <Button sx={{fontFamily: 'Roboto, Helvetica, Arial, sans-serif', color: '#ff0000'}} onClick={handleDeleteNode} autoFocus>
                    Delete
                </Button>
                </DialogActions>
            </Dialog>
            {/* Dialog box for acknowledgement of deletion of node */}
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
                    The node {id} has been successfully deleted.
                </DialogContentText>
                </DialogContent>
                <DialogActions>
                <Button sx={{fontFamily: 'Roboto, Helvetica, Arial, sans-serif'}} onClick={handleClick} autoFocus>
                    Continue
                </Button>
                </DialogActions>
            </Dialog>
        </div>
    );
}
 
export default EditEntry;