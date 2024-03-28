import useFetch from "@/components/useFetch";
import {
  Typography,
  TextField,
  Stack,
  Button,
  IconButton,
  Box,
  Alert,
} from "@mui/material";
import { Link } from "react-router-dom";
import { useEffect, useState } from "react";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogTitle from "@mui/material/DialogTitle";
import AddBoxIcon from "@mui/icons-material/AddBox";
import DeleteOutlineIcon from "@mui/icons-material/DeleteOutline";
import CircularProgress from "@mui/material/CircularProgress";
import ISO6391 from "iso-639-1";
import { ENTER_KEYCODE } from "@/constants";
import { greyHexCode } from "@/constants";

interface Relations {
  index: string;
  child: string;
}

const ListEntryChildren = ({
  url,
  urlPrefix,
  setUpdateNodeChildren,
  hasChanges,
}) => {
  const [relations, setRelations] = useState<Relations[]>([]);
  const [newChild, setNewChild] = useState("");
  const [newLanguageCode, setNewLanguageCode] = useState("");
  const [openDialog, setOpenDialog] = useState(false); // Used for Dialog component
  const isValidLanguageCode = ISO6391.validate(newLanguageCode); // Used for validating a new LC

  /* eslint no-unused-vars: ["error", { varsIgnorePattern: "^__" }] */
  const {
    data: incomingData,
    isPending,
    isError,
    errorMessage,
  } = useFetch(url);

  useEffect(() => {
    if (incomingData) {
      // eslint-disable-next-line @typescript-eslint/ban-ts-comment
      // @ts-expect-error
      setUpdateNodeChildren(incomingData.map((el) => el?.[0]));
      const arrayData: Relations[] = [];
      // eslint-disable-next-line @typescript-eslint/ban-ts-comment
      // @ts-expect-error
      incomingData.map((el) =>
        arrayData.push({ index: Math.random().toString(), child: el?.[0] })
      );
      setRelations(arrayData);
    }
  }, [incomingData, setUpdateNodeChildren]);

  // Helper functions for Dialog component
  const handleCloseDialog = () => {
    setOpenDialog(false);
  };
  const handleOpenDialog = () => {
    setOpenDialog(true);
  };

  const handleAddChild = () => {
    const newChildID = newLanguageCode + ":" + newChild; // Reconstructing node ID
    setRelations([
      ...relations,
      { index: Math.random().toString(), child: newChildID },
    ]);
    setUpdateNodeChildren((prevState) => {
      const duplicateData = [...prevState];
      duplicateData.push(newChildID);
      return duplicateData;
    });
    setOpenDialog(false);
  };

  const handleDeleteChild = (index) => {
    const newRelations = relations.filter((obj) => !(index === obj.index));
    setRelations(newRelations);
    // Updated tags assigned for later use
    const tagsToBeInserted = newRelations.map((el) => el.child);
    setUpdateNodeChildren(tagsToBeInserted);
  };

  // Check error in fetch
  if (isError) {
    return (
      <Typography sx={{ ml: 4 }} variant="h5">
        {errorMessage}
      </Typography>
    );
  }

  if (isPending && !incomingData) {
    return (
      <Box sx={{ textAlign: "center", my: 5 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Stack direction="row" alignItems="center">
        <Typography sx={{ ml: 4 }} variant="h5">
          {!relations.length ? "No children" : "Children"}
        </Typography>
        {!incomingData && (
          <Box sx={{ textAlign: "left", m: 3 }}>
            <CircularProgress size={20} />
          </Box>
        )}
        <IconButton
          sx={{ ml: 1, color: greyHexCode }}
          onClick={handleOpenDialog}
        >
          <AddBoxIcon />
        </IconButton>
      </Stack>

      {/* Renders warning message to save changes to be able to click on a child node */}
      {hasChanges && (
        <Alert severity="warning" sx={{ mb: 1, ml: 4, width: "fit-content" }}>
          Changes are pending and have not been saved. Please save your changes
          before navigating to a child node.
        </Alert>
      )}

      {/* Renders parents or children of the node */}
      <Stack direction="row" flexWrap="wrap">
        {relations.map((relationObject) => (
          <Stack
            key={relationObject["index"]}
            direction="row"
            alignItems="center"
          >
            <Link
              to={
                hasChanges
                  ? "#"
                  : `${urlPrefix}/entry/${relationObject["child"]}`
              }
              style={{ color: "#0064c8", display: "inline-block" }}
            >
              <Typography sx={{ ml: 8 }} variant="h6">
                {relationObject["child"]}
              </Typography>
            </Link>
            <IconButton
              sx={{ ml: 1, color: greyHexCode }}
              onClick={() => handleDeleteChild(relationObject["index"])}
            >
              <DeleteOutlineIcon />
            </IconButton>
          </Stack>
        ))}
      </Stack>

      {/* Dialog box for adding translations */}
      <Dialog open={openDialog} onClose={handleCloseDialog}>
        <DialogTitle>Add a child</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Enter the name of the child in the format
            &quot;LC:child_tag_id&quot;
          </DialogContentText>
          <DialogContentText>Example - en:yogurts</DialogContentText>
          <Stack sx={{ mt: 2 }} direction="row" alignItems="center">
            <TextField
              onKeyPress={(e) => {
                e.keyCode === ENTER_KEYCODE && handleAddChild();
              }}
              onChange={(e) => {
                setNewLanguageCode(e.target.value);
              }}
              label="Language Code"
              error={!isValidLanguageCode}
              sx={{ width: 250, marginRight: 1 }}
              size="small"
              variant="outlined"
            />
            <Typography component="h4">:</Typography>
            <TextField
              margin="dense"
              onKeyPress={(e) => {
                e.keyCode === ENTER_KEYCODE && handleAddChild();
              }}
              onChange={(e) => {
                setNewChild(e.target.value);
              }}
              label="Child"
              sx={{ marginLeft: 1 }}
              size="small"
              fullWidth
              variant="outlined"
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button disabled={!isValidLanguageCode} onClick={handleAddChild}>
            Add
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ListEntryChildren;
