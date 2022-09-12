import { Box, Paper, Stack, TextField, Typography, Button } from "@mui/material";
import { useState, useEffect } from "react";
import { getIdType } from "./createURL";
import AddBoxIcon from '@mui/icons-material/AddBox';
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline';
import * as uuid from "uuid";
import ISO6391 from 'iso-639-1';

/** 
 * Parent component used for rendering info on a stopword, synonym, header or footer
 * If node is an "stopword/synonym": Stopwords/synonyms, language and comments are rendered
 * If node is "header/footer": Only comments are rendered
*/

const ListAllNonEntryInfo = ({ nodeObject, id, setNodeObject, originalNodeObject }) => {
    
    // Stores ID type of node object
    let IDType = getIdType(id);
    // Stores 2 letter language code (LC) of the tags
    let [languageCode, setLanguageCode] = useState('');
    // Storing tags that need to be rendered for editing
    let [renderedNonEntryInfo, setRenderedNonEntryInfo] = useState([])

    useEffect(() => {
        let tagsExtracted = []
        let extractedLanguageCode = ''
        if (originalNodeObject) {
            Object.keys(originalNodeObject).forEach((key) => {
    
                // Get all tags and its corresponding language code
                // Tagids need to be recomputed, so shouldn't be rendered
                // Eg: tags_fr
    
                if (key.startsWith('tags') && 
                    !key.includes('ids')) {
                        extractedLanguageCode = key.slice(-2);
                        originalNodeObject[key].map((tag) => (
                            tagsExtracted.push({
                                'index' : uuid.v4(),
                                'tag' : tag
                            })
                        ))
                    }
            })
        }
        setLanguageCode(extractedLanguageCode)
        setRenderedNonEntryInfo(tagsExtracted)
    }, [originalNodeObject])
    
    // Helper function used for changing state of "preceding_lines"
    function changeDataComment(value) {
        const newNodeObject = {...nodeObject};
        newNodeObject['preceding_lines'] = value.split('\n');
        setNodeObject(newNodeObject);
    }

    // Helper function used for changing state of properties
    function changeData(index, value) {
        const updatedTagObject = {'index' : index, 'tag' : value}
        const newRenderedNonEntryInfo = renderedNonEntryInfo.map(obj => (obj.index === index) ? updatedTagObject : obj)
        setRenderedNonEntryInfo(newRenderedNonEntryInfo); // Set state

        // Updated tags assigned for later use
        const tagsToBeInserted = newRenderedNonEntryInfo.map(el => (el.tag))

        setNodeObject(prevState => {
            const newNodeObject = {...prevState};
            newNodeObject['tags_'+languageCode] = tagsToBeInserted;
            return newNodeObject
        })
    }

    function handleAdd() {
        const newRenderedNonEntryInfo = [...renderedNonEntryInfo, {'index': uuid.v4(), 'tag' : ''}];
        setRenderedNonEntryInfo(newRenderedNonEntryInfo); // Set state

        // Updated tags assigned for later use
        const tagsToBeInserted = newRenderedNonEntryInfo.map(el => (el.tag))
        setNodeObject(prevState => {
            const newNodeObject = {...prevState};
            newNodeObject['tags_'+languageCode] = tagsToBeInserted;
            return newNodeObject
        })
    }

    function handleDelete(index) {
        const newRenderedNonEntryInfo = renderedNonEntryInfo.filter(obj => !(obj.index === index))
        setRenderedNonEntryInfo(newRenderedNonEntryInfo); // Set state

        // Updated tags assigned for later use
        const tagsToBeInserted = newRenderedNonEntryInfo.map(el => (el.tag))
        setNodeObject(prevState => {
            const newNodeObject = {...prevState};
            newNodeObject['tags_'+languageCode] = tagsToBeInserted;
            return newNodeObject
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
                value={nodeObject.preceding_lines} 
                variant="outlined" /> }

            {/* Main Language */}
            { (IDType === 'Synonyms' || IDType === 'Stopwords') && 
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
            { (IDType === 'Synonyms' || IDType === 'Stopwords') &&  
                <Box className="tags">
                    <Stack direction="row" alignItems="center">
                        <Typography sx={{ml: 4, mt: 1, mb: 1.3}} variant='h5'>
                            { IDType }
                        </Typography>
                        <Button sx={{ml: -1, color: "#808080"}} onClick={handleAdd}>
                            <AddBoxIcon />
                        </Button>
                    </Stack>
                    {/* Render all tags */}
                    { renderedNonEntryInfo.map((tagObj) => {
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
                                        value={tag}
                                        variant="outlined" />
                                </Paper>
                                <Button sx={{ml: -1, mt: 1, color: "#808080"}} onClick={(e) => handleDelete(index, e)}>
                                    <DeleteOutlineIcon />
                                </Button>
                            </Stack>
                        )})}
                </Box>
            }
        </Box>
     );
}

export default ListAllNonEntryInfo;