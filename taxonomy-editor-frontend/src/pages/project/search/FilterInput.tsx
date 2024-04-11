import { FormControl, InputLabel, OutlinedInput } from "@mui/material";
import { Dispatch, SetStateAction, useState } from "react";

type FilterInputProps = {
  label: string;
  setQ: Dispatch<SetStateAction<string>>;
  keySearchTerm: string;
  setCurrentPage: Dispatch<SetStateAction<number>>;
};

export const FilterInput = ({
  label,
  setQ,
  keySearchTerm,
  setCurrentPage,
}: FilterInputProps) => {
  const [filterValue, setFilterValue] = useState("");
  const addFilter = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === "Enter" && filterValue !== "") {
      // If the filterValue includes a space, wrap it in double quotes. Ex : “en: paprika extract”, en:e101ii
      const value = filterValue.includes(" ")
        ? `"${filterValue}"`
        : filterValue;
      setCurrentPage(1);
      setQ((prevQ) => `${prevQ} ${keySearchTerm}:${value}`);
      event.preventDefault();
      setFilterValue("");
    }
  };

  return (
    <FormControl sx={{ m: 1, width: "170px" }} variant="outlined">
      <InputLabel id="multiple-select-label">{label}</InputLabel>
      <OutlinedInput
        id="property-input"
        sx={{ backgroundColor: "#f2e9e4" }}
        value={filterValue}
        onChange={(event) => setFilterValue(event.target.value)}
        onKeyDown={addFilter}
      />
    </FormControl>
  );
};
