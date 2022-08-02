import { Typography } from "@mui/material";
import { useEffect } from "react";
import { useState } from "react";
import ListAllProperties from "./ListAllProperties";
import ListTranslations from "./ListTranslations";

const ListAllEntryProperties = ({ props }) => {
    const [nodeObject, setNodeObject] = useState(null);
    useEffect(() => {
        setNodeObject(props);
    }, [props])
    
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