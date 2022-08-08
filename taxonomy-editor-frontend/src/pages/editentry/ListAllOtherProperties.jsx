import { Box, Paper, Stack, TextField, Typography } from "@mui/material";

// Parent component used for rendering info
// on a stopword, synonym, header or footer

const ListAllOtherProperties = ({ nodeObject, id, setNodeObject }) => {
    
    // Stores 2 letter language code (LC) of the tags
    let languageCode = ''; 
    // Storing keys and values that needs to be rendered for editing
    let toBeRendered = {} 
    // Used for conversion of LC to long-form
    let languageNames = new Intl.DisplayNames(['en'], {type: 'language'}); 

    if (nodeObject) {
        Object.keys(nodeObject).forEach((key) => {

            // Get all tags and its corresponding language code
            // Tagids need to be recomputed, so shouldn't be rendered

            if (key.startsWith('tags') && 
                !key.includes('ids')) {
                    languageCode = key.slice(-2);
                    toBeRendered[languageCode] = nodeObject[key]
                }
        })
    }

    // Helper function used for changing state of "preceding_lines"
    function changeDataComment(value) {
        const duplicateData = {...nodeObject};
        duplicateData['preceding_lines'] = value.split('\n');
        setNodeObject(duplicateData);
    }

    // Helper function used for changing state of properties
    function changeData(key, index, value) {
        const duplicateData = {...nodeObject};
        duplicateData[key][index] = value;
        setNodeObject(duplicateData);
    }

    return ( 
        <Box className="all-node-properties">
            {/* Comments */}
            <Typography sx={{ml: 4, mt: 2, mb: 1}} variant='h5'>Comments</Typography>
            { nodeObject && <TextField
                sx={{ml: 8, mt: 1, width: 250}}
                minRows={4}
                multiline
                onChange = {event => {
                    changeDataComment(event.target.value)
                }}
                defaultValue={nodeObject.preceding_lines} 
                variant="outlined" /> }

            {/* Main Language */}
            { Object.keys(toBeRendered).length > 0 && 
                <div className="language">
                    <Typography sx={{ml: 4, mt: 2}} variant='h5'>
                        Language
                    </Typography>
                    <Typography sx={{ml: 8, mt: 1.5}} variant='h6'>
                        {languageNames.of(languageCode)}
                    </Typography>
                </div>
                }
            
            {/* Stopwords or Synonyms */}
            { Object.keys(toBeRendered).length > 0 && 
                <div className="tags">
                    {id.startsWith('stopword') ?
                        <Typography sx={{ml: 4, mt: 1, mb: 1}} variant='h5'>
                            Stopwords
                        </Typography> :
                        <Typography sx={{ml: 4, mt: 1, mb: 1}} variant='h5'>
                            Synonyms
                        </Typography>}

                    {/* Render all tags */}
                    { toBeRendered[languageCode].map((tag, index) => {
                        return (
                            <Paper key={index} component={Stack} direction="column" sx={{ml: 8, width: 200}}>
                                <TextField 
                                    size="small" 
                                    sx={{mt: 1}} 
                                    onChange = {event => {
                                        changeData('tags_'+languageCode, index, event.target.value)
                                    }}
                                    defaultValue={tag} 
                                    variant="outlined" />
                            </Paper>
                        )})}
                </div>
            }
        </Box>
     );
}

export default ListAllOtherProperties;