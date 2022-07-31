import { Stack, Paper, TextField, Typography } from "@mui/material";
import { useEffect } from "react";
import { useState } from "react";

const ListProperties = ({ props }) => {
    const [nodeObject, setNodeObject] = useState(null);
    useEffect(() => {
        setNodeObject(props);
    }, [props])
    
    let languageNames = new Intl.DisplayNames(['en'], {type: 'language'});
    // if (nodeObject) {
    //     console.log(nodeObject["tags_"+nodeObject['main_language']]);
    // }
    return (
        <div className="allLanguages">
            <Typography sx={{ml: 4, mb: 1, textDecoration: 'underline'}} variant='h5' component={'div'}>Translations</Typography>
            <Typography sx={{ml: 4}} variant='h6'>
                { nodeObject && languageNames.of(nodeObject.main_language) }
            </Typography>
            <Typography sx={{ml: 4}} variant='h6'> 
                { nodeObject && 
                    nodeObject["tags_"+nodeObject['main_language']].map((tag) => {
                        return (
                            <Paper key={tag} component={Stack} direction="column" sx={{ml: 2, width: 200}}>
                                <TextField size="small" sx={{mt: 1}} defaultValue={tag} variant="outlined" />
                            </Paper>
                        )
                    })
                }
            </Typography>
            <Typography sx={{ml: 4}} variant='h6'>
                {/* TODO */}
                { nodeObject && 
                    Object.keys(nodeObject).forEach((key) => {
                        if (key.startsWith('tags') && 
                            !key.endsWith(nodeObject.main_language) && 
                            !key.includes('ids')) {
                                let lc = key.slice(-2);
                                return (
                                    <Typography variant="h6">
                                        { languageNames.of(lc) }
                                    </Typography>
                                )
                                // console.log();
                                // console.log(`${key}: ${nodeObject[key]}`);
                            }
                    })}
            </Typography>
        </div>
    );
}
 
export default ListProperties;