import { Typography, Box, TextField, Grid, IconButton, InputAdornment } from "@mui/material";
import SearchIcon from '@mui/icons-material/Search';
import Container from '@mui/material/Container';
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

const SearchNode = () => {
    const [query, setQuery] = useState("");
    const [isDisabled, setIsDisabled] = useState(true);
    const navigate = useNavigate();

    return (
        <Container component="main" maxWidth="xs">
            <Grid
            container
            spacing={0}
            direction="column"
            alignItems="center"
            justifyContent="center"
            style={{ minHeight: '75vh' }}
            >
                <Grid item xs={3}>
                    <Typography variant="h3">Search</Typography>
                </Grid>
                <Box
                  component="img"
                  sx={{mt: 2}}
                  width={128} 
                  height={128}
                  src={require('../../assets/classification.png')} 
                  alt="Classification Logo" 
                />
                <TextField
                    sx={{mt: 4}}
                    InputProps={{
                        endAdornment: (
                          <InputAdornment position="end">
                            <IconButton
                                disabled={isDisabled}
                                component={Link}
                                to={{
                                  pathname: '/results',
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
                      if (e.key === "Enter" && !isDisabled) {
                        navigate(`/results?query=${query}`)
                      }
                    }}
                    onChange = {event => {
                        if (event.target.value === "") setIsDisabled(true)
                        else setIsDisabled(false)
                        setQuery(event.target.value)
                    }}
                    value={query} />
            </Grid>
        </Container>
    );
}

export default SearchNode;