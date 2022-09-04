import { Typography, TextField, Box } from "@mui/material";

/**
 * Sub-component used for rendering comments and properties of a node with ID = "entry" 
*/ 
const ListAllEntryProperties = ({ nodeObject, setNodeObject }) => {
    let renderedProperties = {}
    Object.keys(nodeObject).forEach((key) => {

        // Collecting keys of properties
        // Properties have a prefix "prop_" followed by their name
        // Ex: prop_vegan_en

        if (key.startsWith('prop')) {
                renderedProperties[key] = nodeObject[key]
            }
    });

    // Helper function used for changing state of properties
    function changeData(key, value) {
        const duplicateData = {...nodeObject};
        duplicateData[key] = value;
        setNodeObject(duplicateData);
    }
    
    return (
        <Box>
            {/* Comments */}
            <Typography sx={{ml: 4, mt: 2, mb: 1}} variant='h5'>Comments</Typography>
            <TextField
                sx={{ml: 8, mt: 1, width: 250}}
                minRows={4}
                multiline
                onChange = {event => {
                    changeData('preceding_lines', event.target.value.split('\n'))
                }}
                value={nodeObject.preceding_lines.join('\n')} 
                variant="outlined" />

            {/* Properties */}
            <Typography sx={{ml: 4, mt: 2, mb: 1}} variant='h5'>Properties</Typography>
            { Object.keys(renderedProperties).length === 0 ? 
                <Typography sx={{ml: 8, mb: 1}} variant="h6">None</Typography> :
                Object.entries(renderedProperties).map(([property, value]) => {
                    // Removing "prop_" prefix from key to render only the name
                    const property_name = property.split('_').slice(1).join('_');
                    return (
                        <Box key={property_name}>
                            <Typography sx={{mt: 1, mr: 2, ml: 4, float: 'left'}} variant="h6">
                                {property_name}:
                            </Typography>
                            <TextField
                                size="small" 
                                sx={{mt: 1}}
                                onChange = {event => {
                                    changeData(property, event.target.value)
                                }}
                                value={value} 
                                variant="outlined" />
                        </Box>
                    )
                })
            }
        </Box>
    );
}
 
export default ListAllEntryProperties;