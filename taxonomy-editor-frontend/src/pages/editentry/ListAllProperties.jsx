import { Typography } from "@mui/material";

// Sub-component used for rendering comments and properties of an "entry"

const ListAllProperties = ({ nodeObject, setNodeObject }) => {
    return (
        <div className="all-properties">
            {/* Comments */}
            <Typography sx={{ml: 4, mt: 2, mb: 1}} variant='h5'>Comments</Typography>

            {/* Properties */}
            <Typography sx={{ml: 4, mt: 2, mb: 1}} variant='h5'>Properties</Typography>
        </div>
    );
}
 
export default ListAllProperties;