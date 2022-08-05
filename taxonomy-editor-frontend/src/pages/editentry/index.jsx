import { Typography } from "@mui/material";
import { useParams } from "react-router-dom";
import useFetch from "../../components/useFetch";
import { API_URL } from "../../constants";
import AccumulateAllComponents from "./AccumulateAllComponents";

const EditEntry = () => {
    let url = API_URL;
    let isEntry = false;
    const { id } = useParams();
    if (id.startsWith('__header__')) { url += 'header/' }
    else if (id.startsWith('__footer__')) { url += 'footer/' }
    else if (id.startsWith('synonym')) { url += `synonym/${id}/` }
    else if (id.startsWith('stopword')) { url += `stopword/${id}/` }
    else { url += `entry/${id}/`; isEntry = true; }

    const { data: node, error, isPending } = useFetch(url);
    if (error) {
        return (<div>{error}</div>)
    }

    return (
        <div className="main-content">
            <div className="node-title">
                <Typography sx={{mb: 2, mt:2, ml: 2}} variant="h4">
                    You are now editing "{id}" 
                </Typography>
            </div>
            <AccumulateAllComponents incomingNodeObject={node?.[0]} id={id} isEntry={isEntry} url={url} />
        </div>
    );
}
 
export default EditEntry;