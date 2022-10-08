import { Typography, Box, TextField, Grid, IconButton, InputAdornment } from "@mui/material";
import SearchIcon from '@mui/icons-material/Search';
import { useState } from "react";
import SearchResults from "./results";

const SearchNode = () => {
    const [query, setQuery] = useState("");
    const [queryToBeSent, setQueryToBeSent] = useState(null);
    return (
      <Box>
        {/* <Container component="main" maxWidth="xs"> */}
            <Grid
            container
            direction="column"
            alignItems="center"
            justifyContent="center"
            >
                <Grid item xs={3} sx={{mt: 4}}>
                     <Typography variant="h3">Search</Typography>
                </Grid>
                <Box
                  component="img"
                  sx={{mt: 2}}
                  width={100} 
                  height={100}
                  src={require('../../assets/classification.png')} 
                  alt="Classification Logo" 
                />
                <form onSubmit={(event) => {event.preventDefault(); setQueryToBeSent(query)}}>
                  <TextField
                    sx={{mt: 3, width: 350}}
                    InputProps={{
                        endAdornment: (
                          <InputAdornment position="end">
                            <IconButton
                                disabled={query.length === 0}
                                type="submit"
                            >
                              <SearchIcon />
                            </IconButton>
                          </InputAdornment>
                        )
                      }}
                    onKeyDown={(e) => {
                      if (e.keyCode === 13 && query.length !== 0) {
                        setQueryToBeSent(query)
                      }
                    }}
                    onChange = {event => {
                        setQuery(event.target.value.trim())
                    }}
                    value={query} />
                </form>
            </Grid>
        {/* </Container> */}
        {queryToBeSent !== null && <SearchResults query={queryToBeSent}/>}
      </Box>
    );
}

export default SearchNode;