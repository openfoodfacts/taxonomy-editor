import { Box, Typography } from "@mui/material";

// Parent component used for rendering info
// on a stopword, synonym, header or footer

const ListAllOtherProperties = ({ nodeObject, id, setNodeObject }) => {

    return ( 
        <Box className="all-node-properties">
            {/* Comments */}
            <Typography sx={{ml: 4, mt: 2, mb: 1}} variant='h5'>Comments</Typography>
            
            {/* Stopwords or Synonyms */}
            <div className="tags">
                {id.startsWith('stopword') ?
                    <Typography sx={{ml: 4, mt: 1, mb: 1}} variant='h5'>
                        Stopwords
                    </Typography> :
                    <Typography sx={{ml: 4, mt: 1, mb: 1}} variant='h5'>
                        Synonyms
                    </Typography>}
            </div>
        </Box>
     );
}

export default ListAllOtherProperties;