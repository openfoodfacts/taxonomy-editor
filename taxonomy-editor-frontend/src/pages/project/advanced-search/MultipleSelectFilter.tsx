import {
    FormControl,
    OutlinedInput,
    Checkbox,
    Select,
    MenuItem,
    InputLabel,
    ListItemText,
  } from "@mui/material";
import { SetStateAction } from "react";

type MultipleSelectFilterType = {
    filterValue : string[],
    setFilterValue: (value: SetStateAction<string[]>) => void,
    listOfChoices: string[],
    mapCodeToValue: (code: string) => string,
    mapValueToCode: (value: string) => string,
}

export const MultipleSelectFilter = ({filterValue, setFilterValue,listOfChoices,mapCodeToValue=()=>"",mapValueToCode=()=>""}:MultipleSelectFilterType) => {
    return (
        <FormControl sx={{ m: 1, minWidth: 120 }}>
            <InputLabel id="demo-multiple-name-label">With languages</InputLabel>
            <Select
                id="languages-filter"
                multiple
                value={filterValue}
                onChange={
                    (event) =>{
                        console.log("chosen languages = ",event.target.value as string[])
                        setFilterValue(event.target.value as string[]) // type casting to string[] due to the `multiple` prop
                    }}
                input={<OutlinedInput label="Languages" />}
                renderValue={(selected) =>
                    selected
                        .map((langCode) => mapCodeToValue(langCode))
                        .filter(Boolean) //to ignore "xx" language
                        .join(", ")
                    }
                >
                {listOfChoices
                .sort()
                .map((languageNameItem) => {
                    const languageCodeItem = mapValueToCode(languageNameItem);
                    return (
                    <MenuItem key={languageCodeItem} value={languageCodeItem}>
                        <Checkbox
                        checked={filterValue.includes(languageCodeItem)}
                        />
                        <ListItemText primary={languageNameItem} />
                    </MenuItem>
                    );
                })}
            </Select>
        </FormControl>
    )
}