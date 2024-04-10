import {
  FormControl,
  OutlinedInput,
  InputAdornment,
  IconButton,
} from "@mui/material";
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
      handleSearch();
      event.preventDefault();
    }
  };

  const handleSearch = () => {
    setQ(searchExpression);
  };

  const handleSearchInputChange = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    setSearchExpression(event.target.value);
  };

  return (
    <FormControl
      fullWidth
      sx={{ m: 1, display: "flex", alignItems: "center", flexDirection: "row" }}
      variant="outlined"
    >
      <OutlinedInput
        id="search-expression"
        sx={{ backgroundColor: "#f2e9e4", flexGrow: 1 }}
        startAdornment={
          <InputAdornment position="start">
            <SearchIcon />
          </InputAdornment>
        }
        value={searchExpression}
        onChange={handleSearchInputChange}
        onKeyDown={handleEnterKeyPress}
      />
      <IconButton onClick={handleSearch}>
        <SearchIcon />
      </IconButton>
    </FormControl>
  );
};
