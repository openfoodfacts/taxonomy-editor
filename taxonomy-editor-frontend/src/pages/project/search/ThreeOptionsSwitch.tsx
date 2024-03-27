import { ToggleButton, ToggleButtonGroup, Typography } from "@mui/material";
import React, { Dispatch, SetStateAction } from "react";

const toggleTheme = {
  "& .MuiToggleButton-root": {
    color: "#341100",
    "&.Mui-selected": {
      color: "#341100",
    },
    borderColor: "rgba(0, 0, 0, 0.23)",
  },
};

type ThreeOptionsSwitchType = {
  filterValue: string;
  setFilterValue: Dispatch<SetStateAction<string>>;
  options: { [key: string]: { text: string; isNegated: boolean } };
  setQ: Dispatch<SetStateAction<string>>;
  keySearchTerm: string;
  setCurrentPage: Dispatch<SetStateAction<number>>;
};

export const ThreeOptionsSwitch = ({
  filterValue,
  setFilterValue,
  options,
  setQ,
  keySearchTerm,
  setCurrentPage,
}: ThreeOptionsSwitchType) => {
  const handleChange = (
    event: React.MouseEvent<HTMLElement>,
    newValue: string
  ) => {
    setFilterValue(newValue);
    setCurrentPage(1);
    let newFilterExpression = "";
    if (newValue) {
      // one of the options is selected
      if (options[newValue].isNegated) {
        newFilterExpression = ` is:not:${keySearchTerm}`;
      } else {
        newFilterExpression = ` is:${keySearchTerm}`;
      }
    }
    setQ((prevQ) => {
      prevQ = prevQ.replace(`is:not:${keySearchTerm}`, "");
      prevQ = prevQ.replace(`is:${keySearchTerm}`, "");
      return prevQ + newFilterExpression;
    });
  };
  return (
    <div style={{ display: "flex", flexDirection: "column" }}>
      <Typography
        variant="subtitle1"
        gutterBottom
        sx={{ mb: 0, m: "8px", color: "#341100" }}
      >
        Taxonomy
      </Typography>
      <ToggleButtonGroup
        sx={toggleTheme}
        value={filterValue}
        exclusive
        onChange={handleChange}
        aria-label="Platform"
      >
        {Object.entries(options).map(([value, option]) => (
          <ToggleButton key={value} value={value} sx={{ height: "2em" }}>
            {option.text}
          </ToggleButton>
        ))}
      </ToggleButtonGroup>
    </div>
  );
};
