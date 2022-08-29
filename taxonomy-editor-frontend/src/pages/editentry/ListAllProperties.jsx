import { Typography, Box } from "@mui/material";

// Sub-component used for rendering comments and properties of an "entry"

const ListAllProperties = ({ nodeObject, setNodeObject }) => {
    return (
        <Box className="all-properties">
            <Typography sx={{ml: 4, mt: 2, mb: 1}} variant='h5'>Comments</Typography>
            <Typography sx={{ml: 4, mt: 2, mb: 1}} variant='h5'>Properties</Typography>
        </Box>
    );
}
 
export default ListAllProperties;