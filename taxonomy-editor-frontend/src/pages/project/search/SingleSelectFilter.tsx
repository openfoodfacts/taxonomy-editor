import {
  FormControl,
  Checkbox,
  Select,
  MenuItem,
  InputLabel,
  ListItemText,
} from "@mui/material";
import { ChangeEvent, Dispatch, SetStateAction, useState } from "react";

type SingleSelectFilterType = {
  label: string;
  filterValue: string;
  listOfChoices: string[];
  mapCodeToValue: (code: string) => string;
  mapValueToCode: (value: string) => string;
  setQ: Dispatch<SetStateAction<string>>;
  keySearchTerm: string;
  setCurrentPage: Dispatch<SetStateAction<number>>;
};

export const SingleSelectFilter = ({
  label,
  filterValue,
  listOfChoices,
  mapCodeToValue = () => "",
  mapValueToCode = () => "",
  setQ,
  keySearchTerm,
  setCurrentPage,
}: SingleSelectFilterType) => {
  const [menuOpen, setMenuOpen] = useState(false);

  const handleChange = (
    event: ChangeEvent<HTMLInputElement>,
    codeItem: string
  ) => {
    setCurrentPage(1);
    if (filterValue !== codeItem) {
      setQ((prevQ) => {
        let newQ = prevQ;
        if (codeItem !== "both") {
          newQ += ` ${keySearchTerm}:${codeItem}`; // add new filter value
        }
        newQ = newQ.replace(`${keySearchTerm}:${filterValue}`, ""); //remove potential previous filter value
        return newQ;
      });
    }
    setMenuOpen((prevMenuOpen) => !prevMenuOpen);
  };

  const handleSelectOpen = () => {
    setMenuOpen(true);
  };

  const handleSelectClose = () => {
    setMenuOpen(false);
  };

  return (
    <FormControl sx={{ m: 1 }}>
      <InputLabel id="multiple-select-label">{label}</InputLabel>
      <Select
        id="languages-filter"
        sx={{ width: "170px" }}
        open={menuOpen}
        onClose={handleSelectClose}
        onOpen={handleSelectOpen}
        value={mapCodeToValue(filterValue)}
        renderValue={(selected) => selected}
      >
        {listOfChoices.map((languageNameItem) => {
          const languageCodeItem = mapValueToCode(languageNameItem);
          return (
            <MenuItem key={languageCodeItem} value={languageCodeItem}>
              <Checkbox
                checked={filterValue === languageCodeItem}
                onChange={(event) => handleChange(event, languageCodeItem)}
              />
              <ListItemText primary={languageNameItem} />
            </MenuItem>
          );
        })}
      </Select>
    </FormControl>
  );
};
