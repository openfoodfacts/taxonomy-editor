import { TextField, Typography } from "@mui/material";
import { useState } from "react";

const ListAllProperties = ({ nodeObject, setNodeObject }) => {
    let toBeRendered = {}
    Object.keys(nodeObject).forEach((key) => {
        if (key.startsWith('prop')) {
                let property_name = key.split('_').slice(1).join('_');
                toBeRendered[property_name] = nodeObject[key]
            }
    });

    const [changedObj, setChangedObj] = useState(toBeRendered);
    const [changedComment, setChangedComment] = useState({'preceding_lines': nodeObject.preceding_lines.join('')});

    // Helper function used for changing state of properties
    function changeData(key, value) {
        const duplicateData = {...changedObj};
        duplicateData[key] = value;
        setChangedObj(duplicateData);
    }
    
    // Helper function used for changing state of comment
    function changeDataComment(key, value) {
        const duplicateData = {...changedComment};
        duplicateData[key] = value;
        setChangedComment(duplicateData);
    }
    
    return (
        <div className="all-properties">
            <Typography sx={{ml: 4, mt: 2, mb: 1, textDecoration: 'underline'}} variant='h5'>Comments</Typography>
            <TextField
                sx={{ml: 8, mt: 1}}
                size="small"
                multiline
                onChange = {event => {
                    changeDataComment('preceding_lines', event.target.value)
                }}
                defaultValue={changedComment.preceding_lines} 
                variant="outlined" />
            <Typography sx={{ml: 4, mt: 2, mb: 1, textDecoration: 'underline'}} variant='h5'>Properties</Typography>
            { Object.entries(toBeRendered).map(([property, value]) => {
                return (
                    <div key={property} className="property-component">
                        <Typography sx={{mt: 1, mr: 2, ml: 4, float: 'left'}} variant="h6">
                            {property}:
                        </Typography>
                        <TextField
                            size="small" 
                            sx={{mt: 1}}
                            onChange = {event => {
                                changeData(property, event.target.value)
                            }}
                            defaultValue={value} 
                            variant="outlined" />

                    </div>
                )
            }) }
            { Object.keys(toBeRendered).length === 0 && <Typography sx={{ml: 8, mb: 1}}  variant="h6">None</Typography> }
        </div>
    );
}
 
export default ListAllProperties;