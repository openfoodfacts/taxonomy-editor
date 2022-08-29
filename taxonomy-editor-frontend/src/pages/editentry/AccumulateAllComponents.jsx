import { Box } from "@mui/material";
import { useEffect, useState } from "react";
import useFetch from "../../components/useFetch";
import { createURL } from "./createURL";
import ListAllOtherProperties from "./ListAllOtherProperties";
import ListAllProperties from "./ListAllProperties";
import ListTranslations from "./ListTranslations";

// Used for rendering node information
// If node is an "entry": Relations, translations, comments and properties are rendered
// If node is an "stopword/synonym": Stopwords/synonyms, language and comments are rendered
// If node is "header/footer": Comments are rendered

const AccumulateAllComponents = ({ id }) => {
    const { url, isEntry } = createURL(id);
    const [nodeObject, setNodeObject] = useState(null); // Storing node information
    const { data: node, isPending, isError, isSuccess, errorMessage } = useFetch(url);

    // Setting state of node after fetch
    useEffect(() => {
        setNodeObject(node?.[0]);
    }, [node])

    if (isError) {
        return (
            <Box className="node-attributes">
                {isError && <div>{errorMessage}</div>}
            </Box>
        )
    }
    if (isPending) {
        return (
            <Box className="node-attributes">
                {isPending && <div>Loading...</div>}
            </Box>
        )
    }
    return ( 
        <Box className="node-attributes">
            {/* Based on isEntry, respective components are rendered */}
            { isEntry ? 
                <Box className="allEntryProperties">
                    { !!nodeObject &&
                        <>  <ListTranslations nodeObject={nodeObject} setNodeObject={setNodeObject} /> 
                            <ListAllProperties nodeObject={nodeObject} setNodeObject={setNodeObject} /> </> }
                </Box> :
                <>  <ListAllOtherProperties nodeObject={nodeObject} id={id} setNodeObject={setNodeObject} /> </>
            }
        </Box>
     );
}
 
export default AccumulateAllComponents;