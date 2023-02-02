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

  const languageNames = [...ISO6391.getAllNames()].sort();

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
            onChange={(event) =>
              setNewShownLanguageCodes(event.target.value as string[])
            }
            input={<OutlinedInput label="Languages" />}
            renderValue={(selected) =>
              selected.map((langCode) => ISO6391.getName(langCode)).join(", ")
            }
          >
<<<<<<< HEAD:taxonomy-editor-frontend/src/pages/editentry/LanguageSelectionDialog.jsx
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
=======
            {languageNames.map((languageNameItem) => {
              const languageCode = ISO6391.getCode(languageNameItem);
              return (
                languageCode !== mainLanguageCode && (
                  <MenuItem key={languageNameItem} value={languageCode}>
                    <Checkbox
                      checked={newShownLanguageCodes.indexOf(languageCode) > -1}
                    />
                    <ListItemText primary={languageNameItem} />
                  </MenuItem>
                )
              );
            })}
>>>>>>> db3f481 (refactor: typescript, 2) moved utils to the utils file):taxonomy-editor-frontend/src/pages/editentry/LanguageSelectionDialog.tsx
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
