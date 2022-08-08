import { Grid, Paper, TextField, Typography } from "@mui/material";
import MaterialTable, { MTableToolbar } from '@material-table/core';
import { useState } from "react";
import { Box } from "@mui/system";
import { useEffect } from "react";

const ListAllProperties = ({ nodeObject, setNodeObject }) => {
    let toBeRendered = []
  
    function guidGenerator() {
        var S4 = function() {
           return (((1+Math.random())*0x10000)|0).toString(16).substring(1);
        };
        return (S4()+S4()+"-"+S4()+"-"+S4()+"-"+S4()+"-"+S4()+S4()+S4());
    }

    Object.keys(nodeObject).forEach((key) => {
        if (key.startsWith('prop')) {
                let property_name = key.split('_').slice(1).join('_');
                toBeRendered.push({
                    'id': guidGenerator(),
                    'propertyName': property_name,
                    'propertyValue': nodeObject[key]
                })
            }
    });
    
    const [data, setData] = useState(toBeRendered);

    // Helper function used for updating state
    function changeData(key, value) {
        const duplicateData = {...nodeObject};
        duplicateData[key] = value;
        setNodeObject(duplicateData);
    }

    // Helper function used for deleting from state
    function deleteData(key) {
        const duplicateData = {...nodeObject};
        delete duplicateData[key];
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
            <Box sx={{width: '50%', ml: 4}}>
            <MaterialTable
                data={data}
                columns={[
                    { title: 'Name', field: 'propertyName' },
                    { title: 'Value', field: 'propertyValue' }
                ]}
                editable={{
                    onRowAdd: (newRow) => new Promise((resolve, reject) => {
                        const updatedRows = [...data, { id: guidGenerator(), ...newRow }]
                        setTimeout(() => {
                            setData(updatedRows)
                            resolve()
                        }, 2000)
                    }),
                    onRowDelete: selectedRow => new Promise((resolve, reject) => {
                        const index = selectedRow.tableData.id;
                        const updatedRows = data.filter(obj => !(index === obj.id))
                        setTimeout(() => {
                            setData(updatedRows)
                            resolve()
                        }, 2000)
                    }),
                    onRowUpdate: (updatedRow, oldRow) => new Promise((resolve, reject) => {
                        const updatedRows=[...data];
                        if (updatedRow.propertyName === oldRow.propertyName) {
                            for (let i=0; i<updatedRows.length; i++) {
                                if (updatedRows[i].id === oldRow.id) {
                                    updatedRows[i].propertyValue = updatedRow.propertyValue;
                                    break;
                                }
                            }
                        }
                        setTimeout(() => {
                            setData(updatedRows);
                            resolve()
                        }, 2000)
                    })
                }}
                options={{
                    actionsColumnIndex: -1, addRowPosition: "last"
                }}
                components={{
                    Toolbar: props => {
                      // Make a copy of props so we can hide the default title
                      const propsCopy = { ...props };
                      // Hide default title
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
            { Object.keys(toBeRendered).length === 0 && <Typography sx={{ml: 8, mb: 1}}  variant="h6">None</Typography> }
        </div>
    );
}
 
export default ListAllProperties;