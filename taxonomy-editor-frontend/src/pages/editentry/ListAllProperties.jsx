import { IconButton, TextField, Typography } from "@mui/material";
import AddBoxIcon from '@mui/icons-material/AddBox';
import MaterialTable from '@material-table/core';
import { useState } from "react";

const ListAllProperties = ({ nodeObject, setNodeObject }) => {
    let toBeRendered = []

    function guidGenerator() {
        var S4 = function() {
           return (((1+Math.random())*0x10000)|0).toString(16).substring(1);
        };
        return (S4()+S4()+"-"+S4()+"-"+S4()+"-"+S4()+"-"+S4()+S4()+S4());
    }

    Object.keys(nodeObject).forEach((key, index) => {
        if (key.startsWith('prop')) {
                let property_name = key.split('_').slice(1).join('_');
                toBeRendered.push({
                    'id': guidGenerator(),
                    'property-name': property_name,
                    'property-value': nodeObject[key]
                })
            }
    });
    
    const [data, setData] = useState(toBeRendered);

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
            <MaterialTable
                title={<Typography sx={{ml: 2, mt: 2, mb: 1}} variant='h5'>Properties</Typography>}
                data={data}
                columns={[
                    { title: 'Name', field: 'property-name' },
                    { title: 'Value', field: 'property-value' }
                ]}
                editable={{
                onRowAdd: (newRow) => new Promise((resolve, reject) => {
                    const updatedRows = [...data, { id: Math.floor(Math.random() * 100), ...newRow }]
                    setTimeout(() => {
                    setData(updatedRows)
                    resolve()
                    }, 2000)
                }),
                onRowDelete: selectedRow => new Promise((resolve, reject) => {
                    const index = selectedRow.tableData.id;
                    const updatedRows = [...data]
                    updatedRows.splice(index, 1)
                    setTimeout(() => {
                    setData(updatedRows)
                    resolve()
                    }, 2000)
                }),
                onRowUpdate:(updatedRow,oldRow)=>new Promise((resolve,reject)=>{
                    const index=oldRow.tableData.id;
                    const updatedRows=[...data]
                    updatedRows[index]=updatedRow
                    setTimeout(() => {
                    setData(updatedRows)
                    resolve()
                    }, 2000)
                })

                }}
                options={{
                actionsColumnIndex: -1, addRowPosition: "first"
                }}
            />
            {/* <div style={{ height: 400, width: '50%' }}>
                <DataGrid
                    sx={{ml: 4}}
                    rows={rows}
                    columns={[
                        { field: 'property-name', headerName: 'Name', width: 350, editable: true },
                        { field: 'property-value', headerName: 'Value', editable: true }
                    ]}
                    experimentalFeatures={{ newEditingApi: true }}
                />
            </div> */}
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