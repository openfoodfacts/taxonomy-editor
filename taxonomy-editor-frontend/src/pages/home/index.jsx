import Button from '@mui/material/Button';
import {Link as MuiLink} from '@mui/material';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Container from '@mui/material/Container';
import { Link } from "react-router-dom";


const Home = () => {
    return (
        <Container component="main" maxWidth="md">
            <Box
            sx={{
                marginTop: 4,
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
            <Box sx={{mt: 1}} />
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
            <Button 
                variant="contained" 
                component={Link}
                to="/entry"
                sx={{textDecoration: 'none', mb: 2, backgroundColor: '#0064c8'}}>
                Start Editing!
            </Button>
            </Box>
            <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 8, mb: 4 }}>
              {'Copyright © '}
              <MuiLink color="inherit" href="https://world.openfoodfacts.org/">
                Open Food Facts
              </MuiLink>{' '}
              {new Date().getFullYear()}
              {'.'}
            </Typography>
        </Container>
    );
}

export default Home;