import {
  Typography,
  Box,
  TextField,
  Grid,
  IconButton,
  InputAdornment,
} from "@mui/material";
import SearchIcon from "@mui/icons-material/Search";
import { useState, useEffect } from "react";
import SearchResults from "./SearchResults";
import { ENTER_KEYCODE } from "../../constants";
import { useParams } from "react-router-dom";

const SearchNode = ({ setDisplayedPages }) => {
  const { taxonomyName, branchName } = useParams();
  const urlPrefix = `${taxonomyName}/${branchName}/`;
  const [searchStringState, setSearchStringState] = useState("");
  const [queryFetchString, setQueryFetchString] = useState("");

  // Set url prefix for navbar component
  useEffect(
    function addUrlPrefixToNavbar() {
      setDisplayedPages([
        { url: urlPrefix + "entry", translationKey: "Nodes" },
        { url: urlPrefix + "search", translationKey: "Search" },
        { url: urlPrefix + "errors", translationKey: "Errors" },
        { url: urlPrefix + "export", translationKey: "Export" },
      ]);
    },
    [urlPrefix, setDisplayedPages]
  );

  return (
    <Box>
      <Grid
        container
        direction="column"
        alignItems="center"
        justifyContent="center"
      >
        <Typography sx={{ mt: 4 }} variant="h3">
          Search
        </Typography>
        <Box
          component="img"
          sx={{ mt: 2 }}
          width={100}
          height={100}
          src={require("../../assets/classification.png")}
          alt="Classification Logo"
        />
        <form
          onSubmit={(event) => {
            event.preventDefault();
            setQueryFetchString(searchStringState.trim());
          }}
        >
          <TextField
            sx={{ mt: 3, width: 350 }}
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton
                    disabled={searchStringState.trim().length === 0}
                    type="submit"
                  >
                    <SearchIcon />
                  </IconButton>
                </InputAdornment>
              ),
            }}
            onKeyDown={(e) => {
              if (
                e.keyCode === ENTER_KEYCODE &&
                searchStringState.length !== 0
              ) {
                setQueryFetchString(searchStringState.trim());
              }
            }}
            onChange={(event) => {
              setSearchStringState(event.target.value);
            }}
            value={searchStringState}
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

export default SearchNode;
