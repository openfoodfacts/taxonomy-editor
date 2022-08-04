import { Button } from "@mui/material";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import FetchRelations from "./FetchRelations";
import ListAllEntryProperties from "./ListAllEntryProperties";
import ListAllOtherProperties from "./ListAllOtherProperties";
import Swal from 'sweetalert2'
import withReactContent from 'sweetalert2-react-content'

const AccumulateAllComponents = ({ incomingNodeObject, isEntry, url }) => {
    const [nodeObject, setNodeObject] = useState(null);
    const SuccessSwal = withReactContent(Swal)

    useEffect(() => {
        setNodeObject(incomingNodeObject);
    }, [incomingNodeObject])

    const navigate = useNavigate();

    const handleSubmit = () => {
        delete nodeObject['id']; // ID not allowed in POST
        fetch(url, {
            method : 'POST',
            headers: {"Content-Type" : "application/json"},
            body: JSON.stringify(nodeObject)
        }).then(() => {
            SuccessSwal.fire({
                title: <strong>Your edit was successful!</strong>,
                icon: 'success'
              }).then(() => {
                return navigate('/entry')
              })
        })
    }
    
    return ( 
        <div className="node-attributes">
            { isEntry && <FetchRelations url={url+'parents'} title={'Parents'} /> }
            { isEntry && <FetchRelations url={url+'children'} title={'Children'} /> }
            { isEntry && <ListAllEntryProperties nodeObject={nodeObject} setNodeObject={setNodeObject} /> }
            { !isEntry && <ListAllOtherProperties nodeObject={nodeObject} setNodeObject={setNodeObject} /> }
            <Button
                variant="contained"
                onClick={handleSubmit}
                sx={{ml: 4, mt:2, width: 150}}>
                    Submit
            </Button>
        </div>
     );
}
 
export default AccumulateAllComponents;