import Button from '@mui/material/Button';
import CssBaseline from '@mui/material/CssBaseline';
import Link from '@mui/material/Link';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Container from '@mui/material/Container';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import { useNavigate } from "react-router-dom";

function Copyright(props) {
  return (
    <Typography variant="body2" color="text.secondary" align="center" {...props}>
      {'Copyright © '}
      <Link color="inherit" href="https://world.openfoodfacts.org/">
        Open Food Facts
      </Link>{' '}
      {new Date().getFullYear()}
      {'.'}
    </Typography>
  );
}

const Home = () => {
    const theme = createTheme({
        typography: {
            fontFamily : 'Plus Jakarta Sans',
        },
    });
    const navigate = useNavigate();

    const handleSubmit = (event) => {
        event.preventDefault();
        navigate('/entry');
    };

    return (
        <ThemeProvider theme={theme}>
        <Container component="main" maxWidth="md">
            <CssBaseline />
            <Box
            sx={{
                marginTop: 8,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
            }}
            >
            <Box
                component="img"
                height={140}
                width={700}
                src={require('../../assets/logo.png')} 
                alt="Open Food Facts Logo" 
            />
            <Box sx={{mt: 3}} />
            <Box
                component="img" 
                width={128} 
                height={128}
                src={require('../../assets/classification.png')} 
                alt="Classification Logo" 
            />
            <Typography sx={{mt: 4, mb: 4}} variant="h2">
                Taxonomy Editor
            </Typography>
            <Box component="form" onSubmit={ handleSubmit } noValidate sx={{ mt: 1 }}>
                <Button
                type="submit"
                fullWidth
                variant="contained"
                sx={{mb: 2}}
                >
                Start Editing!
                </Button>
            </Box>
            </Box>
            <Copyright sx={{ mt: 8, mb: 4 }} />
        </Container>
        </ThemeProvider>
    );
}

export default Home;