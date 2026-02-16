stringToStringIds: dict[str, int] = {
}
stringIdsToString: dict[int, str] = {
}



def get_string_id(string: str) -> int:
    if string in stringToStringIds:
        return stringToStringIds[string]
    stringToStringIds[string] = len(stringToStringIds)
    stringIdsToString[stringToStringIds[string]] = string
    return stringToStringIds[string]


