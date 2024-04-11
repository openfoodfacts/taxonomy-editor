import { Alert, Box, Snackbar, Typography, Button } from "@mui/material";
import SaveIcon from "@mui/icons-material/Save";
import CircularProgress from "@mui/material/CircularProgress";
import { useState } from "react";
import ListEntryParents from "./ListEntryParents";
import ListEntryChildren from "./ListEntryChildren";
import { ListTranslations } from "./ListTranslations";
import ListAllEntryProperties from "./ListAllEntryProperties";
import ListAllNonEntryInfo from "./ListAllNonEntryInfo";
import equal from "fast-deep-equal";
import { createURL, getNodeType, toSnakeCase } from "@/utils";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { DefaultService } from "@/client";

interface AccumulateAllComponentsProps {
  id: string;
  taxonomyName: string;
  branchName: string;
  isReadOnly: boolean;
}

/**
 * Component used for rendering node information
 * If node is an "entry": Relations, translations, comments and properties are rendered
 * If node is an "stopword/synonym": Stopwords/synonyms, language and comments are rendered
 * If node is "header/footer": Comments are rendered
 */
const AccumulateAllComponents = ({
  id,
  taxonomyName,
  branchName,
  isReadOnly,
}: AccumulateAllComponentsProps) => {
  // Finding URL to send requests
  const url = createURL(taxonomyName, branchName, id);
  const urlPrefix = `/${taxonomyName}/${branchName}`;
  const isEntry = getNodeType(id) === "entry";

  const {
    data: node,
    isPending,
    isError,
    error,
    refetch,
  } = useQuery({
    queryKey: [
      "findOneEntryTaxonomyNameBranchEntryEntryGet",
      taxonomyName,
      branchName,
      id,
    ],
    queryFn: async () => {
      return await DefaultService.findOneEntryTaxonomyNameBranchEntryEntryGet(
        branchName,
        taxonomyName,
        id
      );
    },
  });
  const [nodeObject, setNodeObject] = useState(null); // Storing updates to node
  const [originalNodeObject, setOriginalNodeObject] = useState(null); // For tracking changes
  const [updateChildren, setUpdateChildren] = useState(null); // Storing updates of children in node
  const [previousUpdateChildren, setPreviousUpdateChildren] = useState(null); // Tracking changes of children
  const [open, setOpen] = useState(false); // Used for Dialog component
  const [isSaveError, setIsSaveError] = useState(false); // Used for displaying error message if save failed
  const [saveErrorMessage, setSaveErrorMessage] = useState(""); // Error message if save failed
  const navigate = useNavigate();

  if (previousUpdateChildren === null && updateChildren !== null) {
    setPreviousUpdateChildren(updateChildren);
  }

  const hasChanges = !nodeObject
    ? false
    : !equal(nodeObject, originalNodeObject) ||
      !equal(updateChildren, previousUpdateChildren);

  if (
    (!nodeObject && node) ||
    (originalNodeObject && !equal(node, originalNodeObject))
  ) {
    setNodeObject(node);
    setOriginalNodeObject(node);
  }

  // Displaying error messages if any
  if (isError) {
    return (
      <Typography sx={{ ml: 4 }} variant="h5">
        {error.message}
      </Typography>
    );
  }

  // Loading...
  if (isPending && !node) {
    return (
      <Box
        style={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          height: "100vh",
        }}
      >
        <CircularProgress sx={{ textAlign: "center" }} />
      </Box>
    );
  }

  // Helper functions for Dialog component
  const handleClose = () => {
    setOpen(false);
    setIsSaveError(false);
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
    let newId = id;
    fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(dataToBeSent),
    })
      .then(async (res) => {
        if (!res.ok) {
          const errorMessage = await res.text();
          throw Error(JSON.parse(errorMessage).detail);
        }
        if (isEntry) {
          newId = (await res.json()).id;
          const newUrl = createURL(taxonomyName, branchName, newId);
          return fetch(newUrl + "/children", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(updateChildren),
          });
        }
        return res;
      })
      .then(() => {
        setOpen(true);
        setPreviousUpdateChildren(updateChildren);
        if (newId !== id) {
          navigate(
            `/${toSnakeCase(taxonomyName)}/${branchName}/entry/${newId}`
          );
        } else {
          refetch();
        }
      })
      .catch((error) => {
        setIsSaveError(true);
        setSaveErrorMessage(error.message);
      });
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
                updateChildren={updateChildren}
                setUpdateNodeChildren={setUpdateChildren}
                previousUpdateChildren={previousUpdateChildren}
                setPreviousUpdateChildren={setPreviousUpdateChildren}
                hasChanges={hasChanges}
              />
              <ListTranslations
                originalNodeObject={originalNodeObject}
                nodeObject={nodeObject}
                setNodeObject={setNodeObject}
                isReadOnly={isReadOnly}
              />
              <ListAllEntryProperties
                nodeObject={nodeObject}
                setNodeObject={setNodeObject}
                isReadOnly={isReadOnly}
              />
              {/* Sticky button for submitting edits */}
              {hasChanges && (
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
                      minHeight: "3rem",
                      borderRadius: "2rem",
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
      <Snackbar
        anchorOrigin={{ vertical: "top", horizontal: "right" }}
        open={isSaveError}
        autoHideDuration={3000}
        onClose={handleClose}
      >
        <Alert
          elevation={6}
          variant="filled"
          onClose={handleClose}
          severity="error"
        >
          {saveErrorMessage}
        </Alert>
      </Snackbar>
    </Box>
  );
};
export default AccumulateAllComponents;
