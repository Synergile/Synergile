# -*- coding: utf-8 -*-

'''MIT License

Copyright (c) 2020 Walker Gray

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

from io import StringIO

class StringBuilder:
    '''Provides efficient and performant concatenation of strings
    The inspiriation for this class comes from the comparision of string concatenation methods found at https://waymoot.org/home/python_string/
    This class serves as an encapsulation of 'method 5', in order to optimize both performance and memory usage
    '''
    
    def __init__(self, initial_str=None):
        '''Construct a new StringBuilder. An initial value may optionally be provided'''
        self.file_str = StringIO()
        if initial_str is not None:
            self.file_str.write(str(initial_str))
            
    def __str__(self)-> str:
        '''Returns a string representation of the data. Causes StrngBuilder to stringify when used in string contexts like str()'''
        return self.file_str.getvalue()
            
        
    @classmethod
    def from_list(cls, data: list):
        '''
        Returns a new StringBuilder using the provided list of initial values. Values are concatenated together in order.
        Accepts any values that str() can be called on.
        '''
        self = cls.__new__(cls)
        self.file_str = StringIO()
        for str in data:
            self.file_str.write(str(str))
        return self
    
    def append(self, data):
        '''Appends data to the StringBuilder. Accepts any value that str() can be called on. Returns self to enable successive chaining'''
        self.file_str.write(str(data))
        return self

    def to_string(self)-> str:
        '''Returns a string representation of the data'''
        return self.file_str.getvalue()
        
    def len(self)-> int:
        '''Returns the length of the string currently'''
        return len(self.file_str.getvalue())
