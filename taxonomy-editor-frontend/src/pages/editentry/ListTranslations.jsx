import { Typography, Paper, TextField, Stack } from "@mui/material";

const ListTranslations = ({ nodeObject, languageNames, setNodeObject }) => {
    let toBeRendered = {}
    Object.keys(nodeObject).forEach((key) => {
        if (key.startsWith('tags') && 
            !key.endsWith(nodeObject.main_language) && 
            !key.includes('ids')) {
                let lc = key.slice(-2);
                toBeRendered[lc] = nodeObject[key]
            }
    })

    // Helper function used for changing state
    function changeData(key, index, value) {
        key = 'tags_' + key;
        const duplicateData = {...nodeObject};
        duplicateData[key][index] = value;
        setNodeObject(duplicateData);
    }

    return ( 
        <div className="translations">
            <Typography sx={{mt: 4, mb: 1}} variant='h5' component={'div'}>Translations</Typography>
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