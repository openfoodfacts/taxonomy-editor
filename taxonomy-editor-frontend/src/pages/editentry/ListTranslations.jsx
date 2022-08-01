import { Typography, Paper, TextField, Stack } from "@mui/material";
import { useState } from "react";

const ListTranslations = ({ nodeObject, languageNames }) => {
    let toBeRendered = {}
    Object.keys(nodeObject).forEach((key) => {
        if (key.startsWith('tags') && 
            !key.endsWith(nodeObject.main_language) && 
            !key.includes('ids')) {
                let lc = key.slice(-2);
                toBeRendered[lc] = nodeObject[key]
            }
    })

    // Add main language before setting it as state variable
    let duplicateToBeRendered = {...toBeRendered};
    duplicateToBeRendered[nodeObject.main_language] = nodeObject["tags_"+nodeObject['main_language']];
    const [changedObj, setChangedObj] = useState(duplicateToBeRendered);

    // Helper function used for changing state
    function changeData(key, index, obj) {
        const duplicateData = {...changedObj};
        duplicateData[key][index] = obj;
        setChangedObj(duplicateData);
    }

    return ( 
        <div className="translations">
            <Typography variant='h6'>
                { nodeObject && languageNames.of(nodeObject.main_language) }
            </Typography>
            <Typography variant='h6'> 
                { nodeObject && 
                    nodeObject["tags_"+nodeObject['main_language']].map((tag, index) => {
                        return (
                            <Paper key={index} component={Stack} direction="column" sx={{ml: 4, width: 200}}>
                                <TextField 
                                    size="small" 
                                    sx={{mt: 1}} 
                                    onChange = {event => {
                                        changeData(nodeObject['main_language'], index, event.target.value)
                                    }}
                                    defaultValue={tag} 
                                    variant="outlined" />
                            </Paper>
                        )
                    })
                }
            </Typography>
            {
                Object.entries(toBeRendered).map( ([lang, value]) => {
                    return (
                        <div key={lang} className="translation-component">
                            <Typography sx={{mt:1}} variant="h6">
                                {languageNames.of(lang)}
                            </Typography>
                            {
                                value.map((tag, index) => {
                                    return (
                                        <Paper key={index} component={Stack} direction="column" sx={{ml: 4, width: 200}}>
                                            <TextField 
                                                size="small" 
                                                sx={{mt: 1}} 
                                                onChange = {event => {
                                                    changeData(lang, index, event.target.value)
                                                }}
                                                defaultValue={tag} 
                                                variant="outlined" />
                                        </Paper>
                                    )
                                })
                            }
                        </div>
                    )
                } )
            }
        </div>
     );
}
 
export default ListTranslations;