import { useEffect, useReducer } from "react";

const initialState = {
  status: "pending",
  data: null,
  errorMessage: "",
};

const reducer = (state, action) => {
  switch (action.type) {
    case "fetching":
      return initialState;
    case "success":
      return {
        status: "success",
        data: action.data,
        errorMessage: "",
      };
    case "error":
      return {
        status: "error",
        data: null,
        errorMessage: action.errorMessage,
      };
    default:
      return state;
  }
};

const useFetch = (url) => {
  const [fetchInfo, dispatch] = useReducer(reducer, initialState);
  useEffect(() => {
    const abortCont = new AbortController();

    dispatch({ type: "fetching" });

    fetch(url, { signal: abortCont.signal })
      .then((res) => {
        if (!res.ok) {
          throw Error("Could not fetch the data for resource!");
        }
        return res.json();
      })
      .then((data) => {
        dispatch({ type: "success", data: data });
      })
      .catch((err) => {
        if (err.name === "AbortError") {
          // Do nothing
        } else {
          dispatch({ type: "error", errorMessage: err.message ?? "" });
        }
      });
    return () => abortCont.abort();
  }, [url]);

  const isPending = fetchInfo.status === "pending";
  const isError = fetchInfo.status === "error";
  const isSuccess = fetchInfo.status === "success";

  return {
    data: fetchInfo.data,
    isPending,
    isError,
    isSuccess,
    errorMessage: fetchInfo.errorMessage,
  };
};

export default useFetch;
