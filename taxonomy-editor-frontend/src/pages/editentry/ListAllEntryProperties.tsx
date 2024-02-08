import { Alert, Box, Grid, Paper, Snackbar, Typography } from "@mui/material";
import MaterialTable, { MTableToolbar } from "@material-table/core";
import { useState } from "react";
import ISO6391, { LanguageCode } from "iso-639-1";

type RowType = {
  propertyName: string;
  propertyValue: string;
};

type RenderedPropertyType = RowType & {
  id: string;
};

const ListAllEntryProperties = ({ nodeObject, setNodeObject }) => {
  function replaceAll(str: string, find: string, replace: string) {
    return str.replace(new RegExp(find, "g"), replace);
  }

  const normalizeNameToFrontend = (name: string) => {
    // Use the replace() method with a regular expression to replace underscores with colons
    return replaceAll(name, "_", ":");
  };

  const normalizeNameToDb = (name: string) => {
    // Use the replace() method with a regular expression to replace underscores with colons
    return replaceAll(name, ":", "_");
  };

  const collectProperties = (): RenderedPropertyType[] => {
    let renderedProperties: RenderedPropertyType[] = [];
    Object.keys(nodeObject).forEach((key: string) => {
      // Collecting properties (begin with prop_)
      // Ex: prop_vegan_en
      if (key.startsWith("prop") && !key.endsWith("_comments")) {
        // Removing "prop_" prefix from key to render only the name
        const property_name = key.replace(/^prop_/, "");

        renderedProperties.push({
          id: Math.random().toString(),
          propertyName: normalizeNameToFrontend(property_name),
          propertyValue: nodeObject[key],
        });
      }
    });
    return renderedProperties;
  };

  const [data, setData] = useState(collectProperties());

  // Helper function used for changing properties of node
  const changePropertyData = (key: string, value: string) => {
    setNodeObject((prevState) => {
      const newNodeObject = { ...prevState };
      newNodeObject["prop_" + key] = value;
      return newNodeObject;
    });
  };

  // Helper function used for deleting properties of node
  const deletePropertyData = (key: string) => {
    setNodeObject((prevState) => {
      const toRemove = normalizeNameToDb("prop_" + key);
      const { [toRemove]: _, ...newNodeObject } = prevState;
      return newNodeObject;
    });
  };

  const LanguageCodes = ISO6391.getAllCodes();

  const validatePropertyName = (propertyName: string): boolean => {
    // Every property name should be in the form property_name:lang_code
    if (propertyName) {
      const words = propertyName.split(":");
      const langCode = words[words.length - 1];
      if (!LanguageCodes.includes(langCode as LanguageCode)) {
        return false;
      }
      // Property name should not include special caracters
      for (const word of words) {
        const pattern = /^[a-zA-Z0-9_]+$/;
        if (!pattern.test(word)) {
          return false;
        }
      }
      return true;
    }
    return false;
  };

  const isPropertyNameUnique = (
    propertyName: string,
    otherProperties: RenderedPropertyType[]
  ): boolean => {
    for (const prop of otherProperties) {
      if (prop.propertyName === propertyName) return false;
    }
    return true;
  };

  const [errorMessage, setErrorMessage] = useState("");
  const handleCloseErrorSnackbar = () => {
    setErrorMessage("");
  };

  return (
    <Box>
      {/* Properties */}
      <Box sx={{ width: "90%", ml: 4, maxWidth: "1000px", m: "auto", mb: 3 }}>
        <MaterialTable
          data={data}
          columns={[
            {
              title: "Name",
              field: "propertyName",
              validate: (rowData) =>
                validatePropertyName(rowData.propertyName)
                  ? true
                  : {
                      isValid: false,
                      helperText:
                        "Property name should not contain special caracters and should follow the format : property_name:lang_code",
                    },
            },
            { title: "Value", field: "propertyValue" },
          ]}
          editable={{
            onRowAdd: (newRow: RowType) =>
              new Promise<void>((resolve, reject) => {
                if (!isPropertyNameUnique(newRow.propertyName, data)) {
                  setErrorMessage(`${newRow.propertyName} already exists`);
                  reject();
                } else {
                  // Add new property to rendered rows
                  const updatedRows = [
                    ...data,
                    { id: Math.random().toString(), ...newRow },
                  ];
                  setData(updatedRows);

                  // Add new key-value pair of a property in nodeObject
                  changePropertyData(
                    normalizeNameToDb(newRow.propertyName),
                    newRow.propertyValue
                  );
                  resolve();
                }
              }),
            onRowDelete: (selectedRow: RenderedPropertyType) =>
              new Promise<void>((resolve, reject) => {
                // Delete property from rendered rows
                const updatedRows = [...data];
                const index = updatedRows.findIndex(
                  (row) => row.id === selectedRow.id
                );
                updatedRows.splice(index, 1);
                setData(updatedRows);
                // Delete key-value pair of a property from nodeObject
                deletePropertyData(selectedRow.propertyName);
                resolve();
              }),
            onRowUpdate: (
              updatedRow: RenderedPropertyType,
              oldRow: RenderedPropertyType
            ) =>
              new Promise<void>((resolve, reject) => {
                const index = data.findIndex((row) => row.id === updatedRow.id);
                const otherProperties = [...data];
                otherProperties.splice(index, 1);
                if (
                  !isPropertyNameUnique(
                    updatedRow.propertyName,
                    otherProperties
                  )
                ) {
                  setErrorMessage(`${updatedRow.propertyName} already exists`);
                  reject();
                } else {
                  // Update row in rendered rows
                  const updatedRows = data.map((el) =>
                    el.id === oldRow.id ? updatedRow : el
                  );
                  setData(updatedRows);
                  // Updation takes place by deletion + addition
                  // If property name has been changed, previous key should be removed from nodeObject
                  updatedRow.propertyName !== oldRow.propertyName &&
                    deletePropertyData(oldRow.propertyName);
                  // Add new property to nodeObject
                  changePropertyData(
                    normalizeNameToDb(updatedRow.propertyName),
                    updatedRow.propertyValue
                  );
                  resolve();
                }
              }),
          }}
          options={{
            actionsColumnIndex: -1,
            addRowPosition: "last",
            tableLayout: "fixed",
            paging: false,
            showTitle: false,
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
      <Snackbar
        anchorOrigin={{ vertical: "top", horizontal: "right" }}
        open={!!errorMessage}
        autoHideDuration={3000}
        onClose={handleCloseErrorSnackbar}
      >
        <Alert
          elevation={6}
          variant="filled"
          onClose={handleCloseErrorSnackbar}
          severity="error"
        >
          {errorMessage}
        </Alert>
      </Snackbar>
    </Box>
  );
};
export default ListAllEntryProperties;
