import { Grid, Paper, TextField, Typography } from "@mui/material";
import MaterialTable, { MTableToolbar } from '@material-table/core';
import { useEffect, useState } from "react";
import { Box } from "@mui/system";
import * as uuid from "uuid";

const ListAllProperties = ({ nodeObject, setNodeObject, originalNodeObject }) => {
    const [data, setData] = useState([]);

    // Changes the properties to be rendered
    // Dependent on changes occuring in "originalNodeObject"
    useEffect(() => {
        let toBeRendered = []
        Object.keys(originalNodeObject).forEach((key) => {

            // Collecting keys of properties
            // Properties have a prefix "prop_" followed by their name
            // Ex: prop_vegan_en
            if (key.startsWith('prop')) {
            
                // Removing "prop_" prefix from key to render only the name
                    let property_name = key.split('_').slice(1).join('_');
                    toBeRendered.push({
                        'id': uuid.v4(),
                        'propertyName': property_name,
                        'propertyValue': originalNodeObject[key]
                    })
                }
        });
        setData(toBeRendered);
    }, [originalNodeObject])

    // Helper function used for changing comments from node
    function changeCommentData(value) {
        const duplicateData = {...nodeObject};
        duplicateData['preceding_lines'] = value;
        setNodeObject(duplicateData);
    }

    // Helper function used for changing properties of node
    function changePropertyData(key, value) {
        setNodeObject(prevState => {
            const duplicateData = {...prevState};
            duplicateData["prop_"+key] = value;
            return duplicateData 
        })
    }

    // Helper function used for deleting properties of node
    function deletePropertyData(key) {
        setNodeObject(prevState => {
            const toRemove = "prop_"+key;
            const {[toRemove]: _, ...duplicateData} = prevState;
            return duplicateData
        })
    }
    
    return (
        <div className="all-properties">
            {/* Comments */}
            <Typography sx={{ml: 4, mt: 2, mb: 1}} variant='h5'>Comments</Typography>
            <TextField
                sx={{ml: 8, mt: 1, width: 250}}
                minRows={4}
                multiline
                onChange = {event => {
                    changeCommentData(event.target.value.split('\n'))
                }}
                defaultValue={nodeObject.preceding_lines.join('\n')} 
                variant="outlined" />

            {/* Properties */}
            <Box sx={{width: '50%', ml: 4}}>
            <MaterialTable
                data={data}
                columns={[
                    { title: 'Name', field: 'propertyName' },
                    { title: 'Value', field: 'propertyValue' }
                ]}
                editable={{
                    onRowAdd: (newRow) => new Promise((resolve, reject) => {
                        // Add new property to rendered rows
                        const updatedRows = [...data, { id: uuid.v4(), ...newRow }]
                        setData(updatedRows);

                        // Add new key-value pair of a property in nodeObject
                        changePropertyData(newRow.propertyName, newRow.propertyValue);
                        resolve()
                    }),
                    onRowDelete: selectedRow => new Promise((resolve, reject) => {
                        // Delete property from rendered rows
                        const index = selectedRow.tableData.id;
                        const updatedRows = data.filter(obj => !(index === obj.id))
                        setData(updatedRows);

                        // Delete key-value pair of a property from nodeObject
                        deletePropertyData(selectedRow.propertyName);
                        resolve();
                    }),
                    onRowUpdate: (updatedRow, oldRow) => new Promise((resolve, reject) => {  
                        // Update row in rendered rows
                        const updatedRows = data.map(el => (el.id === oldRow.id) ? updatedRow : el);
                        setData(updatedRows);

                        // Updation takes place by deletion + addition
                        // If property name has been changed, previous key should be removed from nodeObject
                        (updatedRow.propertyName !== oldRow.propertyName) && deletePropertyData(oldRow.propertyName);
                        // Add new property to nodeObject
                        changePropertyData(updatedRow.propertyName, updatedRow.propertyValue)
                        resolve();
                    })
                }}
                options={{
                    actionsColumnIndex: -1, addRowPosition: "last"
                }}
                components={{
                    Toolbar: props => {
                        // Used for custom title and margins
                        const propsCopy = { ...props };
                        propsCopy.showTitle = false;
                        return (
                        <Grid container direction="row">
                            <Grid item xs={6}>
                            <Typography sx={{mt: 2, mb: 1}} variant='h5'>Properties</Typography>
                            </Grid>
                            <Grid item xs={6}>
                            <MTableToolbar {...propsCopy} />
                            </Grid>
                        </Grid>
                        );
                    },
                    Container: props => <Paper {...props} elevation={0}/>
                }}
            />
            </Box>
        </div>
    );
}
 
export default ListAllProperties;