import { Button, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle } from "@mui/material";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import FetchRelations from "./FetchRelations";
import ListAllEntryProperties from "./ListAllEntryProperties";
import ListAllOtherProperties from "./ListAllOtherProperties";

const AccumulateAllComponents = ({ incomingNodeObject, id, isEntry, url }) => {
    const [nodeObject, setNodeObject] = useState(null);
    const [open, setOpen] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        setNodeObject(incomingNodeObject);
    }, [incomingNodeObject])

    const handleClose = () => {setOpen(false)};
    const handleBack = () => {navigate('/entry')};

    const handleSubmit = () => {
        delete nodeObject['id']; // ID not allowed in POST
        fetch(url, {
            method : 'POST',
            headers: {"Content-Type" : "application/json"},
            body: JSON.stringify(nodeObject)
        }).then(() => {
            setOpen(true);
        }).catch((error) => {
            console.log(error);
        })
    }
    
    return ( 
        <div className="node-attributes">
            { isEntry ? 
                <>  <FetchRelations url={url+'parents'} title={'Parents'} />
                    <FetchRelations url={url+'children'} title={'Children'} />
                    <ListAllEntryProperties nodeObject={nodeObject} setNodeObject={setNodeObject} /> </> :
                <>  <ListAllOtherProperties nodeObject={nodeObject} id={id} setNodeObject={setNodeObject} /> </>
            }
            <Button
                variant="contained"
                onClick={handleSubmit}
                sx={{ml: 4, mt:2, width: 130}}>
                    Submit
            </Button>
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