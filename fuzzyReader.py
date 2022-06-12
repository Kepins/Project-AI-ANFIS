import simpful as sf
import re
import itertools


class GeneralizedBell_MF(sf.MF_object):

    def __init__(self, a, b, c):
        super().__init__()
        self._a = a
        self._b = b
        self._c = c

    def _execute(self, x):
        return 1 / (1 + pow(abs(((x - self._c) / self._a)), 2 * self._b))


class InputOutputVar():
    name: str
    numOfMfs = 0
    mfs: []
    names: []

    def __init__(self, lines, startIndex, function_type, mode="input"):
        line: str
        self.range = []
        self.mfs = []
        self.names = []
        for idx, line in enumerate(lines):
            if idx == startIndex + 1:
                start = line.find('\'')
                name = line[start + 1:]
                name = name[:len(name) - 2]
                self.name = name
            elif idx == startIndex + 2:
                start = line.find('[')
                range = line[start + 1:]
                range = range[:len(range) - 2]
                for item in range.split():
                    self.range.append(float(item))
            elif idx == startIndex + 3:
                start = line.find('=')
                num = line[start + 1:]
                num = num[:len(num) - 1]
                self.numOfMfs = int(num)
            elif startIndex + 4 <= idx < startIndex + 4 + self.numOfMfs:
                a = line.find("\'")
                b = line.find(":")
                term = line[a + 1:b - 1]
                self.names.append(term)
                start = line.find('[')
                inputRangeStr = line[start + 1:]
                inputRangeStr = inputRangeStr[:len(inputRangeStr) - 2]
                inputRange = []
                for item in inputRangeStr.split():
                    inputRange.append(float(item))
                if mode=="input":
                    if function_type=="gaussbell":
                        self.mfs.append(
                            sf.FuzzySet(function=sf.Gaussian_MF(inputRange[1], inputRange[0]), term=term))
                    elif function_type=="generalizedbell":
                        self.mfs.append(
                            sf.FuzzySet(function=GeneralizedBell_MF(inputRange[0], inputRange[1],
                                                                    inputRange[2]), term=term))
                    print("Term: "+term+" "+str(inputRange[1])+" "+str(inputRange[0]))
                elif mode=="output":
                    self.mfs.append([term,inputRange])


class FuzzyReader():

    def __init__(self, path, function_type):
        self.path = path
        self.function_type = function_type
        if function_type != "generalizedbell" and function_type != "gaussbell":
            raise NotImplementedError

    def read(self):
        fs = sf.FuzzySystem(show_banner=False)
        file = open(self.path, 'r')
        lines = file.readlines()
        inputVars = []

        for idx, line in enumerate(lines):
            if re.search("^\[Input[1-9]+]{1}", line) != None:
                inputVars.append(InputOutputVar(lines, idx, self.function_type))
            elif re.search("^\[Output[1-9]+]{1}", line) != None:
                outputVar = InputOutputVar(lines, idx, self.function_type, mode="output")

        for item in inputVars:
            fs.add_linguistic_variable(item.name, sf.LinguisticVariable(item.mfs,
                                                                        universe_of_discourse=[item.range[0],
                                                                                               item.range[1]]))

        for idx, item in enumerate(outputVar.mfs):
            func = ""
            for idx2, item2 in enumerate(item[1]):
                if idx2 < len(inputVars):
                    func += str(item2) + "*" + inputVars[idx2].name + "+"
                else:
                    func += str(item[1][idx2])
            print(item[0])
            print(func)
            fs.set_output_function(item[0], func)

        rules = []

        l = [_ for _ in range(len(inputVars[0].mfs))]

        k = 0
        for i in itertools.product(l, repeat=len(inputVars)):
            z = 0
            rule = ""
            for j in range(0, len(inputVars)):
                if j == 0:
                    rule += "IF (" + inputVars[j].name + " IS " + inputVars[j].names[i[z]] + ")"
                else:
                    rule += " AND (" + inputVars[j].name + " IS " + inputVars[j].names[i[z]] + ")"
                z += 1
            rule += " THEN (Power IS " + outputVar.names[k] + ")"
            print(rule)
            k += 1
            rules.append(rule)

        fs.add_rules(rules)
        return fs