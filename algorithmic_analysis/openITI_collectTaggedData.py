import re, sys, textwrap
from fuzzywuzzy import fuzz

splitter = "#META#Header#End#"
lenSymb  = 68

from datetime import datetime
startTime = datetime.now()

def wrapPar(paragraph, lenSymb):
    if "%~%" in paragraph:
        wrapped = paragraph
    else:
        wrapped = "\n~~".join(textwrap.wrap(paragraph, lenSymb))
    return(wrapped)

def updateDic(dic, item):
    if item in dic:
        dic[item] += 1
    else:
        dic[item]  = 1

tags = ["P", "S", "T"]

def mainFunction(inputFile):
    with open(inputFile, "r", encoding="utf8") as f1:
        text = f1.read().split(splitter)

        header = text[0]
        main = text[1].strip()

        mainNormalized = main
        mainNormalized = re.sub("\n~~", " ", mainNormalized)
        mainNormalized = re.sub(" +", " ", mainNormalized)

        results = []

        for i in range(1, 10):
            print("@[%s]\d%s%s\\b" % ("".join(tags), i, " \w+"*i))
            res = re.findall(r"@[PST]\d%s%s\b" % (i, " \w+"*i), mainNormalized)
            print(len(res))
            results.extend(res)
            print("\t%d" % len(results))

        # collect onomastic
        sections = mainNormalized.split("\n#")
        onomastic = []
        for i in range(0, len(sections)):
            if "~:onomastic:" in sections[i]:
                new = "@P00 " + sections[i+1]
                results.append(new)

        dic = {}

        # processing results
        for r in results:
            t = r[:2]
            cutter = int(r[2])
            cleanItem = r[5+cutter:]

            dicItem = t + " " + cleanItem

            if dicItem in dic:
                dic[dicItem] += 1
            else:
                dic[dicItem]  = 1

            #print(t)
            #print(cutter)
            #print(cleanItem)
            #print(dicItem)
            #input(r)

        # process results
        # process only "@P"

        key = "@P"
        counter = 0
        res_New = []
        dicNew = {}
        for k,v in dic.items():
            if k.startswith(key):
                counter += 1
                PID = "@PID%09d" % counter
                PID_New = "@PID000000001"
                PID_New = "@PIDXXXXXXXXX"
                val = "%09d\t%s\t%s\t%s\t%s" % (v, PID, PID_New, k[3:], "@P\d\d \w*" + k[3:].replace(" ", "[ ~\\n]+"))
                res_New.append(val)

                dicNew[k] = val.split("\t")

                # add TAG - does not seem to work...
                # if re.search(r"\b(@P\d\d \w+?%s)\b" % k[3:], mainNormalized):
                #     print("\t%s" % "\b(@P\d\d \w+?%s)\b" % k[3:])
                #     mainNormalized = re.sub(r"\b(@P\d\d \w+?%s)\b" % k[3:], r"\1 " + PID, mainNormalized)

        head = "\t".join(["FREQ", "ID", "CORRECTED_ID", "NAME_AS_IN_TEXT", "REGULAR_EXPRESSION"])
        res_save = head + "\n" + "\n".join(sorted(res_New, reverse=True))
        with open(inputFile+".pEntities.csv", "w", encoding="utf8") as f9:
            f9.write(res_save)

        # generate fuzzymatches
        pr = 0
        matches = []
        for k,v in dicNew.items():
            if pr % 100 == 0:
                print("\t%d" % pr)
            pr += 1

            #print("="*80)
            item1 = k[3:].strip()
            descr = "\t%s\t%s\t%s" % (v[0], v[1], v[3])
            #print(item1)
            #print("="*80)
            VAR = "="*80 +"\n"+ item1+descr+"\n"+ "="*80 +"\n"
            MAT = []
            for k,v in dicNew.items():
                if k[3:].strip() != item1:
                    #count score
                    item2 = v[-2].strip()
                    # fuzz.ratio
                    score = fuzz.ratio(item1, item2)
                    if score >= 80:
                        M = "\t%d\tfuzz.ratio\t" % score + "%s\t%s\t%s" % (v[0], v[1], v[3])
                        MAT.append(M)
                    # fuzz.partial_ratio
                    score = fuzz.partial_ratio(item1, item2)
                    if score >= 80:
                        M = "\t%d\tfuzz.partial_ratio\t" % score + "%s\t%s\t%s" % (v[0], v[1], v[3])
                        MAT.append(M)
                    # fuzz.token_sort_ratio
                    score = fuzz.token_sort_ratio(item1, item2)
                    if score >= 80:
                        M = "\t%d\tfuzz.token_sort_ratio\t" % score + "%s\t%s\t%s" % (v[0], v[1], v[3])
                        MAT.append(M)
                    # fuzz.token_set_ratio
                    score = fuzz.token_set_ratio(item1, item2)
                    if score >= 80:
                        M = "\t%d\tfuzz.token_set_ratio\t" % score + "%s\t%s\t%s" % (v[0], v[1], v[3])
                        MAT.append(M)
            VAR += "\n".join(MAT)
            if VAR.endswith("=\n"):
                pass
            else:
                #input(VAR)
                matches.append(VAR)
            #input()   

        with open(inputFile+".pFuzzyMatches.txt", "w", encoding="utf8") as f9:
            f9.write("\n\n".join(matches))         


        # reflow doc
        mainNew = []
        toProc  = mainNormalized.split("\n#")

        for t in toProc:
            tNew = "#" + wrapPar(t, lenSymb)
            mainNew.append(tNew)


        # # reassemble text
        # main  = "\n".join(mainNew)
        # final = header + splitter + "\n\n" + main
        # with open(inputFile+".TAGGED", "w", encoding="utf8") as f9:
        #     f9.write(final)


#pathToFile = "../data/0812CaliKhazraji/0812CaliKhazraji.CuqudLuluiyya/0812CaliKhazraji.CuqudLuluiyya.Mahoney20180308-ara1.mARkdown"
#mainFunction(pathToFile)


#reflowMdSimple(inputFile)

# # The following function checks if a file gets messed up or not: test is passed!
# def compare(file):
#     with open(file, "r", encoding="utf8") as f1:
#         text1 = f1.read()
#         text1 = re.sub("###(\$\d+\$#)?", "", text1)
#         text1 = re.sub("###", "", text1)
#         text1 = re.sub("\s+", "", text1)

#     with open(file+"_TEST", "r", encoding="utf8") as f2:
#         text2 = f2.read()
#         text2 = re.sub("###(\$\d+\$#)?", "", text2)
#         text2 = re.sub("\s+", "", text2)

#     if text1 == text2:
#         print("Text1 == Text2")
#     else:
#         print("Text1 != Text2")

# compare(inputFile)

def main():
    if len(sys.argv) == 2:
        mainFunction(sys.argv[1])
    else:
        print("Wrong command! It should be:")
        print("\tpython3 script.py path_to_file")

main()


print("===>" + str(datetime.now() - startTime))
print("Done!")
