import { Box, Typography } from "@mui/material";
import ListAllEntryProperties from "./ListAllEntryProperties";
import ListTranslations from "./ListTranslations";

/**
 * Parent component used for rendering sub-components
 * Sub-components are used to render info for an "entry"
 */

const AccumulateEntryInfo = ({ nodeObject, setNodeObject, originalNodeObject }) => {
    
    return (
        <Box className="allEntryProperties">
            <Typography sx={{ml: 4}} variant='h6'>
                { nodeObject && <ListTranslations nodeObject={nodeObject} setNodeObject={setNodeObject} originalNodeObject={originalNodeObject} /> }
            </Typography>
            { nodeObject && <ListAllEntryProperties nodeObject={nodeObject} setNodeObject={setNodeObject} originalNodeObject={originalNodeObject} /> }
        </Box>
    );
}

export default AccumulateEntryInfo;