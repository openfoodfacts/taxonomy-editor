import { FormControl, OutlinedInput, InputAdornment } from "@mui/material";
import SearchIcon from "@mui/icons-material/Search";
import { Dispatch, SetStateAction } from "react";

type SearchExpressionInputType = {
  searchExpression: string;
  setSearchExpression: Dispatch<SetStateAction<string>>;
  setCurrentPage: Dispatch<SetStateAction<number>>;
  setQ: Dispatch<SetStateAction<string>>;
};

export const SearchExpressionInput = ({
  searchExpression,
  setSearchExpression,
  setCurrentPage,
  setQ,
}: SearchExpressionInputType) => {
  const handleEnterKeyPress = (
    event: React.KeyboardEvent<HTMLInputElement>
  ) => {
    setCurrentPage(1);
    if (event.key === "Enter") {
      setQ(searchExpression);
      event.preventDefault();
    }
  };

  const handleSearchInputChange = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    setSearchExpression(event.target.value);
  };

  return (
    <FormControl fullWidth sx={{ m: 1 }} variant="outlined">
      <OutlinedInput
        id="search-expression"
        sx={{ backgroundColor: "#f2e9e4" }}
        startAdornment={
          <InputAdornment position="start">
            <SearchIcon />
          </InputAdornment>
        }
        value={searchExpression}
        onChange={handleSearchInputChange}
        onKeyDown={handleEnterKeyPress}
      />
    </FormControl>
  );
};
