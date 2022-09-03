import { Box, Paper, Stack, TextField, Typography } from "@mui/material";
import { getIdType } from "./createURL";
import ISO6391 from 'iso-639-1';

/** 
 * Parent component used for rendering info on a stopword, synonym, header or footer
 * If node is an "stopword/synonym": Stopwords/synonyms, language and comments are rendered
 * If node is "header/footer": Only comments are rendered
*/

const ListAllNonEntryInfo = ({ nodeObject, id, setNodeObject }) => {
    
    // TODO: Change variables to state variables and wrap Object.keys() inside a useEffect()

    // Stores 2 letter language code (LC) of the tags
    let languageCode = '';
    // Storing keys and values that needs to be rendered for editing
    let renderedNonEntryInfo = {}

    if (nodeObject) {
        Object.keys(nodeObject).forEach((key) => {
            /** 
             * Get all tags and its corresponding language code
             * Tagids need to be recomputed, so shouldn't be rendered
             * Eg: tags_fr
            */ 
            if (key.startsWith('tags') && 
                !key.includes('ids')) {
                    languageCode = key.slice(-2);
                    renderedNonEntryInfo[languageCode] = nodeObject[key]
                }
        })
    }

    // Helper function used for changing state of "preceding_lines"
    function changeDataComment(value) {
        const newNodeObject = {...nodeObject};
        newNodeObject['preceding_lines'] = value.split('\n');
        setNodeObject(newNodeObject);
    }

    // Helper function used for changing state of properties
    function changeData(key, index, value) {
        const newNodeObject = {...nodeObject};
        newNodeObject[key][index] = value;
        setNodeObject(newNodeObject);
    }

    return ( 
        <Box>
            {/* Comments */}
            <Typography sx={{ml: 4, mt: 2, mb: 1}} variant='h5'>Comments</Typography>
            { nodeObject && <TextField
                sx={{ml: 8, mt: 1, width: 250}}
                minRows={4}
                multiline
                onChange = {event => {
                    changeDataComment(event.target.value)
                }}
                value={nodeObject.preceding_lines} 
                variant="outlined" /> }

            {/* Main Language */}
            { Object.keys(renderedNonEntryInfo).length > 0 && 
                <Box>
                    <Typography sx={{ml: 4, mt: 2}} variant='h5'>
                        Language
                    </Typography>
                    <Typography sx={{ml: 8, mt: 1.5}} variant='h6'>
                        {ISO6391.getName(languageCode)}
                    </Typography>
                </Box>
                }
            
            {/* Stopwords or Synonyms */}
            { Object.keys(renderedNonEntryInfo).length > 0 && 
                <Box>
                    <Typography sx={{ml: 4, mt: 1, mb: 1}} variant='h5'>
                        { getIdType(id) }
                    </Typography>
                    {/* Render all tags */}
                    <Paper component={Stack} direction="column" sx={{ml: 8, width: 200}}>
                        { renderedNonEntryInfo[languageCode].map((tag, index) => {
                            return (
                                <TextField 
                                    key={index}
                                    size="small" 
                                    sx={{mt: 1}} 
                                    onChange = {event => {
                                        changeData('tags_'+languageCode, index, event.target.value)
                                    }}
                                    value={tag} 
                                    variant="outlined" />
                            )})
                        }
                    </Paper>
                </Box>
            }
        </Box>
     );
}

export default ListAllNonEntryInfo;