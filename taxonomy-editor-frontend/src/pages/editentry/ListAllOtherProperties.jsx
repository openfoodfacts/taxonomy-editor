import { Box, Paper, Stack, TextField, Typography, Button } from "@mui/material";
import { useState, useEffect } from "react";
import AddBoxIcon from '@mui/icons-material/AddBox';
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline';
import * as uuid from "uuid";
import ISO6391 from 'iso-639-1';

// Parent component used for rendering info
// on a stopword, synonym, header or footer

const ListAllOtherProperties = ({ nodeObject, id, setNodeObject, originalNodeObject }) => {
    
    // Stores 2 letter language code (LC) of the tags
    let [languageCode, setLanguageCode] = useState('');
    // Storing tags that need to be rendered for editing
    let [toBeRendered, setToBeRendered] = useState([])

    useEffect(() => {
        let tagsExtracted = []
        let extractedLC = ''
        if (originalNodeObject) {
            Object.keys(originalNodeObject).forEach((key) => {
    
                // Get all tags and its corresponding language code
                // Tagids need to be recomputed, so shouldn't be rendered
    
                if (key.startsWith('tags') && 
                    !key.includes('ids')) {
                        extractedLC = key.slice(-2);
                        originalNodeObject[key].map((tag) => (
                            tagsExtracted.push({
                                'index' : uuid.v4(),
                                'tag' : tag
                            })
                        ))
                    }
            })
        }
        setLanguageCode(extractedLC)
        setToBeRendered(tagsExtracted)
    }, [originalNodeObject])
    
    // Helper function used for changing state of "preceding_lines"
    function changeDataComment(value) {
        const duplicateData = {...nodeObject};
        duplicateData['preceding_lines'] = value.split('\n');
        setNodeObject(duplicateData);
    }

    // Helper function used for changing state of properties
    function changeData(index, value) {
        const updatedObj = {'index' : index, 'tag' : value}
        const duplicateToBeRendered = toBeRendered.map(obj => (obj.index === index) ? updatedObj : obj)
        setToBeRendered(duplicateToBeRendered); // Set state

        // Updated tags assigned for later use
        const tagsToBeInserted = duplicateToBeRendered.map(el => (el.tag))

        setNodeObject(prevState => {
            const duplicateData = {...prevState};
            duplicateData['tags_'+languageCode] = tagsToBeInserted;
            return duplicateData
        })
    }

    function handleAdd() {
        const duplicateToBeRendered = [...toBeRendered, {'index': uuid.v4(), 'tag' : ''}];
        setToBeRendered(duplicateToBeRendered); // Set state

        // Updated tags assigned for later use
        const tagsToBeInserted = duplicateToBeRendered.map(el => (el.tag))
        setNodeObject(prevState => {
            const duplicateData = {...prevState};
            duplicateData['tags_'+languageCode] = tagsToBeInserted;
            return duplicateData
        })
    }

    function handleDelete(index) {
        const duplicateToBeRendered = toBeRendered.filter(obj => !(obj.index === index))
        setToBeRendered(duplicateToBeRendered); // Set state

        // Updated tags assigned for later use
        const tagsToBeInserted = duplicateToBeRendered.map(el => (el.tag))
        setNodeObject(prevState => {
            const duplicateData = {...prevState};
            duplicateData['tags_'+languageCode] = tagsToBeInserted;
            console.log(duplicateData);
            return duplicateData
        })
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
            { toBeRendered.length > 0 && 
                <div className="language">
                    <Typography sx={{ml: 4, mt: 2}} variant='h5'>
                        Language
                    </Typography>
                    <Typography sx={{ml: 8, mt: 1.5}} variant='h6'>
                        {ISO6391.getName(languageCode)}
                    </Typography>
                </div>
                }
            
            {/* Stopwords or Synonyms */}
            { toBeRendered.length > 0 && 
                <div className="tags">
                    {id.startsWith('stopword') ?
                        <Stack direction="row" alignItems="center">
                            <Typography sx={{ml: 4, mt: 1, mb: 1.3}} variant='h5'>
                                Stopwords
                            </Typography>
                            <Button sx={{ml: -1, color: "#808080"}} onClick={handleAdd}>
                                <AddBoxIcon />
                            </Button>
                        </Stack> :
                        <Stack direction="row" alignItems="center">
                            <Typography sx={{ml: 4, mt: 1, mb: 1.3}} variant='h5'>
                                Synonyms
                            </Typography>
                            <Button sx={{ml: -1, color: "#808080"}} onClick={handleAdd}>
                                <AddBoxIcon />
                            </Button>
                        </Stack>}

                    {/* Render all tags */}
                    { toBeRendered.map((tagObj) => {
                        const index = tagObj.index;
                        const tag = tagObj.tag;
                        return (
                            <Stack key={index} direction="row" alignItems="center">
                                <Paper key={index} component={Stack} direction="column" sx={{ml: 8, width: 200}}>
                                    <TextField 
                                        size="small" 
                                        sx={{mt: 1}} 
                                        onChange = {event => {
                                            changeData(index, event.target.value)
                                        }}
                                        defaultValue={tag} 
                                        variant="outlined" />
                                </Paper>
                                <Button sx={{ml: -1, mt: 1, color: "#808080"}} onClick={(e) => handleDelete(index, e)}>
                                    <DeleteOutlineIcon />
                                </Button>
                            </Stack>
                        )})}
                </div>
            }
        </Box>
     );
}

export default ListAllOtherProperties;