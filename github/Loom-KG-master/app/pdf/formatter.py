import json
import re
import os
import shutil
import zipfile
import string


def preprocess(text):
    text = str(text).lower()
    text = str(text).strip()
    text = re.compile("<.*?>").sub("", text)
    text = re.compile("[%s]" % re.escape(string.punctuation)).sub(" ", text)
    text = re.sub("\s+", " ", text)
    text = re.sub(r"\[[0-9]*\]", " ", text)
    text = re.sub(r"[^\w\s]", "", str(text).lower().strip())
    text = re.sub(r"\d", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text


def extract_citation_number(input_string):
    citation_no = re.findall(
        r"\b\d+ ONSC \d+|\b\d+ ONCA \d+|\b\d+ ABQB \d+|\b\d+ ABCA \d+|\b\d+ BCSC \d+|\b\d+ BCCA \d+|\b\d+ SCC \d+",
        input_string,
    )

    return citation_no


def remove_unwanted_char(num):
    return num.strip().strip(")").strip("(").strip("[").strip("]").strip(".")


def is_roman_number(num):
    num = remove_unwanted_char(num).upper()
    pattern = re.compile(
        r"""   
                                ^M{0,3}
                                (CM|CD|D?C{0,3})?
                                (XC|XL|L?X{0,3})?
                                (IX|IV|V?I{0,3})?$
                """,
        re.VERBOSE,
    )

    if re.match(pattern, num):
        return True
    return False


def clean_string(string):
    final_str = ""
    flag = False
    for s in string:
        if s == ")":
            if flag:
                final_str = final_str + s
                flag = False
            else:
                pass
        elif s == "(":
            final_str = final_str + s
            flag = True
        else:
            final_str = final_str + s
    final_str = final_str.strip().split(" ")
    final_str = list((value for value in final_str if (value != "")))
    return " ".join(final_str)


def format_json():
    filenames = os.listdir("./outputZip/")
    print("1-------", filenames)
    for file in filenames:
        # Unzipping the output
        with zipfile.ZipFile("./outputZip/" + file, "r") as zip_ref:
            zip_ref.extractall("./outputZip/")
        shutil.move(
            "./outputZip/" + "/structuredData.json",
            "./outputZip/" + file.split(".")[0] + ".json",
        )

        # remove zip file returned by pdf services
        os.remove("./outputZip/" + file)

    filenames = os.listdir("./outputZip/")

    for filename in filenames:
        tempStruct = {}
        metaData = {}
        clauses = {}
        citation_string = ""
        date_string = ""
        citation_end = False
        citation_continue = False
        date_end = False
        end_metadata = False
        case_info_start = False
        case_info = ""
        stack = []
        count_stack = []
        global_count = 1
        change = False

        with open("./outputZip/" + filename, encoding="utf8") as f:
            extractedJSON = json.load(f)
            elements = extractedJSON["elements"]

            for element in elements:
                try:
                    if "Text" in element:

                        if "Lbl" in element["Path"]:
                            if "[" in element["Text"] and "]" in element["Text"]:
                                stack.clear()
                                count_stack.clear()
                                global_count = 1
                            elif remove_unwanted_char(element["Text"]).isdigit():
                                if len(stack) == 0:
                                    stack.append("digit")
                                    global_count = global_count + 1
                                    count_stack.append(1)
                                else:
                                    if (
                                        stack[len(stack) - 1] != "digit"
                                        and "digit" not in stack
                                    ):
                                        stack.append("digit")
                                        l = count_stack[len(count_stack) - 1]
                                        l = l - 1
                                        count_stack[len(count_stack) - 1] = l
                                        count_stack.append(1)
                                        global_count = global_count + 1

                                    elif (
                                        stack[len(stack) - 1] != "digit"
                                        and "digit" in stack
                                    ):
                                        stack.pop()
                                        count_stack.pop()
                                        l = count_stack[len(count_stack) - 1]
                                        l = l + 1
                                        count_stack[len(count_stack) - 1] = l
                                        global_count = global_count - 1

                            elif (
                                remove_unwanted_char(element["Text"]).isalpha()
                                and "i" not in element["Text"]
                                and "v" not in element["Text"]
                                and "x" not in element["Text"]
                            ):
                                if len(stack) == 0:
                                    stack.append("alpha")
                                    global_count = global_count + 1
                                    count_stack.append(1)
                                else:
                                    if (
                                        stack[len(stack) - 1] != "alpha"
                                        and "alpha" not in stack
                                    ):
                                        stack.append("alpha")
                                        l = count_stack[len(count_stack) - 1]
                                        l = l - 1
                                        count_stack[len(count_stack) - 1] = l
                                        count_stack.append(1)
                                        global_count = global_count + 1

                                    elif (
                                        stack[len(stack) - 1] != "alpha"
                                        and "alpha" in stack
                                    ):
                                        stack.pop()
                                        count_stack.pop()
                                        l = count_stack[len(count_stack) - 1]
                                        l = l + 1
                                        count_stack[len(count_stack) - 1] = l
                                        global_count = global_count - 1

                            elif (
                                is_roman_number(element["Text"])
                                and "c" not in element["Text"]
                            ):
                                if len(stack) == 0:
                                    stack.append("roman")
                                    global_count = global_count + 1
                                    count_stack.append(1)
                                else:
                                    if (
                                        stack[len(stack) - 1] != "roman"
                                        and "roman" not in stack
                                    ):
                                        l = count_stack[len(count_stack) - 1]
                                        l = l - 1
                                        count_stack[len(count_stack) - 1] = l
                                        stack.append("roman")
                                        global_count = global_count + 1
                                        count_stack.append(1)

                                    elif (
                                        stack[len(stack) - 1] != "roman"
                                        and "roman" in stack
                                    ):
                                        stack.pop()
                                        count_stack.pop()
                                        l = count_stack[len(count_stack) - 1]
                                        l = l + 1
                                        count_stack[len(count_stack) - 1] = l
                                        global_count = global_count - 1

                            else:
                                print(filename, element["Text"])

                        if "LBody" in element["Path"] and "Lbl" not in element["Path"]:
                            if global_count == 1:
                                clauses[len(clauses)] = {"info": element["Text"]}
                            else:
                                s = ""
                                for ind in count_stack:
                                    s = s + str(ind) + "."
                                e = clauses[len(clauses) - 1]
                                e[s[:-1]] = element["Text"]
                                l = count_stack[len(count_stack) - 1]
                                l = l + 1
                                count_stack[len(count_stack) - 1] = l

                        if case_info_start:
                            case_info = case_info + element["Text"]

                        if (
                            element["Page"] == 0 or element["Page"] == 1
                        ) and case_info_start is True:
                            if (
                                "LBody" in element["Path"] or "Lbl" in element["Path"]
                            ) and element["Text"].strip() == "[1]":
                                metaData["CASE_INFO"] = clean_string(case_info)
                                case_info_start = False
                            if "attributes" in element:
                                if "TextAlign" in element["attributes"]:
                                    if element["attributes"]["TextAlign"] == "Center":
                                        if re.match(
                                            r"\bendorsement\b|\breasons for decision\b|\bruling on application\b|"
                                            r"\bCONSTITUTIONALITY\b|\breasons for judgment\b|COSTS ENDORSEMENT\b|",
                                            element["Text"].strip(),
                                            re.IGNORECASE,
                                        ):
                                            metaData["CASE_INFO"] = clean_string(
                                                case_info
                                            )
                                        # case_info_start = False

                        if re.search(
                            "^RE:.*", element["Text"].strip().replace(" ", "")
                        ) or re.search(
                            "^BETWEEN:.*", element["Text"].strip().replace(" ", "")
                        ):
                            case_info = element["Text"].strip().split(":")[1] + " "
                            case_info_start = True
                            end_metadata = True

                            # Check End of Meta Data
                        if (
                            element["Text"].strip() == "ONTARIO"
                            or "".join(element["Text"].strip().split(" "))
                            == "SUPERIORCOURTOFJUSTICE-ONTARIO"
                            or "".join(element["Text"].strip().split(" "))
                            == "SUPERIORCOURTOFJUSTICEOFONTARIO"
                            or "ONTARIO" in element["Text"].strip()
                        ):
                            metaData["PROVINCE"] = "ONTARIO"
                            case_info_start = True
                            date_end = True
                            end_metadata = True

                            # Extract Court File Number
                        if (
                            re.search("COURT FILE NO", element["Text"], re.IGNORECASE)
                            and not end_metadata
                        ):
                            metaData["CITATION"] = citation_string
                            citation_end = True
                            CFno = element["Text"].split(":")[1].strip().upper()
                            if "COURT_FILE_NO" in metaData:
                                cflist = list([metaData["COURT_FILE_NO"]])
                                cflist.append(CFno)
                                metaData["COURT_FILE_NO"] = cflist
                            else:
                                metaData["COURT_FILE_NO"] = CFno

                            # Extract citation
                        if not citation_end and not end_metadata:
                            if citation_continue:
                                if element["Text"].strip() == ":":
                                    pass
                                else:
                                    citation_string = (
                                        citation_string + element["Text"] + " "
                                    )
                            elif re.search("CITATION", element["Text"], re.IGNORECASE):
                                if (
                                    element["Text"].upper().strip() == "CITATION:"
                                    or element["Text"].upper().strip() == "CITATION"
                                ):
                                    citation_continue = True
                                elif re.search(
                                    "CITATION:", element["Text"], re.IGNORECASE
                                ):
                                    txt = element["Text"]
                                    if "http" in element["Text"]:
                                        ind = element["Text"].find("CITATION")
                                        txt = element["Text"][ind:]
                                    citation_string = txt.split(":")[1].strip().upper()

                            # Extract Date
                        if not date_end and not end_metadata:
                            if re.search("DATE", element["Text"], re.IGNORECASE):
                                # print(element['Text'].split(":")[1].strip())
                                metaData["DATE"] = element["Text"].split(":")[1].strip()
                                date_end = True
                except:
                    print(filename + " Error !!!")

            # Saving formatted JSON files
            if "DATE" not in metaData:
                metaData["DATE"] = ""
            tempStruct["metadata"] = metaData
            tempStruct["clauses"] = clauses
            formatted = json.dumps(tempStruct)
            jsonFile = open("./outputFormatted/" + filename, "w")
            jsonFile.write(formatted)
            jsonFile.close()
            print(filename, " done")
