import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple, Literal, Callable



def cleancolumnnames(names : List[str]) -> List[str]:
    """
    Returns a list of cleaned names; removes spaces and weird characters from the names,
    replacing with underscores.
    """
    names = names.copy()

    names = list(map(lambda x: x.lower(), names))

    for char in [' ', '-', '\\', '/', '.', ',']:
        names = list(map(
            lambda x: '_'.join(x.split(char)),
            names
        ))

    return names


def filterif(frame : pd.DataFrame, conditional : Callable[[any], bool], columns : List[str] = None) -> pd.DataFrame:
    """
    loops over the entire table and removes any ROW that satisfies the conditional being applied on each individual cell value
    conditional has to be a lambda expression/function that returns True or False; returns a new frame with the changes
    """
    frame = frame.copy()
    if columns is None: columns = frame.columns

    n = 0

    for x in frame.index:
        for y in frame.columns:
            if conditional(frame.at[x, y]):
                frame.drop(x, axis = 0, inplace = True)
                n += 1
    
    print(f"Dropped {n} total rows that satisfied the conditional")
    
    return frame


def dropnulls(frame : pd.DataFrame, columns : List[str] = None) -> Tuple[pd.DataFrame, int]:
    """
    Drops all rows that contain a `null` or `NaN` value in any of the given column names.
    Returns a new frame.
    """
    frame = frame.copy()
    
    if columns is None: columns = frame.columns

    n = 0

    for col in columns:
        for x in frame.index:
            try:
                if pd.isna(frame.at[x, col]):
                    n += 1
                    frame.drop(x, axis = 0, inplace=True)
            except TypeError : pass
    
    print(f"Dropped {n} total rows with nulls from {columns}")

    return frame, n



def assigntypes(frame : pd.DataFrame, columns : List[str] = None) -> pd.DataFrame:

    """
    Assigns `ordinal/nominal`, `discrete` and `continuous` to the given columns in a given dataframe.
    """

    if columns is None : columns = frame.columns

    types = []

    for each in columns:
        if pd.api.types.is_numeric_dtype(frame[each].dtype):
            if pd.api.types.is_integer_dtype(frame[each].dtype):
                types.append('discrete')
            else:
                types.append('continuous')
        else:
            types.append('ordinal/nominal')
    
    types = pd.DataFrame([types, [len(frame[each].unique()) for each in columns], frame.dtypes[columns]], columns = columns, index = ['fieldtype', 'uniquevalues', 'datatype'])

    return types



def fillmissing(frame : pd.DataFrame, value : Dict[str, Any] | Any, columns : List[str] = None) -> Tuple[pd.DataFrame, int, int]:
    """
    Fills missing values in the dataframe (`nan` and `null` values) with the given value.
    value can be a single value, or a dictionary with columns as keys and values as the value to be filled.
    Returns a new frame, the no. of successful fills, the number of fails due to type error.
    """
    frame = frame.copy()

    #setting the proper value for columns
    if columns is None: columns = frame.columns
    
    succ, fail = 0, 0
    #loop over columns
    for i in columns:

        #if value is a dictionary, get the appropriate value from it, else the value itself is the default value
        try: val = value if type(value) != dict else value[i]
        except KeyError:
            print(f"No default value provided for column `{i}`, skipping...")
            continue
        
        #for every entry...
        for each in frame.index:
            try:
                #...check if it is NaN, if it is, place the default val here.
                if np.isnan(frame.at[each, i]):
                    frame.at[each, i] = val
                    succ += 1
            except TypeError:
                fail += 1
    return frame, succ, fail



def reducenoise(frame : pd.DataFrame, tolerances : Dict[str, int | float] = None, columns : List[str] = None) -> pd.DataFrame:
    """
    Drops any row of the frame where the value's distance from the mean is more than the given tolerance.
    If tolerance is not provided for a column, standard deivation value of that column is used.
    Works only on numeric valued columns.
    Returns a new frame.
    """
    frame = frame.copy()

    if columns is None: columns = frame.columns

    print(f"Removing noise from {columns}")

    for c in columns:
        if not pd.api.types.is_numeric_dtype(frame[c].dtype): continue
        m = frame[c].mean()
        t = tolerances[c] if tolerances is not None else frame[c].std()
        for r in frame.index:
            if abs(frame.at[r, c] - m) > t : frame.drop(index = r, axis = 0, inplace = True)
    
    return frame


def categorise(frame : pd.DataFrame, columns : List[str] = None) -> Tuple[pd.DataFrame, Dict[str, Dict[int, str]]]:
    """
    Encodes the values of a column into integers. Returns a new dataframe.
    """
    categorised = dict()

    #this stores the categorisation information of each of the columns
    mappings = []
    
    #if columns is not specified, take all the columns that are of dtype 'object'
    if columns is None: columns = list(filter(lambda x: frame[x].dtype == 'object', frame.columns))    

    print(f"Categorising columns : {columns}")

    #for each column...
    for column in columns:
        #...this stores the actual vertical frame that will be inserted into the dataframe later...
        framecolumn = []

        #...this contains all the different instances of the values in the column...
        categories = dict()

        #... and this is the actual numeric value assigned to each new instance...
        i = 1

        label = 'category_' + str(column)

        #this block basically checks if this instance's value has already been encountered before.
        #if it has, then simply append that value to the framecolumn, else assign it a new number and move on.
        for value in frame.loc[:, column]:
            try: framecolumn.append(categories[value])
            except KeyError:
                categories[value] = i
                framecolumn.append(i)
                i += 1
        
        #insert column into the dataframe
        categorised[label] = framecolumn
        mappings.append(categories)

    # print(f"mappings:{mappings}")

    #re-orienting the mapping so that key value pairs are (category_num : category_name)
    maps = dict()

    for each in range(len(columns)):
        mapping = dict()
        for key in mappings[each]:
            mapping[mappings[each][key]] = key
        maps[str(columns[each])] = mapping

    categorised = pd.DataFrame(data = categorised)

    return (categorised, maps)

def norm(column : pd.DataFrame) -> float:
    """
    Returns the norm of the given column
    """
    nor = 0
    for i in column.index:
        nor += pow(column[i], 2)
    return pow(nor, 0.5)


def normalise(frame : pd.DataFrame, columns : list = None, measure : Literal['zfact', 'max', 'mean', 'mode', 'l1', 'l2'] = 'zfact') -> pd.DataFrame:
    """
    Normalises the given columns of the dataframe.
    Returns a new frame.
    Measure defines the method to normalise using.
    """
    frame = frame.copy()

    if columns is None: columns = frame.columns
    
    for column in columns:
        val = (frame.loc[:, column])
        
        if measure == 'max': val = val.max()
        elif measure == 'mean': val = val.mean()
        elif measure == 'median': val = val.median()
        elif measure == 'mode': val = val.mode()
        elif measure == 'l1': val = norm(val)
        elif measure == 'l2' :
            for each in frame.index:
                frame.loc[each, :] /= norm(frame.loc[each, :])
            return frame
        elif measure == 'zfact':
            frame[column] -= frame[column].mean()
            val = frame[column].std()
        else:
            print('Invalid measure type')
            return
        
        frame.loc[:, column] /= val
    
    return frame



def splitframe(frame : pd.DataFrame, ratio : List[int], target : List[str] = None, shuffle : bool = True) -> List[pd.DataFrame | Tuple[pd.DataFrame, pd.DataFrame]]:

    """
    this function divides a pandas dataframe into sets according to the ratio provided
    ratio is a list of integers denoting the ratio in which to split the dataframe
    example: 1:2 ratio would be [1, 2], 3:2:1 ratio would be [3, 2, 1]

    Target is a list of columns that are the target features;
    if targets are provided, the returned list has [(p1x, p1y), (p2x, p2y), ...] format
    """

    frame = frame.copy()

    if shuffle: frame = frame.sample(frac = 1)

    x = (len(frame)/sum(ratio))

    ratio = list(map(lambda r: int(r * x), ratio))

    for each in range(1, len(ratio)):
        ratio[each] += ratio[each - 1]

    partitions = [frame.iloc[:ratio[0]]]

    for r in range(1, len(ratio) - 1):
        partitions.append(frame.iloc[ratio[r-1]:ratio[r], :])
    
    partitions.append(frame.iloc[ratio[-2]:, :])

    if target is not None:
        partitions = list(map(
                            lambda x: (
                                x.loc[:, list(map(lambda y: y not in target, frame.columns))],
                                x.loc[:, target]),
                            partitions
                        ))

    return partitions

def shuffleframe(frame : pd.DataFrame):
    """
    shuffles the frame (meant for reordering a dataset)
    """
    frame = frame.copy().sample(frac = 1)
    return frame