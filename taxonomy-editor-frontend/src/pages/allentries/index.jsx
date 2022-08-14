import useFetch from "../../components/useFetch";
import { API_URL } from "../../constants";
import EntriesList from "./EntriesList";

const Entry = () => {
    const {data: nodes, isPending, error} = useFetch(API_URL+'nodes');
    if (error) {
        return (
            <div className="all-entries">
                {error && <div>{error}</div>}
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