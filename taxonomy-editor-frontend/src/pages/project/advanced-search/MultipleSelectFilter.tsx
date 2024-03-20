import {
    FormControl,
    OutlinedInput,
    Checkbox,
    Select,
    MenuItem,
    InputLabel,
    ListItemText,
  } from "@mui/material";
import { Dispatch, SetStateAction } from "react";

type MultipleSelectFilterType = {
    label: string,
    filterValue : string[],
    listOfChoices: string[],
    mapCodeToValue: (code: string) => string,
    mapValueToCode: (value: string) => string,
    setQ: Dispatch<SetStateAction<string>>,
    keySearchTerm: string,
}

export const MultipleSelectFilter = ({label, filterValue,listOfChoices,mapCodeToValue=()=>"",mapValueToCode=()=>"", setQ, keySearchTerm}:MultipleSelectFilterType) => {
    return (
        <FormControl sx={{ m: 1 }}>
            <InputLabel id="multiple-select-label">{label}</InputLabel>
            <Select
                id="languages-filter"
                sx={{ width: '170px' }}
                multiple
                value={filterValue}
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
                        onChange={(event) => {
                            if (!filterValue.includes(languageCodeItem)) {
                                setQ((prevQ) => prevQ + ` ${keySearchTerm}:${languageCodeItem}`);
                            } else {
                                setQ((prevQ) => prevQ.replace(`${keySearchTerm}:${languageCodeItem}`,""));
                            }
                            event.target.closest('Menu')?.dispatchEvent(new Event('close'));
                        } }

                        />
                        <ListItemText primary={languageNameItem} />
                    </MenuItem>
                    );
                })}
            </Select>
        </FormControl>
    )
}