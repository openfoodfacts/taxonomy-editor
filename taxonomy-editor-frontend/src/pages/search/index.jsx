import { Typography, Box, TextField, Grid, IconButton, InputAdornment } from "@mui/material";
import SearchIcon from '@mui/icons-material/Search';
import Container from '@mui/material/Container';
import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import SearchResults from "./results";

const SearchNode = () => {
    const [searchParams] = useSearchParams();
    let queryString = searchParams.get('query');
    if (queryString === "") queryString = "\"\""

    const [query, setQuery] = useState("");
    const navigate = useNavigate();
    return (
      <Box>
        <Container component="main" maxWidth="xs">
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
                <TextField
                    sx={{mt: 3}}
                    InputProps={{
                        endAdornment: (
                          <InputAdornment position="end">
                            <IconButton
                                disabled={query.trim().length === 0}
                                component={Link}
                                to={{
                                  pathname: '/search',
                                  search: `?query=${query}`
                                }}
                            >
                              <SearchIcon />
                            </IconButton>
                          </InputAdornment>
                        )
                      }}
                    fullWidth
                    onKeyDown={(e) => {
                      if (e.key === "Enter" && query.trim().length !== 0) {
                        navigate(`/search?query=${query}`)
                      }
                    }}
                    onChange = {event => {
                        setQuery(event.target.value.trim())
                    }}
                    value={query} />
            </Grid>
        </Container>
        {queryString !== null && <SearchResults query={queryString}/>}
      </Box>
    );
}

export default SearchNode;