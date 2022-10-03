import { Alert, Box, Button, Snackbar, Typography } from "@mui/material";
import { useEffect, useState } from "react";
import useFetch from "../../components/useFetch";
import ListEntryParents from "./ListEntryParents";
import ListEntryChildren from "./ListEntryChildren";
import ListTranslations from "./ListTranslations";
import ListAllEntryProperties from "./ListAllEntryProperties";
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

    const { data: node, isPending, isError, isSuccess, errorMessage } = useFetch(url);
    const [nodeObject, setNodeObject] = useState(null); // Storing updates to node
    const [updateChildren, setUpdateChildren] = useState([]); // Storing updates of children in node
    const [open, setOpen] = useState(false); // Used for Dialog component

    // Setting state of node after fetch
    useEffect(() => {
        setNodeObject(node?.[0]);
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

    // Function handling updation of node
    const handleSubmit = () => {
        const {id, ...data} = nodeObject // ID not allowed in POST
        let allUrlsAndData = [[url, data]]
        if (isEntry) {
            allUrlsAndData.push([url+'children/', updateChildren])
        }
        Promise.all(allUrlsAndData.map(([url, data]) => {
            return fetch(url, {
                method : 'POST',
                headers: {"Content-Type" : "application/json"},
                body: JSON.stringify(data)
            })
        })).then(() => {
            setOpen(true);
        }).catch(() => {})
    }
    return ( 
        <Box>
            {/* Based on isEntry, respective components are rendered */}
            { isEntry ? 
                <Box>
                    { !!nodeObject &&
                        <>  <ListEntryParents url={url+'parents'} />
                            <ListEntryChildren url={url+'children'} setUpdateNodeChildren={setUpdateChildren} />
                            <ListTranslations nodeObject={nodeObject} setNodeObject={setNodeObject} /> 
                            <ListAllEntryProperties nodeObject={nodeObject} setNodeObject={setNodeObject} /> </> }
                </Box> :
                <>  <ListAllNonEntryInfo nodeObject={nodeObject} id={id} setNodeObject={setNodeObject} /> </>
            }
            {/* Button for submitting edits */}
            <Button
                variant="contained"
                onClick={handleSubmit}
                sx={{ml: 4, mt:2, width: 130}}>
                    Submit
            </Button>
            {/* Snackbar for acknowledgment of update */}
            <Snackbar anchorOrigin={{vertical: 'top', horizontal: 'right'}} open={open} autoHideDuration={3000} onClose={handleClose}>
                <Alert elevation={6} variant="filled" onClose={handleClose} severity="success">
                    The node has been successfully updated!
                </Alert>
            </Snackbar>
        </Box>
     );
}
export default AccumulateAllComponents;