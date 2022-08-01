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
            <Typography sx={{ml: 4, mb: 1, textDecoration: 'underline'}} variant='h5' component={'div'}>Translations</Typography>
            <Typography sx={{ml: 4}} variant='h6'>
                { nodeObject && <ListTranslations nodeObject={nodeObject} languageNames={languageNames} /> }
            </Typography>
            { nodeObject && <ListAllProperties nodeObject={nodeObject} /> }
        </div>
    );
}
 
export default ListAllEntryProperties;