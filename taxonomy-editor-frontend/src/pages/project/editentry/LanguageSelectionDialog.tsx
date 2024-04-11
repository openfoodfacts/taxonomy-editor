import { useEffect, useRef, useState } from "react";
import ISO6391 from "iso-639-1";

import {
  Autocomplete,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
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
  const [newLanguageCodes, setNewLanguageCodes] = useState<string[]>([]);
  const inputRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

  return (
    <>
      <DialogTitle>Show another language</DialogTitle>
      <DialogContent>
        <Autocomplete
          multiple
          openOnFocus
          sx={{ m: 1, width: 500 }}
          value={newLanguageCodes.map((langCode) => ISO6391.getName(langCode))}
          onChange={(_event, newValue: string[]) => {
            setNewLanguageCodes(
              newValue.map((langName) => ISO6391.getCode(langName))
            );
          }}
          options={ISO6391.getAllNames()
            .sort()
            .filter(
              (languageName) =>
                !shownLanguageCodes.includes(ISO6391.getCode(languageName)) &&
                !newLanguageCodes.includes(ISO6391.getCode(languageName)) &&
                languageName !== ISO6391.getName(mainLanguageCode)
            )}
          getOptionLabel={(option) => option}
          renderInput={(params) => (
            <TextField {...params} label="Enter language" inputRef={inputRef} />
          )}
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose}>Cancel</Button>
        <Button
          disabled={newLanguageCodes.length === 0}
          onClick={() => handleDialogConfirm(newLanguageCodes)}
        >
          Add
        </Button>
      </DialogActions>
    </>
  );
};

export default LanguageSelectionDialog;
