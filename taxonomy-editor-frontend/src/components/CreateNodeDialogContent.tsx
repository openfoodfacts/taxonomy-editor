import { useState } from "react";
import ISO6391 from "iso-639-1";

import { TextField, Button, FormControl, InputLabel } from "@mui/material";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import Select from "@mui/material/Select";
import MenuItem from "@mui/material/MenuItem";
import Alert from "@mui/material/Alert";
import DialogTitle from "@mui/material/DialogTitle";

import { createBaseURL } from "@/utils";

type Props = {
  onCloseDialog: () => void;
  onSuccess: () => void;
  taxonomyName: string;
  branchName: string;
};

const CreateNodeDialogContent = ({
  onCloseDialog,
  onSuccess,
  taxonomyName,
  branchName,
}: Props) => {
  const [newLanguageCode, setNewLanguageCode] = useState("");
  const [newNodeName, setNewNodeName] = useState("");
  const [isFailedSubmit, setIsFailedSubmit] = useState(false);

  const baseUrl = createBaseURL(taxonomyName, branchName);

  const handleAddEntryNode = () => {
    setIsFailedSubmit(false);

    const data = { name: newNodeName, mainLanguageCode: newLanguageCode };

    fetch(`${baseUrl}entry`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    })
      .then(() => {
        onSuccess();
      })
      .catch(() => {
        setIsFailedSubmit(true);
      });
  };

  return (
    <>
      <DialogTitle>Create new node</DialogTitle>
      <DialogContent>
        {isFailedSubmit && (
          <Alert severity="error">
            Something went wrong. Unable to create new Node
          </Alert>
        )}

        <FormControl fullWidth sx={{ mt: 1, mb: 2 }}>
          <InputLabel id="main-language-select-label">Main Language</InputLabel>
          <Select
            label="Main Language"
            labelId="main-language-select-label"
            id="main-language-select"
            fullWidth
            value={ISO6391.getName(newLanguageCode)}
            onChange={(e) => {
              setNewLanguageCode(ISO6391.getCode(e.target.value));
            }}
          >
            {[...ISO6391.getAllNames()].sort().map((languageNameItem) => (
              <MenuItem key={languageNameItem} value={languageNameItem}>
                {languageNameItem}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        <TextField
          fullWidth
          onChange={(e) => {
            setNewNodeName(e.target.value);
          }}
          value={newNodeName}
          label="Node Name"
          size="small"
          variant="outlined"
        />
      </DialogContent>

      <DialogActions>
        <Button onClick={onCloseDialog}>Cancel</Button>
        <Button
          disabled={!newLanguageCode || !newNodeName}
          onClick={handleAddEntryNode}
        >
          Create
        </Button>
      </DialogActions>
    </>
  );
};

export default CreateNodeDialogContent;
