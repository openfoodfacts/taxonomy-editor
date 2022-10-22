import { Box, Grid, Typography, Alert, Snackbar, Button, Link as MuiLink, CircularProgress} from "@mui/material";
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import { useParams } from "react-router-dom";
import { createBaseURL } from "../editentry/createURL";
import { useState, useEffect } from "react";

const ExportTaxonomy = ({setDisplayedPages}) => {
    const { taxonomyName, branchName } = useParams();
    const urlPrefix = `${taxonomyName}/${branchName}/`;
    const baseURL = createBaseURL(taxonomyName, branchName);

    const [loadingForDownload, setLoadingForDownload] = useState(false);
    const [loadingForGithub, setLoadingForGitHub] = useState(false);
    const [openSuccessDialog, setOpenSuccessDialog] = useState(false);
    const [pullRequestURL, setPullRequestURL] = useState(null);
    const [openErrorSnackbar, setOpenErrorSnackbar] = useState(false);
    const [errorMessage, setErrorMessage] = useState("");

    // Set url prefix for navbar component
    useEffect(() => {
        setDisplayedPages([
            { url: urlPrefix+"entry", translationKey: "Nodes" },
            { url: urlPrefix+"search", translationKey: "Search" },
            { url: urlPrefix+"export", translationKey: "Export" }
        ])
    }, [urlPrefix, setDisplayedPages])

    function handleDownload() {
        setLoadingForDownload(true);
        fetch(baseURL+'downloadexport', {
            method : 'GET'
        }).then((response) => {
            return response.blob();
        }).then((blob) => {
            // Download taxonomy
            var url = window.URL.createObjectURL(blob);
            var a = document.createElement('a');
            a.href = url;
            a.download = taxonomyName + '.txt'
            document.body.appendChild(a);
            a.click(); a.remove();

            setLoadingForDownload(false);
        }).catch(() => {
            setErrorMessage("Download failed!")
            setLoadingForDownload(false); setOpenSuccessDialog(true)
        })
    }

    function handleGithub() {
        setLoadingForGitHub(true);
        fetch(baseURL+'githubexport', {
            method: 'GET'
        }).then(async (response) => {
            const responseBody = await response.json();
            if (!response.ok) {
                throw Error(responseBody.detail);
            } else {
                setPullRequestURL(responseBody);
                setLoadingForGitHub(false);
                setOpenSuccessDialog(true);
            }
        }).catch((detail) => {
            setErrorMessage(detail.message); 
            setLoadingForGitHub(false); setOpenErrorSnackbar(true)
        })
    }

    function LoadingButton(props) {
        const { onClick, loading, text, sx } = props;
        return (
            <Button variant="contained" sx={sx} onClick={onClick} disabled={loading}>
                {loading && <CircularProgress size={24} />}
                {!loading && text}
            </Button>
        );    
    }

    function handleCloseErrorSnackbar() {
        setOpenErrorSnackbar(false);
    }
    function handleCloseSuccessDialog() {
        setOpenSuccessDialog(false);
    }

    return (
        <Box>
            <Grid
            container
            direction="column"
            alignItems="center"
            justifyContent="center"
            >
                <Typography sx={{mt: 4}} variant="h3">Export Taxonomy</Typography>
                <Typography sx={{mt: 8}} variant="h5">Click the button below to download your edited taxonomy</Typography>
                <LoadingButton
                    loading={loadingForDownload}
                    onClick={handleDownload}
                    sx={{mt: 4, width: 130}}
                    text="Download"
                >
                </LoadingButton>
                <Typography sx={{mt: 10}} variant="h5">Click the button below to create a Pull Request to Github</Typography>
                <LoadingButton
                    loading={loadingForGithub}
                    onClick={handleGithub}
                    sx={{mt: 4, width: 130}}
                    text="Create PR"
                >
                </LoadingButton>
                
            </Grid>
            {/* Snackbar to show errors */}
            <Snackbar anchorOrigin={{vertical: 'top', horizontal: 'right'}} open={openErrorSnackbar} autoHideDuration={3000} onClose={handleCloseErrorSnackbar}>
                <Alert elevation={6} variant="filled" onClose={handleCloseErrorSnackbar} severity="error">
                    {errorMessage}
                </Alert>
            </Snackbar>
            {/* Dialog box for acknowledgement the creation of a pull request */}
            <Dialog
                open={openSuccessDialog}
            >
                <DialogTitle>Your pull request has been created!</DialogTitle>
                <DialogContent>
                <DialogContentText>
                    Thank you for contributing! A maintainer will review your changes soon.
                </DialogContentText>
                </DialogContent>
                <DialogActions>
                <Button onClick={handleCloseSuccessDialog}>
                    Cancel
                </Button>
                <Button component={MuiLink} href={pullRequestURL} autoFocus>
                    Go to PR
                </Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
}
export default ExportTaxonomy;