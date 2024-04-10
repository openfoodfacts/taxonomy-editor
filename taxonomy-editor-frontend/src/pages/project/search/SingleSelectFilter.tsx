import {
  FormControl,
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
  mapValueToCode: (value: string) => string;
  setQ: Dispatch<SetStateAction<string>>;
  keySearchTerm: string;
  setCurrentPage: Dispatch<SetStateAction<number>>;
};

export const SingleSelectFilter = ({
  label,
  filterValue,
  listOfChoices,
  mapValueToCode = () => "",
  setQ,
  keySearchTerm,
  setCurrentPage,
}: SingleSelectFilterType) => {
  const [menuOpen, setMenuOpen] = useState(false);

  const handleChange = (event: ChangeEvent<HTMLInputElement>) => {
    const codeItem = event.target.value;
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
      <InputLabel id="single-select-label">{label}</InputLabel>
      <Select
        id="languages-filter"
        sx={{ width: "170px" }}
        open={menuOpen}
        onClose={handleSelectClose}
        onOpen={handleSelectOpen}
        value={filterValue}
        onChange={handleChange}
      >
        {listOfChoices.map((languageNameItem) => {
          const languageCodeItem = mapValueToCode(languageNameItem);
          return (
            <MenuItem key={languageCodeItem} value={languageCodeItem}>
              <ListItemText primary={languageNameItem} />
            </MenuItem>
          );
        })}
      </Select>
    </FormControl>
  );
};
