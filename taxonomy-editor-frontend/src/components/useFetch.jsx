import { useState, useEffect } from "react";

const useFetch = (url) => {    
    const [data, setData] = useState(null)
    const [isPending, setIsPending] = useState(true)
    const [errorMessage, setErrorMessage] = useState(null);

    useEffect(() => {
        const abortCont = new AbortController();
        fetch(url, {signal: abortCont.signal})
            .then(res => { 
                if (!res.ok) {
                    throw Error("Could not fetch the data for resource!")
                }
                return res.json();
            })
            .then(data => {
                setData(data);
                setIsPending(false);
                setErrorMessage(null);
            })
            .catch(err => {
                if (err.name === 'AbortError') {
                    // Occurs when hook aborts
                    // Don't need to handle separately
                } else {
                    setIsPending(false);
                    setErrorMessage(err.message);
                }
            })
        return () => abortCont.abort();
      }, [url]);
    return { data, isPending, errorMessage }
}

export default useFetch;