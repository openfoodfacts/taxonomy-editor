import { useState, useEffect } from "react";
import { Link, useParams } from "react-router-dom";

import { Typography, Stack, IconButton, Button, Box } from "@mui/material";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogTitle from "@mui/material/DialogTitle";
import DeleteOutlineIcon from "@mui/icons-material/DeleteOutline";
import AccumulateAllComponents from "./AccumulateAllComponents";

import { createBaseURL } from "@/utils";
import { greyHexCode } from "@/constants";
import WarningParsingErrors from "@/components/WarningParsingErrors";

type EditEntryProps = {
  addNavLinks: ({
    branchName,
    taxonomyName,
  }: {
    branchName: string;
    taxonomyName: string;
  }) => void;
  taxonomyName: string;
  branchName: string;
  id: string;
};

const EditEntry = ({
  addNavLinks,
  taxonomyName,
  branchName,
  id,
}: EditEntryProps) => {
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false);
  const [openSuccessDialog, setOpenSuccessDialog] = useState(false);

  const baseUrl: string = createBaseURL(taxonomyName, branchName);

  useEffect(
    function defineMainNavLinks() {
      addNavLinks({ branchName, taxonomyName });
    },
    [taxonomyName, branchName, addNavLinks]
  );

  const handleDeleteNode = (baseUrl: string) => {
    const data = { id: id };
    fetch(baseUrl + "nodes", {
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    }).then(() => {
      setOpenDeleteDialog(false);
      setOpenSuccessDialog(true);
    });
  };

  return (
    <>
      <WarningParsingErrors baseUrl={baseUrl} />
      <Box>
        {/* Renders id of current node */}
        <Box>
          <Stack direction="row" alignItems="center">
            <Typography sx={{ mb: 2, mt: 2, ml: 2 }} variant="h4">
              You are now editing &quot;{id}&quot;
            </Typography>
            <IconButton
              sx={{ ml: 1, color: greyHexCode }}
              onClick={() => setOpenDeleteDialog(true)}
            >
              <DeleteOutlineIcon />
            </IconButton>
          </Stack>
        </Box>

        {/* Renders node info based on id */}
        <AccumulateAllComponents
          id={id}
          taxonomyName={taxonomyName}
          branchName={branchName}
        />

        {/* Dialog box for confirmation of deletion of node */}
        <Dialog open={openDeleteDialog}>
          <DialogTitle>Delete a node</DialogTitle>
          <DialogContent>
            <DialogContentText>
              Are you sure you want to delete this node?
            </DialogContentText>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setOpenDeleteDialog(false)}>Cancel</Button>
            <Button
              color="warning"
              onClick={() => handleDeleteNode(baseUrl)}
              autoFocus
            >
              Delete
            </Button>
          </DialogActions>
        </Dialog>

        {/* Dialog box for acknowledgement of deletion of node */}
        <Dialog
          open={openSuccessDialog}
          aria-labelledby="alert-dialog-title"
          aria-describedby="alert-dialog-description"
        >
          <DialogTitle id="alert-dialog-title">
            Your edits have been saved!
          </DialogTitle>
          <DialogContent>
            <DialogContentText id="alert-dialog-description">
              The node {id} has been successfully deleted.
            </DialogContentText>
          </DialogContent>
          <DialogActions>
            <Button
              component={Link}
              to={`/${taxonomyName}/${branchName}/entry`}
            >
              Continue
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </>
  );
};

type EditEntryWrapperProps = {
  addNavLinks: ({
    branchName,
    taxonomyName,
  }: {
    branchName: string;
    taxonomyName: string;
  }) => void;
};

const EditEntryWrapper = ({ addNavLinks }: EditEntryWrapperProps) => {
  const { taxonomyName, branchName, id } = useParams();

  if (!taxonomyName || !branchName || !id)
    return (
      <Typography variant="h3">
        Oops, something went wrong! Please try again later.
      </Typography>
    );

  return (
    <EditEntry
      addNavLinks={addNavLinks}
      taxonomyName={taxonomyName}
      branchName={branchName}
      id={id}
    />
  );
};

export default EditEntryWrapper;
