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
  Dialog,
  Button,
} from "@mui/material";
import { useEffect, useState } from "react";
import ISO6391 from "iso-639-1";

const LanguageSelectionDialog = ({
  isDialogOpen,
  handleClose,
  mainLanguage,
  handleLanguagesChange,
  selectedShownLanguages,
}) => {
  const [newShownLanguageCodes, setNewShownLanguageCodes] = useState([]); // Used for storing LCs that are selected in the checkbox (temporary state)

  useEffect(() => {
    setNewShownLanguageCodes(selectedShownLanguages);
  }, [selectedShownLanguages]);

  const handleLanguageCheckToggle = (event) => {
    const {
      target: { value },
    } = event;
    setNewShownLanguageCodes(
      typeof value === "string" ? value.split(",") : value
    );
  };

  return (
    <Dialog open={isDialogOpen} onClose={handleClose}>
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
            {ISO6391.getAllCodes().map(
              (langCode) =>
                langCode !== mainLanguage.main_language && (
                  <MenuItem key={langCode} value={langCode}>
                    <Checkbox
                      checked={newShownLanguageCodes.indexOf(langCode) > -1}
                    />
                    <ListItemText primary={ISO6391.getName(langCode)} />
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
          onClick={() => handleLanguagesChange(newShownLanguageCodes)}
        >
          Show Languages
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default LanguageSelectionDialog;
