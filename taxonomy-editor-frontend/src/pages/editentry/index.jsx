import { Typography } from "@mui/material";
import { useParams } from "react-router-dom";
import FetchRelations from "./FetchRelations";
import useFetch from "../../components/useFetch";
import ListAllEntryProperties from "./ListAllEntryProperties";
import ListAllOtherProperties from "./ListAllOtherProperties";
import AccumulateAllComponents from "./AccumulateAllComponents";

const EditEntry = () => {
    let url = 'http://localhost:80/'
    let isEntry = false;
    const { id } = useParams();

    if (id.startsWith('__header__')) { url += 'header/' }
    else if (id.startsWith('__footer__')) { url += 'footer/' }
    else if (id.startsWith('synonym')) { url += `synonym/${id}/` }
    else if (id.startsWith('stopword')) { url += `stopword/${id}/` }
    else { url += `entry/${id}/`; isEntry = true; }

    const { data: node, error, isPending } = useFetch(url);
    let nodeObject = null;
    if (error) {
        return (<div>{error}</div>)
    }

    if (!isPending) {
        nodeObject = node[0];
    }

    return (
        <div className="main-content">
            <div className="node-title">
                <Typography sx={{mb: 2, mt:2, ml: 2}} variant="h4">
                    You are now editing "{id}" 
                </Typography>
            </div>
            <AccumulateAllComponents incomingNodeObject={nodeObject} isEntry={isEntry} url={url} />
        </div>
    );
}
 
export default EditEntry;