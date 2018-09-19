#!/usr/bin/env python

'''
Identify the path to a certain entry in nested objects.
This script was created to determine the location of certain items in objects
created by the Bio.Entrez module, but can be used with other nested objects.
It creates a dictionary of the positions of any hashable item found in the object
supplied as argument.
Data can be retrieved visually (as string), as path (a list of lists of indices and
keys), and more importantly the direct parent object that contains an item 
can be retrieved.

Usage:
retr = Retriever(nested_object)

Example:
 # a nested list we want to search:
>>> my_data = ["foo", 2, [3, {"bar":4}], set([5, 6])]

 # Creating a Retriever object
>>> retr = Retriever(my_data)

 # retr.get_parent(item) will return the parent object containing an item:
>>> retr.get_parent("bar")
{'bar': 4}
>>> retr.get_parent(5)
{5, 6}

 # retr.prettyfind(item) will return, AS STRING, the path to an item (only useful visually)
>>> print(retr.prettyfind(4))
[2][1]["bar"]
 # so now we know that:
>>> my_data[2][1]["bar"]
4

 # finally, retr._track(item) will return a list of lists of indices and keys,
BUT it will also include, at the end, the bool True if "item" is a list item or
a dict value, and False if the item is a dict key or a set item. This is necessary
to retrieve the correct parent. _track is mostly meant to be used by the other
class methods, but it could have interesting applications.


>>> print(retr._track("foo"))
[[0, True]]
 #"True" relates to "foo" being a list item
>>> print(retr._track(4))
[[2, 1, 'bar', True]]
 #"True" relates to 4 being a dictionary value
>>> print(retr._track(5))
[[3, False]]
#"False" relates to 5 being a set item
>>> print(retr._track("bar"))
[[2, 1, False]]
#"False" relates to "bar" being a dictionary key


@author: Roberto Rosati
'''

class Retriever(object):
    '''Identify the path to a certain entry in nested objects.
    It creates a dictionary of the positions of any hashable item found in the object
    supplied as argument.
    Data can be retrieved visually (as string), as path (a list of lists of indices and
    keys), and more importantly the direct parent object that contains an item 
    can be retrieved.
    
    Basic usage:
    retr = Retriever(nested_object)
    retr.get_parent(item)
    
    '''

    def __init__(self, original_data):
        # The original data is still part of the Retriever object
        self.original_data = original_data
        # Populating the item dictionary, {item: [paths]}
        self.itemsdict = dict()
        self.__recursive__(original_data)
        

    def __recursive__(self, iterable, oldcall=False):
        '''Iterate over all the nested objects within the main object, and save
        in a dictionary, as a list, the path to every elemental item (key).
        The last item in the list is a bool: True if the key is a list
        item or a dictionary value, and False if the key is a set item
        or a dictionary key.
        
        '''
        if not oldcall:
            call = []
        else:
            call = list(oldcall)
        # If the current iterable is a list, then iterate over the indices
        if isinstance(iterable, list) or isinstance(iterable, tuple):
            for i in range(len(iterable)):
                self.__recursive__(iterable[i], call+[i])
        # If it's a set, add all its items to the main dict, with paths
        elif isinstance(iterable, set):
            for item in iterable:
                self.itemsdict[item] = self.itemsdict.get(item, [])+[call + [False]]
        # If it's a dict, add all its keys to the main dict, with paths, and iterate over the values
        elif isinstance(iterable, dict):
            for key in iterable.keys():
                self.itemsdict[key] = self.itemsdict.get(key, [])+[call + [False]]
                self.__recursive__(iterable[key], call+[key])
                # tuples or frozensets can be keys too
                if isinstance(key, tuple) or isinstance(key, frozenset):
                    self.__recursive__(key, call)
                    
                
        else:
            # At this point we should only have numbers and strings; add to the main dict
            try:
                self.itemsdict[iterable] = self.itemsdict.get(iterable, [])+[call + [True]]
            # But in any case,
            except:
                print("Unhashable, uncatalogued type: ", type(self.itemsdict[iterable]))
    

    def _track(self, item):
        '''Return the list of paths associated with a key item.
        Return [None] (literally a list containing one element, None) if the
        element is not present.

        '''
        return self.itemsdict.get(item, None)
    

    def get_parent(self, data, pathno=0):
        '''Return the parent object that contains the data.
        If multiple paths to the same object exist, by default return the first one
        (specify "itemno" to override).
        Return None if no path iss found or if the path number is out of range.
        
        '''
        routes = self._track(data)
        if routes and len(routes) > pathno:
            # Remove the appropriate number of items, depending on the final bool;
            # for dict keys and set items, we need to iterate one less time.
            if routes[pathno][-1]:
                route = routes[pathno][:-2]
            else:
                route = routes[pathno][:-1]
            parent = self.original_data
            for element in route:
                parent = parent[element]
            return parent
        else:
            return None
        
            
    def prettyfind(self, data):
        '''Return a string containing the exact text to type to obtain the data
        from the original nested iterable (or from self.original_data).
        
        '''
        routes = self._track(data)
        if routes:
            retstring = ""
            for element in self._track(data):
                retstring += '['+']['.join(['"'+i+'"' if type(i) == str else str(i) for i in element[:-1]])+']\n'
            return retstring
        else:
            return None


