#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This software is under a BSD license.  See LICENSE.txt for details.

import numpy as np

class DTDictionary(object):
    """Dictionary object.
    
    DataTank dictionaries can only contain scalars, strings,
    arrays of numbers, or other dictionaries as values. Keys
    are always strings. Other than that, usual Python dictionary
    semantics apply for access and iteration.
    
    Supported functions:
    
    * :py:func:`len`
    * :py:func:`for`
    * :py:func:`in`
    
    """
    
    dt_type = ("Dictionary", "DTDictionary")
    
    def __init__(self):
        super(DTDictionary, self).__init__()
        self._storage = dict()
        
    def __iter__(self):
        # unordered iteration
        return self._storage.__iter__()
        
    def __getitem__(self, key):
        # support for dictionary-style getting
        return self._storage[key]
        
    def __contains__(self, item):
        # direct (fast) support for in statement
        return item in self._storage
        
    def __setitem__(self, name, value):
        # support for dictionary-style setting; calls write()
        self._storage[name] = value
    
    def __len__(self):
        return len(self._storage)

    def __str__(self):
        return str(self._storage)
        
    def __repr__(self):
        return repr(self._storage)
        
    def _all_strings(self):
        """strings"""
        svals = dict()
        for x in self._storage:
            if isinstance(self._storage[x], basestring):
                svals[x] = self._storage[x]
        return svals
        
    def _all_numbers(self):
        """scalars"""
        nvals = dict()
        for x in self._storage:
            if isinstance(self._storage[x], (float, int)):
                nvals[x] = self._storage[x]
        return nvals
    
    def _all_arrays(self):
        """numeric arrays"""
        avals = dict()
        for x in self._storage:
            if isinstance(self._storage[x], (tuple, list, np.ndarray)):
                avals[x] = self._storage[x]
                # could assert type of elements, but let DTDataFile handle that
        return avals
        
    def _all_dicts(self):
        """dictionaries"""
        dvals = dict()
        for x in self._storage:
            if isinstance(self._storage[x], dict):
                dvals[x] = self._storage[x]
        return dvals
        
    def __dt_type__(self):
        return DTDictionary.dt_type[0]
        
    def __dt_write__(self, datafile, name):
        all_strings = self._all_strings()
        all_numbers = self._all_numbers()
        all_arrays = self._all_arrays()
        all_dicts = self._all_dicts()
        
        lengths = (len(all_numbers), len(all_strings), len(all_arrays), len(all_dicts))
        datafile.write_anonymous(np.array(lengths).astype(np.int32), name)
        
        def _write_dictionary_of_type(d, type_string):
            for idx, key in enumerate(d):
                datafile.write_anonymous(key, "%s_%s%d_name" % (name, type_string, idx))
                datafile.write_anonymous(d[key], "%s_%s%d_value" % (name, type_string, idx))

        _write_dictionary_of_type(all_numbers, "n")                
        _write_dictionary_of_type(all_strings, "s")
        _write_dictionary_of_type(all_arrays, "a")
        
        # warning: untested
        for idx, dict_key in enumerate(all_dicts):
            # create DTDictionary with each dict, tell it to save
            dt_dict = DTDictionary()
            dt_dict._storage = all_dicts[dict_key]
            datafile.write_anonymous(dict_key, "%s_d%d_name" % (name, idx))
            dt_dict.__dt_write__(datafile, "%s_d%d_value" % (name, idx))
        
    @classmethod
    def from_data_file(self, datafile, name):
        
        (nlen, slen, alen, dlen) = np.squeeze(datafile[name])
        dt_dict = DTDictionary()
        
        for idx in xrange(slen):
            name_key = "%s_s%d_name" % (name, idx)
            value_key = "%s_s%d_value" % (name, idx)
            key = datafile[name_key]
            value = datafile[value_key]
            dt_dict[key] = value

        for idx in xrange(nlen):
            name_key = "%s_n%d_name" % (name, idx)
            value_key = "%s_n%d_value" % (name, idx)
            key = datafile[name_key]
            value = datafile[value_key]
            dt_dict[key] = value

        for idx in xrange(alen):
            name_key = "%s_a%d_name" % (name, idx)
            value_key = "%s_a%d_value" % (name, idx)
            key = datafile[name_key]
            value = datafile[value_key]
            dt_dict[key] = value

        # warning: untested
        for idx in xrange(dlen):
            name_key = "%s_a%d_name" % (name, idx)
            value_key = "%s_a%d_value" % (name, idx)
            key = datafile[name_key]
            value = DTDictionary.from_data_file(datafile, value_key + "_d")
            dt_dict[key] = value
                    
        return dt_dict        

if __name__ == '__main__':
    
    from datatank_py.DTDataFile import DTDataFile
    dt_dict = DTDictionary()
    
    dt_dict["Test_scalar_float"] = 2.573
    dt_dict["Test_scalar_int"] = 5
    dt_dict["Test_string"] = "This is only a test"
    dt_dict["Test_array"] = (1.1, 2, 5, 7.5, 11.978)
    
    with DTDataFile("/tmp/dict_test.dtbin", truncate=True) as dtf:
        #dt_dict.__dt_write__(dtf, "dictionary test")
        dtf["dictionary test"] = dt_dict
    
    with DTDataFile("/tmp/dict_test.dtbin") as dtf:
        for k in dtf:
            print k, dtf[k]
            
        dt_dict = DTDictionary.from_data_file(dtf, "dictionary test")
        for k in dt_dict:
            print "%s = %s" % (k, dt_dict[k])
            
        print dt_dict
    
    