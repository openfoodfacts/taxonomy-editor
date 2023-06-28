import { Alert, Box, Snackbar, Typography, Button } from "@mui/material";
import SaveIcon from "@mui/icons-material/Save";
import { useEffect, useState } from "react";
import useFetch from "../../components/useFetch";
import ListEntryParents from "./ListEntryParents";
import ListEntryChildren from "./ListEntryChildren";
import ListTranslations from "./ListTranslations";
import ListAllEntryProperties from "./ListAllEntryProperties";
import ListAllNonEntryInfo from "./ListAllNonEntryInfo";
import equal from "fast-deep-equal";
import { createURL, getNodeType } from "../../utils";

/**
 * Component used for rendering node information
 * If node is an "entry": Relations, translations, comments and properties are rendered
 * If node is an "stopword/synonym": Stopwords/synonyms, language and comments are rendered
 * If node is "header/footer": Comments are rendered
 */
const AccumulateAllComponents = ({ id, taxonomyName, branchName }) => {
  // Finding URL to send requests
  const url = createURL(taxonomyName, branchName, id);
  const urlPrefix = `/${taxonomyName}/${branchName}`;
  const isEntry = getNodeType(id) === "entry";

  /* eslint no-unused-vars: ["error", { varsIgnorePattern: "^__" }] */
  const {
    data: node,
    isPending,
    isError,
    __isSuccess,
    errorMessage,
  } = useFetch(url);
  const [nodeObject, setNodeObject] = useState(null); // Storing updates to node
  const [originalNodeObject, setOriginalNodeObject] = useState(null); // For tracking changes
  const [updateChildren, setUpdateChildren] = useState([]); // Storing updates of children in node
  const [open, setOpen] = useState(false); // Used for Dialog component
  const [changesMade, setChangesMade] = useState(false); // Used for displaying Fab

  // Tracking changes
  useEffect(() => {
    if (nodeObject && originalNodeObject) {
      const changesMade =
        !equal(nodeObject, originalNodeObject) || updateChildren.length !== 0;
      setChangesMade(changesMade);
    }
  }, [nodeObject, originalNodeObject, updateChildren]);

  // Setting state of node after fetch
  useEffect(() => {
    let duplicateNode = null;
    if (node) {
      duplicateNode = { ...node[0] };
      // Adding UUIDs for tags and properties
      Object.keys(node[0]).forEach((key) => {
        if (key.startsWith("tags") && !key.includes("ids")) {
          duplicateNode[key + "_uuid"] = [];
          duplicateNode[key].forEach(() => {
            duplicateNode[key + "_uuid"].push(Math.random().toString());
          });
        } else if (key.startsWith("prop")) {
          duplicateNode[key + "_uuid"] = [Math.random().toString()];
        }
      });
    }
    setNodeObject(duplicateNode);
    setOriginalNodeObject(JSON.parse(JSON.stringify(duplicateNode))); // Deep copy
  }, [node]);

  // Displaying error messages if any
  if (isError) {
    return (
      <Typography sx={{ ml: 4 }} variant="h5">
        {errorMessage}
      </Typography>
    );
  }

  // Loading...
  if (isPending) {
    return (
      <Typography sx={{ ml: 4 }} variant="h5">
        Loading..
      </Typography>
    );
  }

  // Helper functions for Dialog component
  const handleClose = () => {
    setOpen(false);
  };

  // Function handling updation of node
  const handleSubmit = () => {
    if (!nodeObject) return;
    const data = Object.assign({}, nodeObject);
    delete data["id"]; // ID not allowed in POST

    const dataToBeSent = {};
    // Remove UUIDs from data
    Object.keys(data).forEach((key) => {
      if (!key.endsWith("uuid")) {
        dataToBeSent[key] = data[key];
      }
    });
    const allUrlsAndData = [[url, dataToBeSent]];
    if (isEntry) {
      allUrlsAndData.push([url + "/children", updateChildren]);
    }
    Promise.all(
      allUrlsAndData.map(([url, dataToBeSent]) => {
        return fetch(url, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(dataToBeSent),
        });
      })
    )
      .then(() => {
        setOpen(true);
        setChangesMade(false);
      })
      .catch(() => {});
  };
  return (
    <Box>
      {/* Based on isEntry, respective components are rendered */}
      {isEntry ? (
        <Box>
          {!!nodeObject && (
            <>
              <ListEntryParents
                fetchUrl={url + "/parents"}
                linkHrefPrefix={urlPrefix}
              />
              <ListEntryChildren
                url={url + "/children"}
                urlPrefix={urlPrefix}
                setUpdateNodeChildren={setUpdateChildren}
              />
              <ListTranslations
                nodeObject={nodeObject}
                setNodeObject={setNodeObject}
              />
              {/* Fab for submitting edits */}
              <ListAllEntryProperties
                nodeObject={nodeObject}
                setNodeObject={setNodeObject}
              />
              {changesMade && (
                <div
                  style={{
                    backgroundColor: "white",
                    position: "sticky",
                    bottom: 0,
                    zIndex: 1,
                  }}
                >
                  <Button
                    onClick={handleSubmit}
                    variant="contained"
                    sx={{
                      minHeight : "50px",
                      borderRadius : "20px",
                      marginTop: 2,
                      marginBottom: 2,
                      marginLeft: 4,
                    }}
                  >
                    <SaveIcon sx={{ mr: 1 }} />
                    Save Changes
                  </Button>
                </div>
              )}
            </>
          )}
        </Box>
      ) : (
        <>
          <ListAllNonEntryInfo
            nodeObject={nodeObject}
            id={id}
            setNodeObject={setNodeObject}
          />
        </>
      )}
      {/* Snackbar for acknowledgment of update */}
      <Snackbar
        anchorOrigin={{ vertical: "top", horizontal: "right" }}
        open={open}
        autoHideDuration={3000}
        onClose={handleClose}
      >
        <Alert
          elevation={6}
          variant="filled"
          onClose={handleClose}
          severity="success"
        >
          The node has been successfully updated!
        </Alert>
      </Snackbar>
    </Box>
  );
};
export default AccumulateAllComponents;
