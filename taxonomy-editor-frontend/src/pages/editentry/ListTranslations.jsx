import { Typography, TextField, Stack, Button, IconButton, Box, Autocomplete } from "@mui/material";
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import { useEffect, useState } from "react";
import AddBoxIcon from '@mui/icons-material/AddBox';
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';
import ISO6391 from 'iso-639-1';

/**
 * Sub-component for rendering translation of an "entry"
*/
const ListTranslations = ({ nodeObject, setNodeObject }) => {

    const [renderedTranslations, setRenderedTranslations] = useState([]) // Stores state of all tags
    const [mainLangRenderedTranslations, setMainLangRenderedTranslations] = useState([]) // Stores state of main language's tags
    const [openDialog, setOpen] = useState(false); // Used for Dialog component
    const [newLanguageCode, setNewLanguageCode] = useState(''); // Used for storing new LC from Dialog
    const [languageAction, setLanguageAction] = useState('invalid'); // Used for storing state of action to be performed on LC (add/show/invalid)
    const [shownTranslationLanguages, setShownTranslationLanguages] = useState([]); // Used for storing LC's that are to be shown
    const [addedLanguageCodes, setAddedLanguageCodes] = useState([]); // Used for storing LC's that are added to the nodeObject

    // Helper functions for Dialog component
    const handleClose = () => { setOpen(false); }
    const handleOpen = () => { setOpen(true); }

    // Used for addition of a translation language
    const handleAddTranslation = (key) => {
        const newRenderedTranslations = [...renderedTranslations, {'languageCode' : key, 'tags' : []}]
        if (!shownTranslationLanguages.includes(key)) {
            handleToggleTranslationVisibility(key)
        }
        setLanguageAction('invalid')
        setRenderedTranslations(newRenderedTranslations);
        key = 'tags_' + key; // LC must have a prefix "tags_"
        const uuidKey = key + '_uuid' // Format for the uuid

        // Make changes to the parent NodeObject
        setNodeObject(prevState => {
            const newNodeObject = {...prevState};
            newNodeObject[key] = [];
            newNodeObject[uuidKey] = [Math.random().toString()];
            return newNodeObject
        })
        setOpen(false);
    }

    // Used for deleting a translation language
    const handleDeleteTranslation = (key) => {
        const newRenderedTranslations = renderedTranslations.filter(obj => !(key === obj.languageCode))
        setRenderedTranslations(newRenderedTranslations);
        key = 'tags_' + key; // LC must have a prefix "tags_"
        const uuidKey = key + '_uuid' // Format for the uuid
        
        // Make changes to the parent NodeObject
        setNodeObject(prevState => {
            const newNodeObject = {...prevState};
            delete newNodeObject[key];
            delete newNodeObject[uuidKey];
            return newNodeObject
        })
        setOpen(false);
    }

    // Used for toggling visibility of a translation language
    const handleToggleTranslationVisibility = (key) => {
        const newShownTranslationLanguages = shownTranslationLanguages.includes(key) ? shownTranslationLanguages.filter(obj => !(key === obj)) : [...shownTranslationLanguages, key]
        setShownTranslationLanguages(newShownTranslationLanguages);
        localStorage.setItem('shownTranslationLanguages', JSON.stringify(newShownTranslationLanguages))
        setOpen(false);
    }

    // Changes the translations to be rendered
    // Dependent on changes occuring in "nodeObject"
    useEffect(() => {
        // Main langauge tags are considered separately, since they have to be rendered first
        const mainLangTags = []
        const otherLangTags = []
        const addedLanguageCodes = []
        Object.keys(nodeObject).forEach((key) => {
        
            // Get all tags and its corresponding language code
            // Tagids need to be recomputed, so shouldn't be rendered
            // Eg: tags_fr
        
            if (key.startsWith('tags') && !key.includes('ids') && !key.includes('str')) {
                if (key.endsWith('uuid')) {
                    const uuids = nodeObject[key]
                    // If tags are for main language, add them to mainLangTags
                    if (key.includes(nodeObject.main_language)) {
                        nodeObject["tags_"+nodeObject['main_language']].forEach((tag, index) => (
                            mainLangTags.push({ 
                                'index' : uuids[index],
                                'tag' : tag
                            })
                        ))
                    }
                    
                    // If tags are not for the main language, add them to otherLangTags
                    else {
                        // Slice the language code
                        const languageCode = key.split('_').slice(1,-1)[0]
                        addedLanguageCodes.push(languageCode)
                        // General format for storing tags for different lc's
                        const tobeInsertedObj = {'languageCode' : languageCode, 'tags' : []}
                        const tagsKey = key.split('_').slice(0,-1).join('_')
                        nodeObject[tagsKey].forEach((tag, index) => (
                            tobeInsertedObj['tags'].push({
                                'index' : uuids[index], // Give a unique identifier for each tag
                                'tag' : tag
                            })
                        ))
                        otherLangTags.push(tobeInsertedObj);
                    }
                }
            }
        })

        // Set states
        setAddedLanguageCodes(addedLanguageCodes);
        setMainLangRenderedTranslations(mainLangTags);
        setRenderedTranslations(otherLangTags);
    }, [nodeObject, shownTranslationLanguages]);

    useEffect(() => {
        // get shown translation languages from local storage
        const shownTranslationLanguages = JSON.parse(localStorage.getItem('shownTranslationLanguages')) || [];
        setShownTranslationLanguages(shownTranslationLanguages);
    }, [])

    // Helper function used for changing state
    const changeData = (key, index, value) => {
        let updatedTags = [] // Stores all the tags of a language code

        if (key === nodeObject['main_language']) {
            // Update state in correct format after duplication
            const updatedObj = {'index' : index, 'tag' : value}
            updatedTags =  mainLangRenderedTranslations.map(el => (el.index === index) ? updatedObj : el)
            setMainLangRenderedTranslations(updatedTags);
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
    const handleAdd = (key) => {
        let tagsToBeInserted = [];
        const newUUID = Math.random().toString();
        // State of "MainLangRenderedTranslations" is updated according to format used
        if (key === nodeObject.main_language) {
            const duplicateMainLangRenderedTranslations = [...mainLangRenderedTranslations, {'index': newUUID, 'tag' : ''}];
            setMainLangRenderedTranslations(duplicateMainLangRenderedTranslations); // Set state

            // Updated tags assigned for later use
            tagsToBeInserted = duplicateMainLangRenderedTranslations.map(el => (el.tag))
        }
        // State of "renderedTranslations" is updated according to format used
        else {
            const newRenderedTranslations = [...renderedTranslations];
            newRenderedTranslations.map((allTagsObj) => (allTagsObj['languageCode'] === key) ? 
                (
                    allTagsObj['tags'].push({'index': newUUID, 'tag' : ''}),
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
            newNodeObject['tags_'+key+'_uuid'].push(newUUID);
            return newNodeObject
        })
    }

    const handleDelete = (key, index) => {
        let tagsToBeInserted = []
        // State of "MainLangRenderedTranslations" is updated according to format used
        if (key === nodeObject.main_language) {
            const duplicateMainLangRenderedTranslations = mainLangRenderedTranslations.filter(obj => !(index === obj.index))
            setMainLangRenderedTranslations(duplicateMainLangRenderedTranslations); // Set state

            // Updated tags assigned for later use
            tagsToBeInserted = duplicateMainLangRenderedTranslations.map(el => (el.tag))
        }
        // State of "renderedTranslations" is updated according to format used
        else {
            const newRenderedTranslations = []
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
            newNodeObject['tags_'+key+'_uuid'] = newNodeObject['tags_'+key+'_uuid'].filter(currIndex => !(currIndex === index)) 
            return newNodeObject
        })
    }

    return (
        <Box sx={{ml: 4}}>
            {/* Title */}
            <Stack direction="row" alignItems="center">
                <Typography sx={{mt: 4, mb: 1}} variant='h5'>Translations</Typography>
            </Stack>

            {/* Main Language */}
            <Stack direction="row" alignItems="center">
                <Typography variant='h6'>
                    { nodeObject && ISO6391.getName(nodeObject.main_language) }
                </Typography>
                <IconButton sx={{ml: 1}} onClick={() => handleAdd(nodeObject.main_language)}>
                    <AddBoxIcon />
                </IconButton>
            </Stack>
            
            {/* Render main language tags */}
            { nodeObject && 
                mainLangRenderedTranslations.map(({index, tag}) => {
                    return (
                        <Stack sx={{ml: 2}} key={index} direction="row" alignItems="center">
                            <TextField
                                size="small" 
                                sx={{mt: 1}} 
                                onChange = {event => {
                                    changeData(nodeObject['main_language'], index, event.target.value)
                                }}
                                value={tag}
                                variant="outlined" />  
                        
                            <IconButton sx={{ml: 1, mt: 1}} onClick={() => handleDelete(nodeObject.main_language, index)}>
                                <DeleteOutlineIcon />
                            </IconButton>
                        </Stack>
                    )
                })
            }

            {/* All other languages */}
            {
                renderedTranslations.map( (allTagsObj) => {
                    const lang = allTagsObj['languageCode']
                    const tagValue = allTagsObj['tags']
                    return (
                        shownTranslationLanguages.includes(lang) &&
                        <Box key={lang}>
                            <Stack sx={{mt: 2}} direction="row" alignItems="center">
                                <Typography variant="h6">
                                    {ISO6391.getName(lang)}
                                </Typography>
                                <IconButton sx={{ml: 1}} onClick={() => handleAdd(lang)}>
                                    <AddBoxIcon />
                                </IconButton>
                                <IconButton onClick={() => handleDeleteTranslation(lang)}>
                                    <DeleteOutlineIcon />
                                </IconButton>
                                <IconButton onClick={() => handleToggleTranslationVisibility(lang)}>
                                    <VisibilityOffIcon />
                                </IconButton>
                            </Stack>
                            {/* Render all related tags */}
                            {
                                tagValue.map((tagObj) => {
                                    const index = tagObj['index']
                                    const tag = tagObj['tag']
                                    return (
                                        <Stack key={index} sx={{ml: 2}} direction="row" alignItems="center">
                                            <TextField 
                                                size="small" 
                                                sx={{mt: 1}} 
                                                onChange = {event => {
                                                    changeData(lang, index, event.target.value)
                                                }}
                                                value={tag} 
                                                variant="outlined" />
                                            <IconButton sx={{ml: 1, mt: 1}} onClick={() => handleDelete(lang, index)}>
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
            {/* Button to add language to the list of shown languages or show the language if it already exists */}
            <Button sx={{mt: 2}} onClick={handleOpen}>
                Add/Show More Languages 
                ({
                    addedLanguageCodes.length - 
                    addedLanguageCodes.filter(element => new Set(shownTranslationLanguages).has(element)).length
                } Hidden)
            </Button>
            {/* Dialog box for adding languages to the list of shown languages */}
            <Dialog open={openDialog} onClose={handleClose}>
                <DialogTitle>Add or Show another language</DialogTitle>
                <DialogContent>
                <DialogContentText>
                    Enter the two letter language code for the language to be shown or added.
                </DialogContentText>
                <Autocomplete
                    sx={{mt: 2}}
                    options={ISO6391.getAllNames()}
                    onChange={(e,language) => {
                        if (!language) language = '';
                        setNewLanguageCode(ISO6391.getCode(language));
                        const isValidLanguage = ISO6391.validate(ISO6391.getCode(language))
                        const isAlreadyShown = shownTranslationLanguages.includes(ISO6391.getCode(language))
                        const isDuplicateLanguage = renderedTranslations.some(el => (el.languageCode === ISO6391.getCode(language))) || 
                                                nodeObject.main_language === ISO6391.getCode(language)
                        if (isValidLanguage  && !isDuplicateLanguage) {setLanguageAction("add")}
                        else if (isValidLanguage && !isAlreadyShown && isDuplicateLanguage) {setLanguageAction("show")}
                        else {setLanguageAction("invalid")}
                    }}
                    renderOption={(props, option) => {
                        const languageCode = ISO6391.getCode(option)
                        const isAlreadyShown = addedLanguageCodes.includes(languageCode)
                        // set color of text to green if the language is already shown
                        return (
                            <span {...props} style={{ color: isAlreadyShown ? 'green' : 'black' }}>
                                {option}
                            </span>
                        )
                    }}
                    renderInput={(params) =>
                        <TextField
                            error={languageAction === "invalid"} {...params} label="Languages"
                        />}
                />
                </DialogContent>
                <DialogActions>
                <Button onClick={handleClose}>Cancel</Button>
                { languageAction !== "invalid" && 
                    <Button
                        onClick={() => {languageAction === "add" ? handleAddTranslation(newLanguageCode) : handleToggleTranslationVisibility(newLanguageCode)}}>
                            {languageAction === "add" ? "Add" : "Show" }
                    </Button>
                }
                </DialogActions>
            </Dialog>
        </Box>
     );
}
 
export default ListTranslations;