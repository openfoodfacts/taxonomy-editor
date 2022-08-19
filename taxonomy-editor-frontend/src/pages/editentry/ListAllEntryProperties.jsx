import { Typography } from "@mui/material";
import ListAllProperties from "./ListAllProperties";
import ListTranslations from "./ListTranslations";

// Parent component used for rendering sub-components
// Sub-components are used to render info for an "entry"

const ListAllEntryProperties = ({ nodeObject, setNodeObject, originalNodeObject }) => {
    
    return (
        <div className="allEntryProperties">
            <Typography sx={{ml: 4}} variant='h6'>
                { nodeObject && <ListTranslations nodeObject={nodeObject} setNodeObject={setNodeObject} originalNodeObject={originalNodeObject} /> }
            </Typography>
            { nodeObject && <ListAllProperties nodeObject={nodeObject} setNodeObject={setNodeObject} originalNodeObject={originalNodeObject} /> }
        </div>
    );
}
 
export default ListAllEntryProperties;