import { Typography, Stack, IconButton, Button, Box } from "@mui/material";
import { useState, useEffect } from "react";
import { Link, useParams } from "react-router-dom";
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import AccumulateAllComponents from "./AccumulateAllComponents";
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline';
import { createBaseURL } from "./createURL";

const EditEntry = ({setDisplayedPages}) => {
    const { taxonomyName, branchName, id } = useParams();
    const urlPrefix = `${taxonomyName}/${branchName}/`;
    const baseUrl = createBaseURL(taxonomyName, branchName);
    const [openDeleteDialog, setOpenDeleteDialog] = useState(false);
    const [openSuccessDialog, setOpenSuccessDialog] = useState(false);
    const greyHexCode = "#808080";

    // Set url prefix for navbar component
    useEffect(
        function addUrlPrefixToNavbar() {
            setDisplayedPages([
                { url: urlPrefix+"entry", translationKey: "Nodes" },
                { url: urlPrefix+"search", translationKey: "Search" }
            ])
        }, [urlPrefix, setDisplayedPages]
    );

    // Helper functions for Dialog component
    const handleCloseDeleteDialog = () => { setOpenDeleteDialog(false); }
    const handleOpenDeleteDialog = () => { setOpenDeleteDialog(true); }
    const handleOpenSuccessDialog = () => { setOpenSuccessDialog(true); }
    
    const handleDeleteNode = () => {
        const data = {"id" : id}
        fetch(baseUrl+'nodes', {
            method : 'DELETE',
            headers: {"Content-Type" : "application/json"},
            body: JSON.stringify(data)
        }).then(() => {
            handleCloseDeleteDialog();
            handleOpenSuccessDialog();
        }).catch(() => {})
    }

    return (
        <Box>
            {/* Renders id of current node */}
            <Box>
                <Stack direction="row" alignItems="center">
                    <Typography sx={{mb: 2, mt:2, ml: 2}} variant="h4">
                        You are now editing "{id}"
                    </Typography>
                    <IconButton sx={{ml: 1, color: greyHexCode}} onClick={handleOpenDeleteDialog}>
                        <DeleteOutlineIcon />
                    </IconButton>
                </Stack>
            </Box>
            {/* Renders node info based on id */}
            <AccumulateAllComponents id={id} taxonomyName={taxonomyName} branchName={branchName} />
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
                <Button onClick={handleCloseDeleteDialog}>
                    Cancel
                </Button>
                <Button sx={{color: '#ff0000'}} onClick={handleDeleteNode} autoFocus>
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
                <Button 
                    component={Link} 
                    to={`${urlPrefix}/entry`}
                    autoFocus
                >
                    Continue
                </Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
}
 
export default EditEntry;