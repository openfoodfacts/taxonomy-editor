import { Typography } from "@mui/material";
import ListAllProperties from "./ListAllProperties";
import ListTranslations from "./ListTranslations";

const ListAllEntryProperties = ({ nodeObject, setNodeObject }) => {
    
    let languageNames = new Intl.DisplayNames(['en'], {type: 'language'});
    return (
        <div className="allEntryProperties">
            <Typography sx={{ml: 4}} variant='h6'>
                { nodeObject && <ListTranslations nodeObject={nodeObject} languageNames={languageNames} setNodeObject={setNodeObject} /> }
            </Typography>
            { nodeObject && <ListAllProperties nodeObject={nodeObject} setNodeObject={setNodeObject} /> }
        </div>
    );
}
 
export default ListAllEntryProperties;