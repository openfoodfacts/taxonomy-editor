import { Button, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle, Typography } from "@mui/material";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import useFetch from "../../components/useFetch";
import { API_URL } from "../../constants";
import FetchRelations from "./FetchAndDisplayRelations";
import ListAllEntryProperties from "./ListAllEntryProperties";
import ListAllOtherProperties from "./ListAllOtherProperties";

// Used for rendering node information
// If node is an "entry": Relations, translations, comments and properties are rendered
// If node is an "stopword/synonym": Stopwords/synonyms, language and comments are rendered
// If node is "header/footer": Comments are rendered

const AccumulateAllComponents = ({ id }) => {
    
    // Finding URL to send requests
    let url = API_URL;
    let isEntry = false;
    if (id.startsWith('__header__')) { url += 'header/' }
    else if (id.startsWith('__footer__')) { url += 'footer/' }
    else if (id.startsWith('synonym')) { url += `synonym/${id}/` }
    else if (id.startsWith('stopword')) { url += `stopword/${id}/` }
    else { url += `entry/${id}/`; isEntry = true; }

    const [nodeObject, setNodeObject] = useState(null); // Storing original node information
    const [updatedNodeObject, setUpdatedNodeObject] = useState(null); // Storing updates to node
    const [open, setOpen] = useState(false); // Used for Dialog component
    const navigate = useNavigate(); // Navigation between pages

    const { data: node, error, isPending } = useFetch(url);

    // Setting state of node after fetch
    useEffect(() => {
        setNodeObject(node?.[0]);
        setUpdatedNodeObject(node?.[0]);
    }, [node])

    // Displaying errors if any
    if (error) {
        return (<div>{error}</div>)
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
            setOpen(true);
        }).catch((error) => {
            console.log(error);
        })
    }
    
    return ( 
        <div className="node-attributes">
            {isPending && <Typography sx={{ml: 4}} variant='h5' component={'div'}>Loading..</Typography>}
            {/* Based on isEntry, respective components are rendered */}
            { isEntry ? 
                <>  <FetchRelations url={url+'parents'} title={'Parents'} />
                    <FetchRelations url={url+'children'} title={'Children'} />
                    <ListAllEntryProperties nodeObject={updatedNodeObject} setNodeObject={setUpdatedNodeObject} originalNodeObject={nodeObject} /> </> :
                <>  <ListAllOtherProperties nodeObject={updatedNodeObject} id={id} setNodeObject={setUpdatedNodeObject} originalNodeObject={nodeObject} /> </>
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
        </div>
     );
}
 
export default AccumulateAllComponents;