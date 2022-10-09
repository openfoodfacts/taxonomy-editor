import { Typography, Box, TextField, Grid, IconButton, InputAdornment } from "@mui/material";
import SearchIcon from '@mui/icons-material/Search';
import { useState } from "react";
import SearchResults from "./SearchResults";
import { ENTER_KEYCODE } from "../../constants";

const SearchNode = () => {
    const [searchStringState, setSearchStringState] = useState("");
    const [queryFetchString, setQueryFetchString] = useState("");
    return (
      <Box>
          <Grid
          container
          direction="column"
          alignItems="center"
          justifyContent="center"
          >
              <Typography sx={{mt: 4}} variant="h3">Search</Typography>
              <Box
                component="img"
                sx={{mt: 2}}
                width={100} 
                height={100}
                src={require('../../assets/classification.png')} 
                alt="Classification Logo" 
              />
              <form onSubmit={(event) => {event.preventDefault(); setQueryFetchString(searchStringState.trim())}}>
                <TextField
                  sx={{mt: 3, width: 350}}
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
                      )
                    }}
                  onKeyDown={(e) => {
                    if (e.keyCode === ENTER_KEYCODE && searchStringState.length !== 0) {
                      setQueryFetchString(searchStringState.trim())
                    }
                  }}
                  onChange = {event => {
                      setSearchStringState(event.target.value)
                  }}
                  value={searchStringState} />
              </form>
          </Grid>
        {queryFetchString !== "" && <SearchResults query={queryFetchString}/>}
      </Box>
    );
}

export default SearchNode;