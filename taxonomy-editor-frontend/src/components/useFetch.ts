import { useEffect, useReducer, Reducer } from "react";

type ReducerStateType<DataType> = {
  status: "pending" | "success" | "fetching" | "error";
  data: DataType | null;
  errorMessage: string;
};

const initialState: ReducerStateType<null> = {
  status: "pending",
  data: null,
  errorMessage: "",
};

type ActionsType<DataType> =
  | {
      type: "fetching";
    }
  | {
      type: "success";
      data: DataType;
    }
  | {
      type: "error";
      errorMessage: string;
    };

const reducer = <DataType>(
  state: ReducerStateType<DataType>,
  action: ActionsType<DataType>
): ReducerStateType<DataType> => {
  switch (action.type) {
    case "fetching":
      return { ...initialState };
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

type ReturnedType<DataType> = {
  data: DataType | null;
  isPending: boolean;
  isError: boolean;
  isSuccess: boolean;
  errorMessage: string | null;
};

const useFetch = <DataType>(url: string): ReturnedType<DataType> => {
  const [fetchInfo, dispatch] = useReducer<
    Reducer<ReducerStateType<DataType | null>, ActionsType<DataType>>
  >(reducer, initialState);

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
