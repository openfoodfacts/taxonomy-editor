import { Box, Grid, Paper, Typography } from "@mui/material";
import MaterialTable, { MTableToolbar } from "@material-table/core";
import { useState } from "react";

interface RenderedProperties {
  id: string;
  propertyName: string;
  propertyValue: string;
}

const ListAllEntryProperties = ({ nodeObject, setNodeObject }) => {
  const collectProperties = () => {
    let renderedProperties: RenderedProperties[] = [];
    Object.keys(nodeObject).forEach((key) => {
      // Collecting uuids of properties
      // UUID of properties will have a "_uuid" suffix
      // Ex: prop_vegan_en_uuid

      if (
        key.startsWith("prop") &&
        key.endsWith("uuid") &&
        !key.endsWith("_comments_uuid")
      ) {
        const uuid = nodeObject[key][0]; // UUID
        // Removing "prop_" prefix from key to render only the name
        const property_name = key.split("_").slice(1, -1).join("_");

        // Properties have a prefix "prop_" followed by their name
        // Getting key for accessing property value
        const property_key = "prop_" + property_name;

        renderedProperties.push({
          id: uuid,
          propertyName: property_name,
          propertyValue: nodeObject[property_key],
        });
      }
    });
    return renderedProperties;
  };

  const [data, setData] = useState(collectProperties());

  // Helper function used for changing properties of node
  const changePropertyData = (key, value) => {
    setNodeObject((prevState) => {
      const newNodeObject = { ...prevState };
      newNodeObject["prop_" + key] = value;
      return newNodeObject;
    });
  };

  // Helper function used for deleting properties of node
  const deletePropertyData = (key) => {
    setNodeObject((prevState) => {
      const toRemove = "prop_" + key;
      const { [toRemove]: _, ...newNodeObject } = prevState;
      return newNodeObject;
    });
  };

  return (
    <Box>
      {/* Properties */}
      <Box sx={{ width: "90%", ml: 4, maxWidth: "1000px", m: "auto", mb: 3 }}>
        <MaterialTable
          data={data}
          columns={[
            { title: "Name", field: "propertyName" },
            { title: "Value", field: "propertyValue" },
          ]}
          editable={{
            onRowAdd: (newRow) =>
              new Promise((resolve, reject) => {
                // Add new property to rendered rows
                const updatedRows = [
                  ...data,
                  { ...newRow, id: Math.random().toString() },
                ];
                setData(updatedRows);

                // Add new key-value pair of a property in nodeObject
                changePropertyData(newRow.propertyName, newRow.propertyValue);
                // @ts-ignore
                resolve();
              }),
            onRowDelete: (selectedRow) =>
              new Promise((resolve, reject) => {
                // Delete property from rendered rows
                const updatedRows = [...data];
                const index = parseInt(selectedRow.id);
                updatedRows.splice(index, 1);
                setData(updatedRows);

                // Delete key-value pair of a property from nodeObject
                deletePropertyData(selectedRow.propertyName);
                // @ts-ignore
                resolve();
              }),
            onRowUpdate: (updatedRow, oldRow) =>
              new Promise((resolve, reject) => {
                // Update row in rendered rows
                const updatedRows = data.map((el) =>
                  // @ts-ignore
                  el.id === oldRow.id ? updatedRow : el
                );
                setData(updatedRows);
                // Updation takes place by deletion + addition
                // If property name has been changed, previous key should be removed from nodeObject
                // @ts-ignore
                updatedRow.propertyName !== oldRow.propertyName &&
                  // @ts-ignore
                  deletePropertyData(oldRow.propertyName);
                // Add new property to nodeObject
                changePropertyData(
                  updatedRow.propertyName,
                  updatedRow.propertyValue
                );
                // @ts-ignore
                resolve();
              }),
          }}
          options={{
            actionsColumnIndex: -1,
            addRowPosition: "last",
            tableLayout: "fixed",
            paging: false,
          }}
          components={{
            Toolbar: (props) => {
              // Used for custom title and margins
              const propsCopy = { ...props };
              propsCopy.showTitle = false;
              return (
                <Grid container direction="row">
                  <Grid item xs={6}>
                    <Typography sx={{ mt: 2, mb: 1 }} variant="h5">
                      Properties
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <MTableToolbar {...propsCopy} />
                  </Grid>
                </Grid>
              );
            },
            Container: (props) => <Paper {...props} elevation={0} />,
          }}
        />
      </Box>
    </Box>
  );
};
export default ListAllEntryProperties;
