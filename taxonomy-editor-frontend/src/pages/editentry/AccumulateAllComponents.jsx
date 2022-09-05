import { Box } from "@mui/material";
import { useEffect, useState } from "react";
import useFetch from "../../components/useFetch";
import { createURL, getIdType } from "./createURL";
import ListAllNonEntryInfo from "./ListAllNonEntryInfo";
import ListAllEntryProperties from "./ListAllEntryProperties";
import ListTranslations from "./ListTranslations";
import FetchRelations from "./FetchAndDisplayRelations";

/**
 * Component used for rendering node information
 * If node is an "entry": Relations, translations, comments and properties are rendered
 * If node is an "stopword/synonym": Stopwords/synonyms, language and comments are rendered
 * If node is "header/footer": Comments are rendered  
*/ 
const AccumulateAllComponents = ({ id }) => {
    const url = createURL(id);
    const isEntry = getIdType(id) === 'entry';
    const [nodeObject, setNodeObject] = useState(null); // Storing node information
    const { data: node, isPending, isError, isSuccess, errorMessage } = useFetch(url);

    // Setting state of node after fetch
    useEffect(() => {
        setNodeObject(node?.[0]);
    }, [node])

    if (isError) {
        return (
            <Box>{isError && <div>{errorMessage}</div>}</Box>
        )
    }
    if (isPending) {
        return (
            <Box>{isPending && <div>Loading...</div>}</Box>
        )
    }
    return ( 
        <Box className="node-attributes">
            {/* Based on isEntry, respective components are rendered */}
            { isEntry ? 
                <Box>
                    { !!nodeObject &&
                        <>  <FetchRelations url={url+'parents'} title={'Parents'} />
                            <FetchRelations url={url+'children'} title={'Children'} />
                            <ListTranslations nodeObject={nodeObject} setNodeObject={setNodeObject} /> 
                            <ListAllEntryProperties nodeObject={nodeObject} setNodeObject={setNodeObject} /> </> }
                </Box> :
                <>  <ListAllNonEntryInfo nodeObject={nodeObject} id={id} setNodeObject={setNodeObject} /> </>
            }
        </Box>
     );
}

export default AccumulateAllComponents;