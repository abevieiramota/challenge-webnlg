#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 11 08:50:00 2018

@author: abevieiramota
"""

import os
import sys
from itertools import zip_longest
import logging

logger = logging.Logger("Test")


def get_only_files(dir):
    
    return (file for file in os.listdir(dir) 
            if os.path.isfile(os.path.join(dir, file)))


def compare_files(filepath1, filepath2):
    
    differences = []
    
    with open(filepath1) as f1, open(filepath2) as f2:
        
        for l1, l2 in zip_longest(f1, f2):
            
            if l1 is None:
                
                logger.warn('File %s has fewer lines than file %s', filepath1, 
                            filepath2)
            
            if l2 is None:
                
                logger.warn('File %s has fewer lines than file %s', filepath2, 
                            filepath1)
                
            if l1 != l2:
                
                differences.append((l1, l2))
                
    return differences
            


if __name__ == '__main__':
    
    logger.setLevel(logging.WARN)  
    # folder paths to compare
    dir1 = sys.argv[1]
    dir2 = sys.argv[2]
    
    dir1_files = get_only_files(dir1)
    dir2_files = get_only_files(dir2)
    
    # tests if they have the same files
    if set(dir1_files) ^ set(dir2_files):
        
        logger.warn("The folders have different sizes.\n%s number of files %d\n%s number of files %d", 
                    dir1, len(dir1_files),
                    dir2, len(dir2_files))
        
        print(set(dir1_files) ^ set(dir2_files))
        sys.exit()
    
    for filename in dir1_files:
        
        filepath1 = os.path.join(dir1, filename)
        filepath2 = os.path.join(dir2, filename)
        
        differences = compare_files(filepath1, filepath2)
        
        if differences:
            
            logger.warn("There are %d differences between files:\n %s \n %s",
                        len(differences), filepath1, filepath2)
