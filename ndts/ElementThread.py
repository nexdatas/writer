#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012 Jan Kotanski
#
#    Foobar is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Foobar is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
## \package ndts nexdatas
## \file ElementThread.py
# ElementThread

from threading import *                                                                       

## Single Thread Element
class ElementThread(Thread):
    ## constructor
    # \brief It creates ElementThread from the runnable element
    def __init__(self,elem):
        Thread.__init__(self)
        ## runnable element
        self.elem=elem

    ## runner
    # \brief It runs the defined thread
    def run(self):
        if hasattr(self.elem,"run"):
            self.elem.run()

