import useFetch from "../../components/useFetch";
import { API_URL } from "../../constants";
import EntriesList from "./EntriesList";

const Entry = () => {
    const { data: nodes, isPending, isError, isSuccess, errorMessage } = useFetch(API_URL+'nodes');
    if (isError) {
        return (
            <div className="all-entries">
                {isError && <div>{errorMessage}</div>}
            </div>
        )
    }
    return (
        <div className="all-entries">
            {isPending && <div>Loading...</div>}
            {isSuccess && <EntriesList nodes={nodes} title={"Test"}/>}
        </div>
    );
}
 
export default Entry;