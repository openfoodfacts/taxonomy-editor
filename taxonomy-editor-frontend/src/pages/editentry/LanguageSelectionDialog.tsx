import { useState } from "react";
import ISO6391 from "iso-639-1";

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

type Props = {
  handleClose: () => void;
  mainLanguageCode: string;
  handleDialogConfirm: (newLanguageCodes: string[]) => void;
  shownLanguageCodes: string[];
};

const LanguageSelectionDialog = ({
  handleClose,
  mainLanguageCode,
  handleDialogConfirm,
  shownLanguageCodes,
}: Props) => {
  const [newShownLanguageCodes, setNewShownLanguageCodes] = useState([
    ...shownLanguageCodes,
  ]);

  return (
    <>
      <DialogTitle>Select shown languages</DialogTitle>
      <DialogContent>
        <FormControl sx={{ m: 1, width: 500 }}>
          <InputLabel id="multiple-lang-checkbox-label">Languages</InputLabel>
          <Select
            labelId="multiple-lang-checkbox-label"
            id="multiple-lang-checkbox"
            value={newShownLanguageCodes}
            multiple
            onChange={
              (event) =>
                setNewShownLanguageCodes(event.target.value as string[]) // type casting to string[] due to the `multiple` prop
            }
            input={<OutlinedInput label="Languages" />}
            renderValue={(selected) =>
              selected.map((langCode) => ISO6391.getName(langCode)).join(", ")
            }
          >
            {["All languages"].concat(ISO6391.getAllNames())
              .sort()
              .map((languageNameItem) => {
                const languageCodeItem = languageNameItem === "All languages" ? "xx" : ISO6391.getCode(languageNameItem);
                return languageCodeItem === mainLanguageCode ? null : (
                  <MenuItem key={languageCodeItem} value={languageCodeItem}>
                    <Checkbox
                      checked={newShownLanguageCodes.includes(languageCodeItem)}
                    />
                    <ListItemText primary={languageNameItem} />
                  </MenuItem>
                );
              })}
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
