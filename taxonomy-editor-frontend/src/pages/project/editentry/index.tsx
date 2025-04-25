import { useState } from "react";
import { Link, useParams } from "react-router-dom";

import {
  Typography,
  Stack,
  IconButton,
  Alert,
  Button,
  Box,
} from "@mui/material";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogTitle from "@mui/material/DialogTitle";
import DeleteOutlineIcon from "@mui/icons-material/DeleteOutline";
import AccumulateAllComponents from "./AccumulateAllComponents";

import { createBaseURL, removeTxtExtension, toTitleCase } from "@/utils";
import { greyHexCode } from "@/constants";
import { useQuery } from "@tanstack/react-query";
import { DefaultService } from "@/client";

type EditEntryProps = {
  taxonomyName: string;
  branchName: string;
  id: string;
};

const EditEntry = ({ taxonomyName, branchName, id }: EditEntryProps) => {
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false);
  const [openSuccessDialog, setOpenSuccessDialog] = useState(false);

  const { data: node } = useQuery({
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
        id,
      );
    },
  });

  const isExternalNode = node?.isExternal === true;

  const baseUrl: string = createBaseURL(taxonomyName, branchName);

  const handleDeleteNode = (baseUrl: string) => {
    fetch(baseUrl + "nodes/" + id, {
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
    }).then(() => {
      setOpenDeleteDialog(false);
      setOpenSuccessDialog(true);
    });
  };

  return (
    <Box>
      {/* Renders id of current node */}
      <Box>
        <Stack direction="row" alignItems="center">
          <Typography sx={{ mb: 2, mt: 2, ml: 2 }} variant="h4">
            You are now editing &quot;{id}&quot;
          </Typography>
          {node && !isExternalNode && (
            <IconButton
              sx={{ ml: 1, color: greyHexCode }}
              onClick={() => setOpenDeleteDialog(true)}
            >
              <DeleteOutlineIcon />
            </IconButton>
          )}
        </Stack>
        {isExternalNode && (
          <Alert severity="info" sx={{ ml: 4, mb: 2, width: "fit-content" }}>
            {`This node has been imported from another taxonomy (${toTitleCase(
              removeTxtExtension(node.originalTaxonomy as string),
            )}) to extend the current taxonomy. You can only add children from the current taxonomy to it.`}
          </Alert>
        )}
      </Box>

      {/* Renders node info based on id */}
      <AccumulateAllComponents
        id={id}
        taxonomyName={taxonomyName}
        branchName={branchName}
        isReadOnly={isExternalNode}
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
          <Button component={Link} to={`/${taxonomyName}/${branchName}/entry`}>
            Continue
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export const EditEntryWrapper = () => {
  const { taxonomyName, branchName, id } = useParams();

  if (!taxonomyName || !branchName || !id)
    return (
      <Typography variant="h3">
        Oops, something went wrong! Please try again later.
      </Typography>
    );

  return (
    <EditEntry taxonomyName={taxonomyName} branchName={branchName} id={id} />
  );
};
