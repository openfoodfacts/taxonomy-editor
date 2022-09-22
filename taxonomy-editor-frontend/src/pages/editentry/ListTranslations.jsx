import { Typography, Paper, TextField, Stack, Button, IconButton, Box } from "@mui/material";
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import { useEffect, useState } from "react";
import AddBoxIcon from '@mui/icons-material/AddBox';
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline';
import * as uuid from "uuid";
import ISO6391 from 'iso-639-1';

/**
 * Sub-component for rendering translation of an "entry"  
*/
const ListTranslations = ({ nodeObject, setNodeObject, originalNodeObject }) => {

    const [renderedTranslations, setRenderedTranslations] = useState([]) // Stores state of all tags
    const [mainLang_renderedTranslations, setMainLang_renderedTranslations] = useState([]) // Stores state of main language's tags
    const [open, setOpen] = useState(false); // Used for Dialog component
    const [newLanguageCode, setNewLanguageCode] = useState(''); // Used for storing new LC from Dialog
    const [isValidLanguageCode, setisValidLanguageCode] = useState(false); // Used for validating a new LC
    const [btnDisabled, setBtnDisabled] = useState(true) // For enabling or disabling Dialog button

    // Helper functions for Dialog component
    function handleClose() { setOpen(false); }
    function handleOpen() { setOpen(true); }

    // Used for addition of a translation language
    function handleAddTranslation(key) {
        const newRenderedTranslations = [...renderedTranslations, {'languageCode' : key, 'tags' : []}]
        setRenderedTranslations(newRenderedTranslations);
        key = 'tags_' + key; // LC must have a prefix "tags_"
        
        // Make changes to the parent NodeObject
        setNodeObject(prevState => {
            const newNodeObject = {...prevState};
            newNodeObject[key] = [];
            return newNodeObject
        })
        setOpen(false);
    }

    // Used for deleting a translation language
    function handleDeleteTranslation(key) {
        const newRenderedTranslations = renderedTranslations.filter(obj => !(key === obj.languageCode))
        setRenderedTranslations(newRenderedTranslations);
        key = 'tags_' + key; // LC must have a prefix "tags_"
        
        // Make changes to the parent NodeObject
        setNodeObject(prevState => {
            const newNodeObject = {...prevState};
            delete newNodeObject[key];
            return newNodeObject
        })
        setOpen(false);
    }

    // Changes the translations to be rendered
    // Dependent on changes occuring in "originalNodeObject"
    useEffect(() => {

        // Main langauge tags are considered separately, since they have to be rendered first
        let mainLangTags = []
        let otherLangTags = []

        Object.keys(originalNodeObject).forEach((key) => {
        
            // Get all tags and its corresponding language code
            // Tagids need to be recomputed, so shouldn't be rendered
            // Eg: tags_fr
        
            if (key.startsWith('tags') && !key.includes('ids')) {

                // If tags are not for the main language, add them to otherLangTags
                if (!key.endsWith(originalNodeObject.main_language)) {

                    // Slice the language code
                    let languageCode = key.slice(-2);
                    let tobeInsertedObj = {'languageCode' : languageCode, 'tags' : []} // General format for storing tags for different lc's
                    originalNodeObject[key].map((tag) => (
                        tobeInsertedObj['tags'].push({
                            'index' : uuid.v4(), // Give a unique identifier for each tag
                            'tag' : tag
                        })
                    ))
                    otherLangTags.push(tobeInsertedObj);
                }
                // If tags are for main language, add them to mainLangTags
                else {
                    originalNodeObject["tags_"+originalNodeObject['main_language']].map((tag) => (
                        mainLangTags.push({ 
                            'index' : uuid.v4(),
                            'tag' : tag
                        })
                    ))
                }
            }
        })

        // Set states
        setMainLang_renderedTranslations(mainLangTags);
        setRenderedTranslations(otherLangTags);
    }, [originalNodeObject]);

    // Helper function used for changing state
    function changeData(key, index, value) {
        let updatedTags = [] // Stores all the tags of a language code

        if (key === nodeObject['main_language']) {
            // Update state in correct format after duplication
            const updatedObj = {'index' : index, 'tag' : value}
            updatedTags =  mainLang_renderedTranslations.map(el => (el.index === index) ? updatedObj : el)
            setMainLang_renderedTranslations(updatedTags);
        }

        else {
            let duplicateOtherTags = []; // Stores the updated state for "renderedTranslations"
            const updatedObj = {'index' : index, 'tag' : value}
            renderedTranslations.forEach((allTagsObj) => {

                // Check if update LC and current element LC are same
                // If LC is same, the element's tags needs to be updated
                if (allTagsObj['languageCode'] === key) {
                    const newTags = allTagsObj['tags'].map(el => (el.index === index) ? updatedObj : el)

                    // Append according to format used in "renderedTranslations"
                    duplicateOtherTags.push({
                        'languageCode' : key,
                        'tags' : newTags
                    })
                    updatedTags = [...newTags] // Assign to updatedTags for later use
                }
                // If LC is not the same, element doesn't require any changes
                else {
                    duplicateOtherTags.push(allTagsObj)
                }
            })
            // Set state
            setRenderedTranslations(duplicateOtherTags)
        }

        let tagsToBeInserted = updatedTags.map(el => (el.tag)) // Removes unique idenitifer from each tag

        key = 'tags_' + key; // LC must have a prefix "tags_"

        // Make changes to the parent NodeObject
        setNodeObject(prevState => {
            const newNodeObject = {...prevState};
            newNodeObject[key] = tagsToBeInserted;
            return newNodeObject 
        })
    }

    // Helper function for adding a translation for a LC
    function handleAdd(key) {
        let tagsToBeInserted = []
        // State of "MainLang_renderedTranslations" is updated according to format used
        if (key === nodeObject.main_language) {
            const duplicateMainLang_renderedTranslations = [...mainLang_renderedTranslations, {'index': uuid.v4(), 'tag' : ''}];
            setMainLang_renderedTranslations(duplicateMainLang_renderedTranslations); // Set state

            // Updated tags assigned for later use
            tagsToBeInserted = duplicateMainLang_renderedTranslations.map(el => (el.tag))
        }
        // State of "renderedTranslations" is updated according to format used
        else {
            const newRenderedTranslations = [...renderedTranslations];
            newRenderedTranslations.map((allTagsObj) => (allTagsObj['languageCode'] === key) ? 
                (
                    allTagsObj['tags'].push({'index': uuid.v4(), 'tag' : ''}),
                    // Updated tags assigned for later use
                    tagsToBeInserted = allTagsObj['tags'].map(el => (el.tag))
                ) : allTagsObj
            )
            setRenderedTranslations(newRenderedTranslations) // Set state

        }
        // Set state of main NodeObject
        setNodeObject(prevState => {
            const newNodeObject = {...prevState};
            newNodeObject['tags_'+key] = tagsToBeInserted;
            return newNodeObject
        })
    }

    function handleDelete(key, index) {
        let tagsToBeInserted = []
        // State of "MainLang_renderedTranslations" is updated according to format used
        if (key === nodeObject.main_language) {
            const duplicateMainLang_renderedTranslations = mainLang_renderedTranslations.filter(obj => !(index === obj.index))
            setMainLang_renderedTranslations(duplicateMainLang_renderedTranslations); // Set state

            // Updated tags assigned for later use
            tagsToBeInserted = duplicateMainLang_renderedTranslations.map(el => (el.tag))
        }
        // State of "renderedTranslations" is updated according to format used
        else {
            let newRenderedTranslations = []
            renderedTranslations.forEach((allTagsObj) => {
                if (allTagsObj['languageCode'] === key) {
                    const unDeletedTags = allTagsObj['tags'].filter((tagObj) => !(tagObj.index === index));
                    newRenderedTranslations.push({
                        'languageCode' : key,
                        'tags' : unDeletedTags
                    })
                    // Updated tags assigned for later use
                    tagsToBeInserted = [...unDeletedTags].map(el => (el.tag));
                }
                else {
                    newRenderedTranslations.push(allTagsObj)
                }
            })
            setRenderedTranslations(newRenderedTranslations) // Set state
        }
        // Set state of main NodeObject
        setNodeObject(prevState => {
            const newNodeObject = {...prevState};
            newNodeObject['tags_'+key] = tagsToBeInserted;
            return newNodeObject
        })
    }

    return ( 
        <Box sx={{ml: 4}}>
            {/* Title */}
            <Stack direction="row" alignItems="center">
                <Typography sx={{mt: 4, mb: 1}} variant='h5'>Translations</Typography>
                <IconButton sx={{mt: 3.5, ml: 1, color: "#808080"}} onClick={handleOpen}>
                    <AddBoxIcon />
                </IconButton>
            </Stack>

            {/* Main Language */}
            <Stack direction="row" alignItems="center">
                <Typography variant='h6'>
                    { nodeObject && ISO6391.getName(nodeObject.main_language) }
                </Typography>
                <IconButton sx={{ml: 1, color: "#808080"}} onClick={() => handleAdd(nodeObject.main_language)}>
                    <AddBoxIcon />
                </IconButton>
            </Stack>
            
            {/* Render main language tags */}
            <Typography variant='h6'> 
                { nodeObject && 
                    mainLang_renderedTranslations.map(({index, tag}) => {
                        return (
                            <Stack key={index} direction="row" alignItems="center">
                                <Paper component={Stack} direction="column" sx={{ml: 4, width: 200}}>
                                    <TextField 
                                        size="small" 
                                        sx={{mt: 1}} 
                                        onChange = {event => {
                                            changeData(nodeObject['main_language'], index, event.target.value)
                                        }}
                                        value={tag}
                                        variant="outlined" />  
                                </Paper>
                                    <IconButton sx={{ml: 1, mt: 1, color: "#808080"}} onClick={() => handleDelete(nodeObject.main_language, index)}>
                                        <DeleteOutlineIcon />
                                    </IconButton>
                            </Stack>
                        )
                    })
                }
            </Typography>

            {/* All other languages */}
            {
                renderedTranslations.map( (allTagsObj) => {
                    const lang = allTagsObj['languageCode']
                    const value = allTagsObj['tags']
                    return (
                        <Box key={lang}>
                            <Stack sx={{mt: 2}} direction="row" alignItems="center">
                                <Typography variant="h6">
                                    {ISO6391.getName(lang)}
                                </Typography>
                                <IconButton sx={{ml: 1, color: "#808080"}} onClick={() => handleAdd(lang)}>
                                    <AddBoxIcon />
                                </IconButton>
                                <IconButton sx={{ml: -1, color: "#808080"}} onClick={() => handleDeleteTranslation(lang)}>
                                    <DeleteOutlineIcon />
                                </IconButton>
                            </Stack>
                            {/* Render all related tags */}
                            {
                                value.map((tagObj) => {
                                    const index = tagObj['index']
                                    const tag = tagObj['tag']
                                    return (
                                        <Stack key={index} direction="row" alignItems="center">
                                            <Paper component={Stack} direction="column" sx={{ml: 4, width: 200}}>
                                                <TextField 
                                                    size="small" 
                                                    sx={{mt: 1}} 
                                                    onChange = {event => {
                                                        changeData(lang, index, event.target.value)
                                                    }}
                                                    value={tag} 
                                                    variant="outlined" />
                                            </Paper>
                                            <IconButton sx={{ml: 1, mt: 1, color: "#808080"}} onClick={() => handleDelete(lang, index)}>
                                                 <DeleteOutlineIcon />
                                            </IconButton>
                                        </Stack>
                                    )
                                })
                            }
                        </Box>
                    )
                } )
            }
            {/* Dialog box for adding translations */}
            <Dialog open={open} onClose={handleClose}>
                <DialogTitle>Add a language</DialogTitle>
                <DialogContent>
                <DialogContentText>
                    Enter the two letter language code for the language to be added.
                </DialogContentText>
                <TextField
                    autoFocus
                    margin="dense"
                    onKeyPress={(e) => { (e.key === 'Enter') && isValidLanguageCode && handleAddTranslation(newLanguageCode, e) }} 
                    onChange={(e) => { 
                        setNewLanguageCode(e.target.value);
                        const validateBool = ISO6391.validate(e.target.value);
                        const ifDuplicateBool = renderedTranslations.some(el => (el.languageCode === e.target.value)) || 
                                                nodeObject.main_language === e.target.value
                        validateBool && !ifDuplicateBool ? setisValidLanguageCode(true) : setisValidLanguageCode(false)
                        validateBool && !ifDuplicateBool ? setBtnDisabled(false) : setBtnDisabled(true)
                    }}
                    helperText={!isValidLanguageCode ? "Enter a correct language code!" : ""}
                    error={!isValidLanguageCode}
                    fullWidth
                    variant="standard"
                />
                </DialogContent>
                <DialogActions>
                <Button onClick={handleClose}>Cancel</Button>
                <Button 
                    disabled={btnDisabled}
                    onClick={() => {handleAddTranslation(newLanguageCode)}}>
                        Add
                </Button>
                </DialogActions>
            </Dialog>
        </Box>
     );
}
 
export default ListTranslations;