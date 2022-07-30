import { createTheme, ThemeProvider, Typography } from "@mui/material";
import { useParams } from "react-router-dom";
import FetchRelations from "../../components/FetchRelations";

const EditEntry = () => {
    let url = 'http://localhost:80/'
    let isEntry = false;
    const { id } = useParams();

    if (id.startsWith('__header__')) { url += 'header/' }
    else if (id.startsWith('__footer__')) { url += 'footer/' }
    else if (id.startsWith('synonym')) { url += `synonym/${id}/` }
    else if (id.startsWith('stopword')) { url += `stopword/${id}/` }
    else { url += `entry/${id}/`; isEntry = true; }

    const theme = createTheme({
        typography: {
            fontFamily : 'Plus Jakarta Sans',
        },
    });
    return (
        <ThemeProvider theme={theme}>
            <Typography sx={{mb: 2, mt:2, ml: 2}} variant="h4">
                You are now editing "{id}"
            </Typography>
            { isEntry && <FetchRelations url={url+'parents'} title={'Parents'} /> }
            { isEntry && <FetchRelations url={url+'children'} title={'Children'} /> }
        </ThemeProvider>
    );
}
 
export default EditEntry;