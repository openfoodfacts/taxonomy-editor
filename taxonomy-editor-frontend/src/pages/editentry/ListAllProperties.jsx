import { Paper, Stack, TextField, Typography } from "@mui/material";
import { useState } from "react";

const ListAllProperties = ({ nodeObject }) => {
    let toBeRendered = {}
    Object.keys(nodeObject).forEach((key) => {
        if (key.startsWith('prop')) {
                let property_name = key.split('_').slice(1).join('_');
                // console.log(property_name);
                toBeRendered[property_name] = nodeObject[key]
            }
    });

    const [changedObj, setChangedObj] = useState(toBeRendered);

    // Helper function used for changing state
    function changeData(key, obj) {
        const duplicateData = {...changedObj};
        duplicateData[key] = obj;
        setChangedObj(duplicateData);
    }

    return (
        <div className="allProperties">
            <Typography sx={{ml: 4, mt: 2, mb: 1, textDecoration: 'underline'}} variant='h5' component={'div'}>Properties</Typography>
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