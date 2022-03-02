# recursivesearch

Identify the path to a certain entry in nested objects. This script was created to determine the location of certain items in objects created by the Bio.Entrez module, but can be used with other nested objects. It creates a dictionary of the positions of any hashable item found in the object supplied as argument. Data can be retrieved visually (as string), as path (a list of lists of indices and keys), and more importantly the direct parent object that contains an item can be retrieved.
