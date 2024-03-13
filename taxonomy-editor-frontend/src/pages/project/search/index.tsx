import { useState } from "react";
import { useParams } from "react-router-dom";

import {
  Typography,
  Box,
  TextField,
  Grid,
  IconButton,
  InputAdornment,
} from "@mui/material";
import SearchIcon from "@mui/icons-material/Search";

import SearchResults from "./SearchResults";
import { ENTER_KEYCODE } from "@/constants";
import classificationImgUrl from "@/assets/classification.png";

type SearchNodeProps = {
  taxonomyName: string;
  branchName: string;
};

const SearchNode = ({ taxonomyName, branchName }: SearchNodeProps) => {
  const [searchInput, setSearchInput] = useState("");
  const [queryFetchString, setQueryFetchString] = useState("");

  return (
    <Box>
      <Grid
        container
        display="flex"
        flexDirection="column"
        alignItems="center"
        justifyContent="flex-start"
        gap="20px"
      >
        <Typography variant="h3">Search</Typography>
        <Box
          component="img"
          width={100}
          height={100}
          src={classificationImgUrl}
          alt="Classification Logo"
        />
        <form
          onSubmit={(event) => {
            event.preventDefault();
            setQueryFetchString(searchInput.trim());
          }}
        >
          <TextField
            sx={{ width: 350 }}
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton
                    disabled={searchInput.trim().length === 0}
                    type="submit"
                  >
                    <SearchIcon />
                  </IconButton>
                </InputAdornment>
              ),
            }}
            onKeyDown={(e) => {
              if (e.keyCode === ENTER_KEYCODE && searchInput.length !== 0) {
                setQueryFetchString(searchInput.trim());
              }
            }}
            onChange={(event) => {
              setSearchInput(event.target.value);
            }}
            value={searchInput}
          />
        </form>
      </Grid>
      {queryFetchString !== "" && (
        <SearchResults
          query={queryFetchString}
          taxonomyName={taxonomyName}
          branchName={branchName}
        />
      )}
    </Box>
  );
};

export const SearchNodeWrapper = () => {
  const { taxonomyName, branchName } = useParams();

  if (!taxonomyName || !branchName)
    return (
      <Typography variant="h3">
        Oops, something went wrong! Please try again later.
      </Typography>
    );

  return <SearchNode taxonomyName={taxonomyName} branchName={branchName} />;
};
