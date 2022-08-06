import { IconButton, TextField, Typography } from "@mui/material";
import AddBoxIcon from '@mui/icons-material/AddBox';
import { DataGrid } from '@mui/x-data-grid';

const ListAllProperties = ({ nodeObject, setNodeObject }) => {
    let toBeRendered = []
    Object.keys(nodeObject).forEach((key, index) => {
        if (key.startsWith('prop')) {
                let property_name = key.split('_').slice(1).join('_');
                toBeRendered.push({
                    'id': index+1,
                    'property-name': property_name,
                    'property-value': nodeObject[key]
                })
            }
    });

    // Helper function used for changing state of properties
    function changeData(key, value) {
        const duplicateData = {...nodeObject};
        duplicateData[key] = value;
        setNodeObject(duplicateData);
    }

    const handleAdd = () => {
        console.log('I added!');
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
            <Typography sx={{ml: 4, mt: 2, mb: 1}} variant='h5'>
                Properties
                <IconButton color="inherit" onClick={handleAdd}>
                    <AddBoxIcon style={{marginLeft: 6, position: 'relative'}} />
                </IconButton>
            </Typography>
            <div style={{ height: 400, width: '50%' }}>
                <DataGrid
                    sx={{ml: 4}}
                    rows={toBeRendered}
                    columns={[
                        { field: 'property-name', headerName: 'Name', width: 350, editable: true },
                        { field: 'property-value', headerName: 'Value', editable: true }
                    ]}
                    experimentalFeatures={{ newEditingApi: true }}
                />
            </div>
            {/* { Object.entries(toBeRendered).map(([property, value]) => {
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
            }) } */}
            { Object.keys(toBeRendered).length === 0 && <Typography sx={{ml: 8, mb: 1}}  variant="h6">None</Typography> }
        </div>
    );
}
 
export default ListAllProperties;