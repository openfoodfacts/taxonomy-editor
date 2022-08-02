import { Paper, Stack, TextField, Typography } from "@mui/material";
import { useEffect, useState } from "react";

const ListAllOtherProperties = ({ props }) => {
    const [nodeObject, setNodeObject] = useState(null);
    useEffect(() => {
        setNodeObject(props);
    }, [props])

    let lc = '';
    let toBeRendered = {}
    let languageNames = new Intl.DisplayNames(['en'], {type: 'language'});

    if (nodeObject) {
        Object.keys(nodeObject).forEach((key) => {
            if (key.startsWith('tags') && 
                !key.includes('ids')) {
                    lc = key.slice(-2);
                    toBeRendered[lc] = nodeObject[key]
                }
        })
    }

    // Helper function used for changing state of properties
    function changeDataComment(key, value) {
        const duplicateData = {...nodeObject};
        duplicateData[key] = value;
        setNodeObject(duplicateData);
    }

    function changeData(key, index, obj) {
        console.log(key, index, obj);
        const duplicateData = {...nodeObject};
        duplicateData[key][index] = obj;
        setNodeObject(duplicateData);
    }

    return ( 
        <div className="allProperties">
            <Typography sx={{ml: 4, mt: 2, mb: 1, textDecoration: 'underline'}} variant='h5'>Comments</Typography>
            { nodeObject && <TextField
                sx={{ml: 8, mt: 1}}
                size="small"
                multiline
                onChange = {event => {
                    // console.log(event.target.value);
                    changeDataComment('preceding_lines', event.target.value)
                }}
                defaultValue={nodeObject.preceding_lines} 
                variant="outlined" /> }

            { Object.keys(toBeRendered).length > 0 && 
                <div className="language">
                    <Typography sx={{ml: 4, mt: 2, textDecoration: 'underline'}} variant='h5'>
                        Language
                    </Typography>
                    <Typography sx={{ml: 8, mt: 2}} variant='h6'>
                        {languageNames.of(lc)}
                    </Typography>
                    
                </div>
                }
            
            { Object.keys(toBeRendered).length > 0 && 
                    <div className="tags">
                        {nodeObject.id.startsWith('stopword') && 
                            <Typography sx={{ml: 4, mt: 1, mb: 1, textDecoration: 'underline'}} variant='h5'>
                                Stopwords
                            </Typography>}
                        {nodeObject.id.startsWith('synonym') && 
                            <Typography sx={{ml: 4, mt: 1, mb: 1, textDecoration: 'underline'}} variant='h5'>
                                Synonyms
                            </Typography>}
                        { toBeRendered[lc].map((tag, index) => {
                            return (
                                <Paper key={index} component={Stack} direction="column" sx={{ml: 8, width: 200}}>
                                    <TextField 
                                        size="small" 
                                        sx={{mt: 1}} 
                                        onChange = {event => {
                                            changeData('tags_'+lc, index, event.target.value)
                                        }}
                                        defaultValue={tag} 
                                        variant="outlined" />
                                </Paper>
                            )})}
                    </div>
                }
        </div>
     );
}

export default ListAllOtherProperties;