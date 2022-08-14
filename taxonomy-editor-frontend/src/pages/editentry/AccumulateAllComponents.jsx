import { useEffect, useState } from "react";
import useFetch from "../../components/useFetch";
import { API_URL } from "../../constants";
import ListAllEntryProperties from "./ListAllEntryProperties";
import ListAllOtherProperties from "./ListAllOtherProperties";

// Used for rendering node information
// If node is an "entry": Relations, translations, comments and properties are rendered
// If node is an "stopword/synonym": Stopwords/synonyms, language and comments are rendered
// If node is "header/footer": Comments are rendered

const AccumulateAllComponents = ({ id }) => {
    
    // Finding URL to send requests
    let url = API_URL;
    let isEntry = false;
    if (id.startsWith('__header__')) { url += 'header/' }
    else if (id.startsWith('__footer__')) { url += 'footer/' }
    else if (id.startsWith('synonym')) { url += `synonym/${id}/` }
    else if (id.startsWith('stopword')) { url += `stopword/${id}/` }
    else { url += `entry/${id}/`; isEntry = true; }

    const [nodeObject, setNodeObject] = useState(null); // Storing node information
    const { data: node, error, isPending } = useFetch(url);

    // Setting state of node after fetch
    useEffect(() => {
        setNodeObject(node?.[0]);
    }, [node])

    // Displaying errors if any
    if (error) {
        return (<div>{error}</div>)
    }
    
    return ( 
        <div className="node-attributes">
            {/* Based on isEntry, respective components are rendered */}
            { isEntry ? 
                <>  <ListAllEntryProperties nodeObject={nodeObject} setNodeObject={setNodeObject} /> </> :
                <>  <ListAllOtherProperties nodeObject={nodeObject} id={id} setNodeObject={setNodeObject} /> </>
            }
        </div>
     );
}
 
export default AccumulateAllComponents;