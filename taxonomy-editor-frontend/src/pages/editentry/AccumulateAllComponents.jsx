import { Box, Button, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle, Typography } from "@mui/material";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import useFetch from "../../components/useFetch";
import ListAllEntryProperties from "./AccumulateEntryInfo";
import ListEntryParents from "./ListEntryParents";
import ListEntryChildren from "./ListEntryChildren";
import ListAllNonEntryInfo from "./ListAllNonEntryInfo";
import { createURL, getIdType } from "./createURL";

/**
 * Component used for rendering node information
 * If node is an "entry": Relations, translations, comments and properties are rendered
 * If node is an "stopword/synonym": Stopwords/synonyms, language and comments are rendered
 * If node is "header/footer": Comments are rendered  
*/ 

const AccumulateAllComponents = ({ id }) => {

    // Finding URL to send requests
    const url = createURL(id);
    const isEntry = getIdType(id) === 'entry';

    const [nodeObject, setNodeObject] = useState(null); // Storing original node information
    const [updatedNodeObject, setUpdatedNodeObject] = useState(null); // Storing updates to node
    const [updateChildren, setUpdateChildren] = useState([]); // Storing updates of children in node
    const [open, setOpen] = useState(false); // Used for Dialog component
    const navigate = useNavigate(); // Navigation between pages
    const { data: node, isPending, isError, isSuccess, errorMessage } = useFetch(url);

    // Setting state of node after fetch
    useEffect(() => {
        setNodeObject(node?.[0]);
        setUpdatedNodeObject(node?.[0]);
    }, [node])

    // Displaying errorMessages if any
    if (isError) {
        return (<Typography sx={{ml: 4}} variant='h5'>{errorMessage}</Typography>)
    }

    // Loading...
    if (isPending) {
        return (<Typography sx={{ml: 4}} variant='h5'>Loading..</Typography>)
    }
    
    // Helper functions for Dialog component 
    const handleClose = () => {setOpen(false)};
    const handleBack = () => {navigate('/entry')};

    // Function handling updation of node
    const handleSubmit = () => {
        const {id, ...data} = updatedNodeObject // ID not allowed in POST
        fetch(url, {
            method : 'POST',
            headers: {"Content-Type" : "application/json"},
            body: JSON.stringify(data)
        }).then(() => {
            if (isEntry) {
                fetch(url+'children/', {
                    method : 'POST',
                    headers: {"Content-Type" : "application/json"},
                    body: JSON.stringify(updateChildren)
                }).then(() => {
                    setOpen(true);
                }).catch((errorMessage) => {
                    console.log(errorMessage);
                })
            }
        }).catch((errorMessage) => {
            console.log(errorMessage);
        })
    }
    
    return ( 
        <Box className="node-attributes">
            {/* Based on isEntry, respective components are rendered */}
            { isEntry ? 
                <Box>
                    { !!nodeObject &&
                        <>  <ListEntryParents url={url+'parents'} />
                            <ListEntryChildren url={url+'children'} setUpdateNodeChildren={setUpdateChildren} />
                            <ListAllEntryProperties nodeObject={updatedNodeObject} setNodeObject={setUpdatedNodeObject} originalNodeObject={nodeObject} /> </> }
                </Box> :
                <>  <ListAllNonEntryInfo nodeObject={updatedNodeObject} id={id} setNodeObject={setUpdatedNodeObject} originalNodeObject={nodeObject} /> </>
            }
            {/* Button for submitting edits */}
            <Button
                variant="contained"
                onClick={handleSubmit}
                sx={{ml: 4, mt:2, width: 130}}>
                    Submit
            </Button>
            {/* Dialog box for acknowledgment of update */}
            <Dialog
                open={open}
                aria-labelledby="alert-dialog-title"
                aria-describedby="alert-dialog-description"
            >
                <DialogTitle id="alert-dialog-title">
                {"Your edits have been saved!"}
                </DialogTitle>
                <DialogContent>
                <DialogContentText id="alert-dialog-description">
                    The node {id} has been successfully updated.
                </DialogContentText>
                </DialogContent>
                <DialogActions>
                <Button sx={{fontFamily: 'Roboto, Helvetica, Arial, sans-serif'}} onClick={handleBack}>
                    Back to all nodes
                </Button>
                <Button sx={{fontFamily: 'Roboto, Helvetica, Arial, sans-serif'}} onClick={handleClose} autoFocus>
                    Continue Editing
                </Button>
                </DialogActions>
            </Dialog>
        </Box>
     );
}
 
export default AccumulateAllComponents;