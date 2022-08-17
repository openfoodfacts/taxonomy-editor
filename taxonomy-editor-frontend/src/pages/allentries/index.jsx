import useFetch from "../../components/useFetch";
import { API_URL } from "../../constants";
import EntriesList from "./EntriesList";

const Entry = () => {
    const {data: nodes, isPending, errorMessage} = useFetch(API_URL+'nodes');
    if (errorMessage) {
        return (
            <div className="all-entries">
                {errorMessage && <div>{errorMessage}</div>}
            </div>
        )
    }
    return (
        <div className="all-entries">
            {isPending && <div>Loading...</div>}
            {nodes && <EntriesList nodes={nodes} title={"Test"}/>}
        </div>
    );
}
 
export default Entry;