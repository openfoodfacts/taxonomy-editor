import { TextField, Typography } from "@mui/material";

const ListAllProperties = ({ nodeObject, setNodeObject }) => {
    let toBeRendered = {}
    Object.keys(nodeObject).forEach((key) => {
        if (key.startsWith('prop')) {
                // Example key: prop_vegan_en, Property name: vegan_en
                let property_name = key.split('_').slice(1).join('_'); // Slicing property name from key
                toBeRendered[property_name] = nodeObject[key]
            }
    });

    // Helper function used for changing state of properties
    function changeData(key, value) {
        const duplicateData = {...nodeObject};
        duplicateData[key] = value;
        setNodeObject(duplicateData);
    }
    
    return (
        <div className="all-properties">
            <Typography sx={{ml: 4, mt: 2, mb: 1}} variant='h5'>Comments</Typography>
            <TextField
                sx={{ml: 8, mt: 1, width: 250}}
                minRows={4}
                multiline
                onChange = {event => {
                    changeData('preceding_lines', event.target.value.split('\n'))
                }}
                defaultValue={nodeObject.preceding_lines.join('\n')} 
                variant="outlined" />
            <Typography sx={{ml: 4, mt: 2, mb: 1}} variant='h5'>Properties</Typography>
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
                                changeData("prop_"+property, event.target.value)
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