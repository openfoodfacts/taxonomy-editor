import {
  OutlinedInput,
  InputLabel,
  MenuItem,
  FormControl,
  ListItemText,
  Select,
  Checkbox,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
} from "@mui/material";
import { useState } from "react";
import ISO6391 from "iso-639-1";

const LanguageSelectionDialog = ({
  handleClose,
  mainLanguage,
  handleDialogConfirm,
  shownLanguages,
}) => {
  const [newShownLanguageCodes, setNewShownLanguageCodes] = useState([
    ...shownLanguages,
  ]); // Used for storing LCs that are selected in the checkbox (temporary state)

  const handleLanguageCheckToggle = (event) => {
    const newLanguageCodes = event.target.value;
    setNewShownLanguageCodes(newLanguageCodes);
  };

  return (
    <>
      <DialogTitle>Select shown languages</DialogTitle>
      <DialogContent>
        <FormControl sx={{ m: 1, width: 500 }}>
          <InputLabel id="multiple-lang-checkbox-label">Languages</InputLabel>
          <Select
            labelId="multiple-lang-checkbox-label"
            id="multiple-lang-checkbox"
            multiple
            value={newShownLanguageCodes}
            onChange={handleLanguageCheckToggle}
            input={<OutlinedInput label="Languages" />}
            renderValue={(selected) =>
              selected.map((langCode) => ISO6391.getName(langCode)).join(", ")
            }
          >
            {ISO6391.getAllNames()
              .sort()
              .map(
                (langName) =>
                  langName !== mainLanguage.main_language && (
                    <MenuItem key={langName} value={ISO6391.getCode(langName)}>
                      <Checkbox
                        checked={
                          newShownLanguageCodes.indexOf(
                            ISO6391.getCode(langName)
                          ) > -1
                        }
                      />
                      <ListItemText primary={langName} />
                    </MenuItem>
                  )
              )}
          </Select>
        </FormControl>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose}>Cancel</Button>
        <Button
          disabled={setNewShownLanguageCodes.length === 0}
          onClick={() => handleDialogConfirm(newShownLanguageCodes)}
        >
          Done
        </Button>
      </DialogActions>
    </>
  );
};

export default LanguageSelectionDialog;
